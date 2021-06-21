// -----------------------------------------------------------------------
// <copyright file="BayesianOptimizerProxy.cs" company="Microsoft Corporation">
// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See LICENSE in the project root
// for license information.
// </copyright>
// -----------------------------------------------------------------------

using System;
using System.Linq;

using Mlos.Core;
using Mlos.Model.Services.Spaces;

namespace Mlos.Model.Services.Client.BayesianOptimizer
{
    /// <summary>
    /// A proxy to a BayesianOptimizer executing within the Mlos.Model.Services.
    /// </summary>
    public class BayesianOptimizerProxy : IOptimizerProxy
    {
        private readonly OptimizerService.OptimizerService.OptimizerServiceClient client;

        private readonly OptimizerService.OptimizerHandle optimizerHandle;

        public BayesianOptimizerProxy(OptimizerService.OptimizerService.OptimizerServiceClient client, OptimizerService.OptimizerHandle optimizerHandle)
        {
            this.client = client;
            this.optimizerHandle = optimizerHandle;
        }

        /// <inheritdoc/>
        public IOptimizationProblem GetOptimizationProblem()
        {
            OptimizerService.OptimizerInfo optimizerInfo = client.GetOptimizerInfo(optimizerHandle);

            OptimizationProblem optimizationProblem = OptimizerServiceDecoder.DecodeOptimizationProblem(optimizerInfo.OptimizationProblem);

            // Add optimization objectives.
            //
            optimizationProblem.Objectives.AddRange(
                optimizerInfo.OptimizationProblem.Objectives.Select(r =>
                    new OptimizationObjective(r.Name, r.Minimize)));

            return optimizationProblem;
        }

        /// <inheritdoc/>
        public void Register(string paramsJsonString, string objectiveName, double objectiveValue)
        {
            Console.WriteLine("test");
            client.RegisterObservation(
                new OptimizerService.RegisterObservationRequest
                {
                    OptimizerHandle = optimizerHandle,
                    Observation = new OptimizerService.Observation
                    {
                        Features = new OptimizerService.Features
                        {
                            FeaturesJsonString = paramsJsonString,
                        },
                        ObjectiveValues = new OptimizerService.ObjectiveValues
                        {
                            ObjectiveValuesJsonString = @$"{{""{objectiveName}"": {objectiveValue} }}",
                        },
                    },
                });

            Console.WriteLine($"Register {paramsJsonString} {objectiveName} = {objectiveValue}");
        }

        /// <inheritdoc/>
        public string Suggest(bool random = false)
        {
            OptimizerService.ConfigurationParameters configurationParameters = client.Suggest(
                new OptimizerService.SuggestRequest
                {
                    OptimizerHandle = optimizerHandle,
                    Context = new OptimizerService.Context
                    {
                        ContextJsonString = string.Empty,
                    },
                    Random = random,
                });

            string suggestedParameter = configurationParameters.ParametersJsonString;
            Console.WriteLine($"Suggest random={random} {suggestedParameter}");
            return suggestedParameter;
        }
    }
}
