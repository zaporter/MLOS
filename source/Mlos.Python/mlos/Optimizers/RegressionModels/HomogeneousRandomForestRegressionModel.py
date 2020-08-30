#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#
import math
import random

import pandas as pd

from mlos.Spaces import Dimension, Hypergrid, SimpleHypergrid, ContinuousDimension, DiscreteDimension, CategoricalDimension, Point
from mlos.Spaces.HypergridAdapters import CompositeToSimpleHypergridAdapter
from mlos.Tracer import trace
from mlos.Logger import create_logger
from mlos.Optimizers.RegressionModels.GoodnessOfFitMetrics import DataSetType
from mlos.Optimizers.RegressionModels.Prediction import Prediction
from mlos.Optimizers.RegressionModels.DecisionTreeRegressionModel import DecisionTreeRegressionModel, DecisionTreeRegressionModelConfig
from mlos.Optimizers.RegressionModels.HomogeneousRandomForestFitState import HomogeneousRandomForestFitState
from mlos.Optimizers.RegressionModels.RegressionModel import RegressionModel, RegressionModelConfig


class HomogeneousRandomForestRegressionModelConfig(RegressionModelConfig):

    CONFIG_SPACE = SimpleHypergrid(
        name="homogeneous_random_forest_regression_model_config",
        dimensions=[
            DiscreteDimension(name="n_estimators", min=1, max=100),
            ContinuousDimension(name="features_fraction_per_estimator", min=0, max=1, include_min=False, include_max=True),
            ContinuousDimension(name="samples_fraction_per_estimator", min=0, max=1, include_min=False, include_max=True),
            CategoricalDimension(name="regressor_implementation", values=[DecisionTreeRegressionModel.__name__]),
        ]
    ).join(
        subgrid=DecisionTreeRegressionModelConfig.CONFIG_SPACE,
        on_external_dimension=CategoricalDimension(name="regressor_implementation", values=[DecisionTreeRegressionModel.__name__])
    )

    _DEFAULT = Point(
        n_estimators=5,
        features_fraction_per_estimator=1,
        samples_fraction_per_estimator=0.7,
        regressor_implementation=DecisionTreeRegressionModel.__name__,
        decision_tree_regression_model_config=DecisionTreeRegressionModelConfig.DEFAULT
    )

    def __init__(
            self,
            n_estimators=_DEFAULT.n_estimators,
            features_fraction_per_estimator=_DEFAULT.features_fraction_per_estimator,
            samples_fraction_per_estimator=_DEFAULT.samples_fraction_per_estimator,
            regressor_implementation=_DEFAULT.regressor_implementation,
            decision_tree_regression_model_config: Point()=_DEFAULT.decision_tree_regression_model_config
    ):
        self.n_estimators = n_estimators
        self.features_fraction_per_estimator = features_fraction_per_estimator
        self.samples_fraction_per_estimator = samples_fraction_per_estimator
        self.regressor_implementation = regressor_implementation

        assert regressor_implementation == DecisionTreeRegressionModel.__name__
        self.decision_tree_regression_model_config = DecisionTreeRegressionModelConfig.create_from_config_point(decision_tree_regression_model_config)

    @classmethod
    def contains(cls, config): # pylint: disable=unused-argument
        return True  # TODO: see if you can remove this class entirely.


class HomogeneousRandomForestRegressionModel(RegressionModel):
    """ A RandomForest with homogeneously configured trees.

    This is the first implementation of a random forest regressor (and more generally of an ensemble model)
    that returns variance in addition to prediction. This should allow us to build a more robust bayesian
    optimizer.

    1. In this random forest, all decision trees are uniformly configured.
    2. Each decision tree receives a subset of features and a subset of rows.

    """

    _PREDICTOR_OUTPUT_COLUMNS = [
        Prediction.LegalColumnNames.IS_VALID_INPUT,
        Prediction.LegalColumnNames.PREDICTED_VALUE,
        Prediction.LegalColumnNames.PREDICTED_VALUE_VARIANCE,
        Prediction.LegalColumnNames.SAMPLE_VARIANCE,
        Prediction.LegalColumnNames.SAMPLE_SIZE,
        Prediction.LegalColumnNames.DEGREES_OF_FREEDOM
    ]

    @trace()
    def __init__(
            self,
            model_config: HomogeneousRandomForestRegressionModelConfig,
            input_space: Hypergrid,
            output_space: Hypergrid,
            logger=None
    ):
        if logger is None:
            logger = create_logger("HomogeneousRandomForestRegressionModel")
        self.logger = logger

        assert HomogeneousRandomForestRegressionModelConfig.contains(model_config)

        RegressionModel.__init__(
            self,
            model_type=type(self),
            model_config=model_config,
            input_space=input_space,
            output_space=output_space,
            fit_state=HomogeneousRandomForestFitState(input_space=input_space, output_space=output_space)
        )

        self._input_space_adapter = CompositeToSimpleHypergridAdapter(adaptee=self.input_space)
        self._output_space_adapter = CompositeToSimpleHypergridAdapter(adaptee=self.output_space)


        self.target_dimension_names = [dimension.name for dimension in self._output_space_adapter.dimensions]
        assert len(self.target_dimension_names) == 1, "Single target predictions for now."

        self._decision_trees = []
        self._create_estimators()

    @trace()
    def _create_estimators(self):
        """ Create individual estimators.

        Each estimator is meant to have a different subset of features and a different subset of samples.

        In the long run, we can solve it by creating an DataSet or DataSetView class, then each
        estimator would have its own DataSetView object that would know which data points to fetch and
        how to do it.

        For now however, I'll do it here in-line to get it working.

        1. Selecting features - to select a subset of features for each estimator we will:
            1. Create a random valid point in the search space. Any such valid config will not contain mutually exclusive
                parameters (for example if we chose an LRU eviction strategy, we won't get any parameters for a Random eviction strategy)
            2. Select a subset of dimensions from such a valid point so that we comply with the 'features_fraction_per_estimator' value.
            3. Build an input hypergrid for each estimator. However dimensions from above could be deeply nested.
                For example: smart_cache_config.lru_cache_config.lru_cache_size. We don't need the individual hypergrids
                to be nested at all so we will 'flatten' the dimension name by replacing the '.' with another delimiter.
                Then for each observation we will flatten the names again to see if the observation belongs to our observation
                space. If it does, then we can use our observation selection filter to decide if we want to feed that observation
                to the model. I'll leave the observation selection filter implementation for some other day.

        :return:
        """
        # Now we get to create all the estimators, each with a different feature subset and a different
        # observation filter

        self.logger.debug(f"Creating {self.model_config.n_estimators} estimators. Request id: {random.random()}")

        all_dimension_names = [dimension.name for dimension in self.input_space.dimensions]
        total_num_dimensions = len(all_dimension_names)
        features_per_estimator = max(1, math.ceil(total_num_dimensions * self.model_config.features_fraction_per_estimator))

        for i in range(self.model_config.n_estimators):
            estimator_input_space = self._create_random_flat_subspace(
                original_space=self.input_space,
                subspace_name=f"estimator_{i}_input_space",
                max_num_dimensions=features_per_estimator
            )

            estimator = DecisionTreeRegressionModel(
                model_config=self.model_config.decision_tree_regression_model_config,
                input_space=estimator_input_space,
                output_space=self.output_space,
                logger=self.logger
            )

            # TODO: each one of them also needs a sample filter.
            self._decision_trees.append(estimator)
            self.fit_state.decision_trees_fit_states.append(estimator.fit_state)

    @staticmethod
    def _create_random_flat_subspace(original_space, subspace_name, max_num_dimensions):
        """ Creates a random simple hypergrid from the hypergrid with up to max_num_dimensions dimensions.

        TODO: move this to the *Hypergrid classes.

        :param original_space:
        :return:
        """
        random_point = original_space.random()
        dimensions_for_point = original_space.get_dimensions_for_point(random_point)
        selected_dimensions = random.sample(dimensions_for_point, min(len(dimensions_for_point), max_num_dimensions))
        flat_dimensions = []
        for dimension in selected_dimensions:
            flat_dimension = dimension.copy()
            flat_dimension.name = Dimension.flatten_dimension_name(flat_dimension.name)
            flat_dimensions.append(flat_dimension)
        flat_hypergrid = SimpleHypergrid(
            name=subspace_name,
            dimensions=flat_dimensions
        )
        return flat_hypergrid

    @trace()
    def fit(self, feature_values_pandas_frame, target_values_pandas_frame, iteration_number):
        """ Fits the random forest.

            The issue here is that the feature_values will come in as a numpy array where each column corresponds to one
            of the dimensions in our input space. The target_values will come in a similar numpy array with each column
            corresponding to a single dimension in our output space.

            Our goal is to slice them up and feed the observations to individual decision trees.

        :param feature_values:
        :param target_values:
        :return:
        """
        self.logger.debug(f"Fitting a {self.__class__.__name__} with {len(feature_values_pandas_frame.index)} observations.")

        feature_values_pandas_frame = self._input_space_adapter.translate_dataframe(feature_values_pandas_frame, in_place=False)
        target_values_pandas_frame = self._output_space_adapter.translate_dataframe(target_values_pandas_frame)

        for i, tree in enumerate(self._decision_trees):
            # Let's filter out samples with missing values
            estimators_df = feature_values_pandas_frame[tree.input_dimension_names]
            non_null_observations = estimators_df[estimators_df.notnull().all(axis=1)]
            targets_for_non_null_observations = target_values_pandas_frame.loc[non_null_observations.index]

            observations_for_tree_training = non_null_observations.sample(
                frac=self.model_config.samples_fraction_per_estimator,
                replace=False, # TODO: add options to control bootstrapping vs. subsampling,
                random_state=i,
                axis='index'
            )
            observations_for_tree_validation = non_null_observations.loc[non_null_observations.index.difference(observations_for_tree_training.index)]
            num_selected_observations = len(observations_for_tree_training.index)
            if tree.should_fit(num_selected_observations):
                assert len(non_null_observations.index) == len(targets_for_non_null_observations.index)
                targets_for_tree_training = targets_for_non_null_observations.loc[observations_for_tree_training.index]
                tree.fit(
                    feature_values_pandas_frame=observations_for_tree_training,
                    target_values_pandas_frame=targets_for_tree_training,
                    iteration_number=iteration_number
                )
                tree.compute_goodness_of_fit(features_df=observations_for_tree_training, target_df=targets_for_tree_training, data_set_type=DataSetType.TRAIN)
                if not observations_for_tree_validation.empty:
                    targets_for_tree_validation = targets_for_non_null_observations.loc[observations_for_tree_validation.index]
                    tree.compute_goodness_of_fit(
                        features_df=observations_for_tree_validation,
                        target_df=targets_for_tree_validation,
                        data_set_type=DataSetType.VALIDATION
                    )

        self.last_refit_iteration_number = max(tree.last_refit_iteration_number for tree in self._decision_trees)
        self.fitted = any(tree.fitted for tree in self._decision_trees)

    @trace()
    def predict(self, feature_values_pandas_frame, include_only_valid_rows=True):
        """ Aggregate predictions from all estimators

        see: https://arxiv.org/pdf/1211.0906.pdf
        section: 4.3.2 for details

        :param feature_values_pandas_frame:
        :return: Prediction
        """
        self.logger.debug(f"Creating predictions for {len(feature_values_pandas_frame.index)} samples.")

        feature_values_pandas_frame = self._input_space_adapter.translate_dataframe(feature_values_pandas_frame)

        # dataframe column shortcuts
        is_valid_input_col = Prediction.LegalColumnNames.IS_VALID_INPUT.value
        predicted_value_col = Prediction.LegalColumnNames.PREDICTED_VALUE.value
        predicted_value_var_col = Prediction.LegalColumnNames.PREDICTED_VALUE_VARIANCE.value
        sample_var_col = Prediction.LegalColumnNames.SAMPLE_VARIANCE.value
        sample_size_col = Prediction.LegalColumnNames.SAMPLE_SIZE.value
        dof_col = Prediction.LegalColumnNames.DEGREES_OF_FREEDOM.value

        # collect predictions from ensemble constituent models
        predictions_per_tree = [
            estimator.predict(feature_values_pandas_frame=feature_values_pandas_frame, include_only_valid_rows=True)
            for estimator in self._decision_trees
        ]
        prediction_dataframes_per_tree = [prediction.get_dataframe() for prediction in predictions_per_tree]
        num_prediction_dataframes = len(prediction_dataframes_per_tree)

        # We will be concatenating all these prediction dataframes together, but to to avoid duplicate columns, we first rename them.
        #
        old_names = [predicted_value_col, predicted_value_var_col, sample_var_col, sample_size_col, dof_col]
        predicted_value_col_names_per_tree = [f"{predicted_value_col}_{i}" for i in range(num_prediction_dataframes)]
        mean_var_col_names_per_tree = [f"{predicted_value_var_col}_{i}" for i in range(num_prediction_dataframes)]
        sample_var_col_names_per_tree = [f"{sample_var_col}_{i}" for i in range(num_prediction_dataframes)]
        sample_size_col_names_per_tree = [f"{sample_size_col}_{i}" for i in range(num_prediction_dataframes)]

        for i in range(num_prediction_dataframes):
            new_names = [f"{old_name}_{i}" for old_name in old_names]
            old_names_to_new_names_mapping = {old_name: new_name for old_name, new_name in zip(old_names, new_names)}
            prediction_dataframes_per_tree[i].drop(columns=[is_valid_input_col], inplace=True)
            # We can safely overwrite them in place since we are their sole owner by now.
            prediction_dataframes_per_tree[i].rename(columns=old_names_to_new_names_mapping, inplace=True)

        # This creates a 'wide' dataframe with unique column names.
        #
        all_predictions_df = pd.concat(prediction_dataframes_per_tree, axis=1)
        all_predictions_df[predicted_value_col] = all_predictions_df[predicted_value_col_names_per_tree].apply('mean', axis=1)

        # To compute the pooled variance we will use the second to last form of the equation from the paper:
        #   paper: https://arxiv.org/pdf/1211.0906.pdf
        #   section: section: 4.3.2 for details
        all_predictions_df[predicted_value_var_col] = all_predictions_df[mean_var_col_names_per_tree].mean(axis=1) \
                                             + (all_predictions_df[predicted_value_col_names_per_tree] ** 2).mean(axis=1) \
                                             - all_predictions_df[predicted_value_col] ** 2
        all_predictions_df[sample_var_col] = all_predictions_df[sample_var_col_names_per_tree].mean(axis=1) \
                                             + (all_predictions_df[predicted_value_col_names_per_tree] ** 2).mean(axis=1) \
                                             - all_predictions_df[predicted_value_col] ** 2
        all_predictions_df[sample_size_col] = all_predictions_df[predicted_value_col_names_per_tree].count(axis=1)
        all_predictions_df[dof_col] = all_predictions_df[sample_size_col_names_per_tree].sum(axis=1) - all_predictions_df[sample_size_col]
        all_predictions_df[is_valid_input_col] = True

        aggregate_predictions = Prediction(
            objective_name=self.target_dimension_names[0],
            predictor_outputs=self._PREDICTOR_OUTPUT_COLUMNS,
            allow_extra_columns=True
        )

        aggregate_predictions_df = all_predictions_df[[column.value for column in self._PREDICTOR_OUTPUT_COLUMNS]]
        aggregate_predictions.set_dataframe(aggregate_predictions_df)
        if not include_only_valid_rows:
            aggregate_predictions.add_invalid_rows_at_missing_indices(desired_index=feature_values_pandas_frame.index)
        return aggregate_predictions
