#!/bin/bash
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# We need to recreate the structure of the python module in the input to grpc
# to have the imports be generated correctly.
# See https://github.com/grpc/grpc/issues/9575#issuecomment-293934506
#
# Note: We currently do not use imports in order to keep OptimizerMonitoringService
# and OptimizerService seperate for future iterations (one may lead the other)
#


set -eu

# Start in the script directory.
scriptdir=$(readlink -f "$(dirname "$0")")
MLOS_ROOT=$(readlink -f "$scriptdir/../..")

. "$MLOS_ROOT/scripts/util.sh"
pythonCmd=$(getPythonCmd)

cd "$scriptdir"
mkdir -p mlos/Grpc

cp *.proto mlos/Grpc/
$pythonCmd -m grpc_tools.protoc -I . --python_out=../Mlos.Python --grpc_python_out=../Mlos.Python mlos/Grpc/*.proto

rm -rf mlos
