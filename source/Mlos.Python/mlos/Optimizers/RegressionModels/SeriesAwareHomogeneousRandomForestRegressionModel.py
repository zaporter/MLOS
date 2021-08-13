#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#
import math
import random

import pandas as pd
import numpy as np

from mlos.Optimizers.OptimizationProblem import SeriesObjective
from mlos.Optimizers.RegressionModels.HomogeneousRandomForestRegressionModel import HomogeneousRandomForestRegressionModel
from mlos.Spaces import Dimension, Hypergrid, Point, SimpleHypergrid
from mlos.Spaces.HypergridAdapters import HierarchicalToFlatHypergridAdapter
from mlos.Tracer import trace
from mlos.Logger import create_logger
from mlos.Optimizers.RegressionModels.Prediction import Prediction
from mlos.Optimizers.RegressionModels.DecisionTreeRegressionModel import DecisionTreeRegressionModel
from mlos.Optimizers.RegressionModels.HomogeneousRandomForestConfigStore import homogeneous_random_forest_config_store
from mlos.Optimizers.RegressionModels.HomogeneousRandomForestFitState import HomogeneousRandomForestFitState
from mlos.Optimizers.RegressionModels.RegressionModel import RegressionModel


class SeriesAwareHomogeneousRandomForestRegressionModel(HomogeneousRandomForestRegressionModel):
    """TODO ZACK COMMENT
    """


    @trace()
    def __init__(
            self,
            model_config: Point,
            input_space: Hypergrid,
            output_space: Hypergrid,
            objective: SeriesObjective,
            logger=None
    ):
        if logger is None:
            logger = create_logger("SeriesAwareHomogeneousRandomForestRegressionModel")
        self.logger = logger

        assert model_config in homogeneous_random_forest_config_store.parameter_space

        self.objective = objective

        print("ZACK KAPPA")
        # If this is a series objective, create a fake set of forests
        #
        input_space_shallow_copy = SimpleHypergrid(
            name=input_space.name,
            dimensions=input_space.dimensions
        )
        series_modulation_dimension_copy = self.objective.series_modulation_dimension.copy()
        series_modulation_dimension_copy.name = f"context_space.{series_modulation_dimension_copy.name}"
        input_space_shallow_copy.add_dimension(series_modulation_dimension_copy)

        output_space_shallow_copy = SimpleHypergrid(
            name=output_space.name,
            dimensions=[self.objective.series_output_dimension]
        )

        HomogeneousRandomForestRegressionModel.__init__(
            self,
            model_config=model_config,
            input_space=input_space_shallow_copy,
            output_space=output_space_shallow_copy,
            logger=self.logger
        )
        print("CREATED RANDOM FOREST")
        print(self.input_space)
        print(self.output_space)

    @trace()
    def fit(self, feature_values_pandas_frame, target_values_pandas_frame, iteration_number):
        print("FITTING RANDOM FOREST")
        modulated_column_name = f"context_space.time"
        output_column_name = f"f_output"
        lens_of_lists = feature_values_pandas_frame[modulated_column_name].apply(len)
        origin_rows = range(feature_values_pandas_frame.shape[0])
        destination_rows = np.repeat(origin_rows, lens_of_lists)
        non_list_cols = (
            [idx for idx, col in enumerate(feature_values_pandas_frame.columns)
             if col != modulated_column_name]
        )
        expanded_feature_values_df = feature_values_pandas_frame.iloc[destination_rows, non_list_cols].copy()
        expanded_feature_values_df[modulated_column_name] = (
            [item for items in feature_values_pandas_frame[modulated_column_name] for item in items]
        )
        expanded_feature_values_df.reset_index(inplace=True, drop=True)
        expanded_target_values_df = pd.DataFrame({output_column_name: [item for items in target_values_pandas_frame[output_column_name] for item in items]})
        print("INPUT")
        print(expanded_feature_values_df)
        print("TARGET VALUES")
        print(expanded_target_values_df)

        HomogeneousRandomForestRegressionModel.fit(self, expanded_feature_values_df, expanded_target_values_df, iteration_number)

    @trace()
    def predict(self, feature_values_pandas_frame, include_only_valid_rows=True):
        """ Aggregate predictions from all estimators

        see: https://arxiv.org/pdf/1211.0906.pdf
        section: 4.3.2 for details

        :param feature_values_pandas_frame:
        :return: Prediction
"""

        self.logger.debug(f"Predicting {len(feature_values_pandas_frame.index)} points.")

        is_valid_input_col = Prediction.LegalColumnNames.IS_VALID_INPUT.value
        predicted_value_col = Prediction.LegalColumnNames.PREDICTED_VALUE.value
        predicted_value_var_col = Prediction.LegalColumnNames.PREDICTED_VALUE_VARIANCE.value
        sample_var_col = Prediction.LegalColumnNames.SAMPLE_VARIANCE.value
        sample_size_col = Prediction.LegalColumnNames.SAMPLE_SIZE.value
        dof_col = Prediction.LegalColumnNames.PREDICTED_VALUE_DEGREES_OF_FREEDOM.value

        series_vals_df = pd.DataFrame({
            f"context_space.{self.objective.series_modulation_dimension.name}": self.objective.series_modulation_dimension.linspace()
        })
        feature_values_pandas_frame_merged = feature_values_pandas_frame.merge(series_vals_df, how="cross")
        print("INPUT")
        print(feature_values_pandas_frame_merged)

        raw_predictions = HomogeneousRandomForestRegressionModel.predict(self, feature_values_pandas_frame=feature_values_pandas_frame_merged)

        print(raw_predictions)
        predictions_df = raw_predictions.get_dataframe()
        print("OUTPUT")
        print(predictions_df)

        # TODO ZACK: After fighting DataFrames for a few hours I have given up. Maybe I should spend a weekend truly learning them.
        series_error_values = []
        variances = []
        sample_sizes = []
        dofs = []
        sample_variances = []
        current_predictions = []
        for index, prediction in predictions_df.iterrows():
            current_predictions.append(prediction)
            if ((index + 1) % len(self.objective.series_modulation_dimension)) == 0:
                current_expected = np.array([prediction[predicted_value_col] for prediction in current_predictions])
                current_variance = np.array([prediction[predicted_value_var_col] for prediction in current_predictions])
                current_sample_size = np.min([prediction[sample_size_col] for prediction in current_predictions])
                current_dof = np.min([prediction[dof_col] for prediction in current_predictions])
                current_expected_minus_target = current_expected - self.objective.target_series
                calculated_utility_expectation = sum(current_expected_minus_target ** 2 + current_variance)
                calculated_utility_variance = \
                    sum(current_expected_minus_target ** 4 + 6 * (current_expected_minus_target ** 2) * current_variance
                        + 3 * current_variance ** 2 - (current_expected_minus_target ** 2 + current_variance) ** 2)
                series_error_values.append(calculated_utility_expectation)
                variances.append(calculated_utility_variance)
                sample_sizes.append(current_sample_size)
                dofs.append(current_dof)
                sample_variances.append(np.std(current_expected)**2)
                current_predictions = []

        predictions_df = pd.DataFrame({
            predicted_value_col: series_error_values,
            predicted_value_var_col: variances,
            sample_size_col: sample_sizes,
            sample_var_col: sample_variances,
            dof_col: dofs,
            is_valid_input_col: [True for x in series_error_values]
        })

        aggregate_predictions = Prediction(
            objective_name=self.target_dimension_names[0],
            predictor_outputs=self._PREDICTOR_OUTPUT_COLUMNS,
            allow_extra_columns=True
        )

        aggregate_predictions_df = predictions_df[[column.value for column in self._PREDICTOR_OUTPUT_COLUMNS]]
        aggregate_predictions.set_dataframe(aggregate_predictions_df)
        return aggregate_predictions
