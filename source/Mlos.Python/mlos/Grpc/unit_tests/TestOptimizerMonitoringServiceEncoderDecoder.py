#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#

import pytest

from mlos.Grpc.OptimizerMonitoringServiceEncoderDecoder import OptimizerMonitoringServiceDecoder, OptimizerMonitoringServiceEncoder

from mlos.Grpc import OptimizerMonitoringService_pb2
from mlos.Optimizers.OptimizationProblem import OptimizationProblem, Objective
from mlos.Spaces import CategoricalDimension,\
    ContinuousDimension, DiscreteDimension, EmptyDimension, OrdinalDimension, SimpleHypergrid
from mlos.Optimizers.BayesianOptimizerConfigStore import bayesian_optimizer_config_store

# Note:
# As of 2021-06-15, the OptimizerService and OptimizerMonitoringService have identical encoders and decoders. As such, I have
# duplicated the unit tests. The fact that they are currently identical is simply a response to the current design state and does
# not reflect the future design of the API.
#
class TestOptimizerMonitoringServiceEncoderDecoder:
    """Tests encoding and decoding for dimensions.

    """

    def test_empty_dimension(self):
        empty_dimension = EmptyDimension(name="empty", type=ContinuousDimension)
        serialized = OptimizerMonitoringServiceEncoder.encode_empty_dimension(empty_dimension)
        deserialized_empty_dimension = OptimizerMonitoringServiceDecoder.decode_empty_dimension(serialized)

        assert isinstance(serialized, OptimizerMonitoringService_pb2.EmptyDimension)
        assert empty_dimension == deserialized_empty_dimension

    def test_categorical_dimension(self):
        categorical_dimension = CategoricalDimension(name='categorical', values=[0, 1, True, False, "red", "green", "blue", 3.14, 7.5])
        serialized = OptimizerMonitoringServiceEncoder.encode_categorical_dimension(categorical_dimension)
        deserialized_categorical_dimension = OptimizerMonitoringServiceDecoder.decode_categorical_dimension(serialized)

        assert isinstance(serialized, OptimizerMonitoringService_pb2.CategoricalDimension)
        assert categorical_dimension == deserialized_categorical_dimension

    @pytest.mark.parametrize('include_min', [True, False])
    @pytest.mark.parametrize('include_max', [True, False])
    def test_continuous_dimension(self, include_min, include_max):
        continuous_dimension = ContinuousDimension(name='continuous', min=0, max=10, include_min=include_min, include_max=include_max)
        serialized = OptimizerMonitoringServiceEncoder.encode_continuous_dimension(continuous_dimension)
        deserialized_continuous_dimension = OptimizerMonitoringServiceDecoder.decode_continuous_dimension(serialized)
        assert isinstance(serialized, OptimizerMonitoringService_pb2.ContinuousDimension)
        assert deserialized_continuous_dimension == continuous_dimension

    def test_discrete_dimension(self):
        discrete_dimension = DiscreteDimension(name='discrete', min=1, max=100)
        serialized = OptimizerMonitoringServiceEncoder.encode_discrete_dimension(discrete_dimension)
        deserialized = OptimizerMonitoringServiceDecoder.decode_discrete_dimension(serialized)
        assert isinstance(serialized, OptimizerMonitoringService_pb2.DiscreteDimension)
        assert discrete_dimension == deserialized

    def test_ordinal_dimension(self):
        ordinal_dimension = OrdinalDimension(name='ordinal', ordered_values=['good', 'better', 'best'])
        serialized = OptimizerMonitoringServiceEncoder.encode_ordinal_dimension(ordinal_dimension)
        deserialized = OptimizerMonitoringServiceDecoder.decode_ordinal_dimension(serialized)
        assert deserialized == ordinal_dimension
        assert isinstance(serialized, OptimizerMonitoringService_pb2.OrdinalDimension)

    def test_composite_dimension(self):
        original_A = ContinuousDimension(name='x', min=0, max=1)
        original_B = ContinuousDimension(name='x', min=2, max=3)
        original_C = ContinuousDimension(name='x', min=2.5, max=3.5)
        original_D = original_A.union(original_B) - original_C
        original_E = original_B - original_C
        original_F = original_A.union(original_E)

        serialized_A = OptimizerMonitoringServiceEncoder.encode_continuous_dimension(original_A)
        serialized_B = OptimizerMonitoringServiceEncoder.encode_continuous_dimension(original_B)
        serialized_C = OptimizerMonitoringServiceEncoder.encode_continuous_dimension(original_C)
        serialized_D = OptimizerMonitoringServiceEncoder.encode_composite_dimension(original_D)
        serialized_E = OptimizerMonitoringServiceEncoder.encode_continuous_dimension(original_E)
        serialized_F = OptimizerMonitoringServiceEncoder.encode_composite_dimension(original_F)

        A = OptimizerMonitoringServiceDecoder.decode_continuous_dimension(serialized_A)
        B = OptimizerMonitoringServiceDecoder.decode_continuous_dimension(serialized_B)
        C = OptimizerMonitoringServiceDecoder.decode_continuous_dimension(serialized_C)
        D = OptimizerMonitoringServiceDecoder.decode_composite_dimension(serialized_D)
        E = OptimizerMonitoringServiceDecoder.decode_continuous_dimension(serialized_E)
        F = OptimizerMonitoringServiceDecoder.decode_composite_dimension(serialized_F)

        assert A in original_A
        assert B in original_B
        assert C in original_C
        assert D in original_D
        assert E in original_E
        assert F in original_F

        assert original_A in A
        assert original_B in B
        assert original_C in C
        assert original_D in D
        assert original_E in E
        assert original_F in F

        assert 0.5 in D
        assert 1.5 not in D
        assert 2.5 not in D
        assert 3.4 not in D
        assert 35 not in D
        assert 2 in E
        assert 2.5 not in E
        assert 0 in F and 1 in F and 1.5 not in F and 2 in F and 2.5 not in F


    def test_hypergrid(self):
        parameter_space = bayesian_optimizer_config_store.parameter_space
        serialized = OptimizerMonitoringServiceEncoder.encode_hypergrid(parameter_space)
        deserialized = OptimizerMonitoringServiceDecoder.decode_hypergrid(serialized)

        print(deserialized)

        for _ in range(1000):
            assert deserialized.random() in parameter_space

        for _ in range(1000):
            assert parameter_space.random() in deserialized

    def test_optimization_problem(self):
        parameter_space = SimpleHypergrid(
            name="test",
            dimensions=[
                ContinuousDimension(name="x",min=0,max=1),
                CategoricalDimension(name="y",values=[1,2,3])
            ]
        )
        objective_space = SimpleHypergrid(
            name="z",
            dimensions=[
                ContinuousDimension(name="z",min=0,max=1),
                ContinuousDimension(name="z1",min=-1,max=1)
            ]
        )
        context_space = SimpleHypergrid(
            name="context_space",
            dimensions=[
                ContinuousDimension(name="x_c",min=0,max=1),
                CategoricalDimension(name="y_c",values=[1,2,3,4,6])
            ]
        )
        optimization_problem = OptimizationProblem(
            parameter_space=parameter_space,
            objective_space=objective_space,
            objectives=[
                Objective(name="z",minimize=True),
                Objective(name="z1",minimize=False)
            ],
            context_space=context_space
        )
        encoded_problem = OptimizerMonitoringServiceEncoder.encode_optimization_problem(optimization_problem)
        decoded_problem = OptimizerMonitoringServiceDecoder.decode_optimization_problem(encoded_problem)

        # A = B iff A >= B && B <= A
        # Could be condensed to single loop but easier to read this way.
        # Parameter Space
        for _ in range(1000):
            assert decoded_problem.parameter_space.random() in parameter_space
            assert parameter_space.random() in decoded_problem.parameter_space

        # Output Space
        for _ in range(1000):
            assert decoded_problem.objective_space.random() in objective_space
            assert objective_space.random() in decoded_problem.objective_space

        # Context Space
        for _ in range(1000):
            assert decoded_problem.context_space.random() in context_space
            assert context_space.random() in decoded_problem.context_space

        print(decoded_problem.objectives)
        assert len(decoded_problem.objectives) == 2
        assert decoded_problem.objectives[0].name=="z"
        assert decoded_problem.objectives[1].name=="z1"
        assert decoded_problem.objectives[0].minimize
        assert decoded_problem.objectives[1].minimize == False

    def test_optimization_problem_none_context(self):
        optimization_problem = OptimizationProblem(
            parameter_space=SimpleHypergrid(name="p_s", dimensions=[]),
            objective_space=SimpleHypergrid(name="o_s", dimensions=[]),
            objectives=[]
        )

        encoded_problem=OptimizerMonitoringServiceEncoder.encode_optimization_problem(optimization_problem)
        decoded_problem=OptimizerMonitoringServiceDecoder.decode_optimization_problem(encoded_problem)

        print(f"Context space is: {decoded_problem.context_space}")
        assert decoded_problem.context_space is None


