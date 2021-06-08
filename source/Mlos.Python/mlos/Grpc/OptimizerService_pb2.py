# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: mlos/Grpc/OptimizerService.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from mlos.Grpc import OptimizerShared_pb2 as mlos_dot_Grpc_dot_OptimizerShared__pb2

from mlos.Grpc.OptimizerShared_pb2 import *

DESCRIPTOR = _descriptor.FileDescriptor(
  name='mlos/Grpc/OptimizerService.proto',
  package='mlos.optimizer_service',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n mlos/Grpc/OptimizerService.proto\x12\x16mlos.optimizer_service\x1a\x1fmlos/Grpc/OptimizerShared.proto\"\x81\x01\n\x16\x43reateOptimizerRequest\x12\x31\n\x13OptimizationProblem\x18\x01 \x01(\x0b\x32\x14.OptimizationProblem\x12\x1b\n\x13OptimizerConfigName\x18\x02 \x01(\t\x12\x17\n\x0fOptimizerConfig\x18\x03 \x01(\t\"f\n\x0eSuggestRequest\x12)\n\x0fOptimizerHandle\x18\x01 \x01(\x0b\x32\x10.OptimizerHandle\x12\x0e\n\x06Random\x18\x02 \x01(\x08\x12\x19\n\x07\x43ontext\x18\x03 \x01(\x0b\x32\x08.Context2\xfc\x02\n\x10OptimizerService\x12S\n\x0f\x43reateOptimizer\x12..mlos.optimizer_service.CreateOptimizerRequest\x1a\x10.OptimizerHandle\x12\x34\n\x10GetOptimizerInfo\x12\x10.OptimizerHandle\x1a\x0e.OptimizerInfo\x12K\n\x07Suggest\x12&.mlos.optimizer_service.SuggestRequest\x1a\x18.ConfigurationParameters\x12:\n\x13RegisterObservation\x12\x1b.RegisterObservationRequest\x1a\x06.Empty\x12<\n\x14RegisterObservations\x12\x1c.RegisterObservationsRequest\x1a\x06.Empty\x12\x16\n\x04\x45\x63ho\x12\x06.Empty\x1a\x06.EmptyP\x00\x62\x06proto3'
  ,
  dependencies=[mlos_dot_Grpc_dot_OptimizerShared__pb2.DESCRIPTOR,],
  public_dependencies=[mlos_dot_Grpc_dot_OptimizerShared__pb2.DESCRIPTOR,])




_CREATEOPTIMIZERREQUEST = _descriptor.Descriptor(
  name='CreateOptimizerRequest',
  full_name='mlos.optimizer_service.CreateOptimizerRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='OptimizationProblem', full_name='mlos.optimizer_service.CreateOptimizerRequest.OptimizationProblem', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='OptimizerConfigName', full_name='mlos.optimizer_service.CreateOptimizerRequest.OptimizerConfigName', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='OptimizerConfig', full_name='mlos.optimizer_service.CreateOptimizerRequest.OptimizerConfig', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=94,
  serialized_end=223,
)


_SUGGESTREQUEST = _descriptor.Descriptor(
  name='SuggestRequest',
  full_name='mlos.optimizer_service.SuggestRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='OptimizerHandle', full_name='mlos.optimizer_service.SuggestRequest.OptimizerHandle', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='Random', full_name='mlos.optimizer_service.SuggestRequest.Random', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='Context', full_name='mlos.optimizer_service.SuggestRequest.Context', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=225,
  serialized_end=327,
)

_CREATEOPTIMIZERREQUEST.fields_by_name['OptimizationProblem'].message_type = mlos_dot_Grpc_dot_OptimizerShared__pb2._OPTIMIZATIONPROBLEM
_SUGGESTREQUEST.fields_by_name['OptimizerHandle'].message_type = mlos_dot_Grpc_dot_OptimizerShared__pb2._OPTIMIZERHANDLE
_SUGGESTREQUEST.fields_by_name['Context'].message_type = mlos_dot_Grpc_dot_OptimizerShared__pb2._CONTEXT
DESCRIPTOR.message_types_by_name['CreateOptimizerRequest'] = _CREATEOPTIMIZERREQUEST
DESCRIPTOR.message_types_by_name['SuggestRequest'] = _SUGGESTREQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

CreateOptimizerRequest = _reflection.GeneratedProtocolMessageType('CreateOptimizerRequest', (_message.Message,), {
  'DESCRIPTOR' : _CREATEOPTIMIZERREQUEST,
  '__module__' : 'mlos.Grpc.OptimizerService_pb2'
  # @@protoc_insertion_point(class_scope:mlos.optimizer_service.CreateOptimizerRequest)
  })
_sym_db.RegisterMessage(CreateOptimizerRequest)

SuggestRequest = _reflection.GeneratedProtocolMessageType('SuggestRequest', (_message.Message,), {
  'DESCRIPTOR' : _SUGGESTREQUEST,
  '__module__' : 'mlos.Grpc.OptimizerService_pb2'
  # @@protoc_insertion_point(class_scope:mlos.optimizer_service.SuggestRequest)
  })
_sym_db.RegisterMessage(SuggestRequest)



_OPTIMIZERSERVICE = _descriptor.ServiceDescriptor(
  name='OptimizerService',
  full_name='mlos.optimizer_service.OptimizerService',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=330,
  serialized_end=710,
  methods=[
  _descriptor.MethodDescriptor(
    name='CreateOptimizer',
    full_name='mlos.optimizer_service.OptimizerService.CreateOptimizer',
    index=0,
    containing_service=None,
    input_type=_CREATEOPTIMIZERREQUEST,
    output_type=mlos_dot_Grpc_dot_OptimizerShared__pb2._OPTIMIZERHANDLE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='GetOptimizerInfo',
    full_name='mlos.optimizer_service.OptimizerService.GetOptimizerInfo',
    index=1,
    containing_service=None,
    input_type=mlos_dot_Grpc_dot_OptimizerShared__pb2._OPTIMIZERHANDLE,
    output_type=mlos_dot_Grpc_dot_OptimizerShared__pb2._OPTIMIZERINFO,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='Suggest',
    full_name='mlos.optimizer_service.OptimizerService.Suggest',
    index=2,
    containing_service=None,
    input_type=_SUGGESTREQUEST,
    output_type=mlos_dot_Grpc_dot_OptimizerShared__pb2._CONFIGURATIONPARAMETERS,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='RegisterObservation',
    full_name='mlos.optimizer_service.OptimizerService.RegisterObservation',
    index=3,
    containing_service=None,
    input_type=mlos_dot_Grpc_dot_OptimizerShared__pb2._REGISTEROBSERVATIONREQUEST,
    output_type=mlos_dot_Grpc_dot_OptimizerShared__pb2._EMPTY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='RegisterObservations',
    full_name='mlos.optimizer_service.OptimizerService.RegisterObservations',
    index=4,
    containing_service=None,
    input_type=mlos_dot_Grpc_dot_OptimizerShared__pb2._REGISTEROBSERVATIONSREQUEST,
    output_type=mlos_dot_Grpc_dot_OptimizerShared__pb2._EMPTY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='Echo',
    full_name='mlos.optimizer_service.OptimizerService.Echo',
    index=5,
    containing_service=None,
    input_type=mlos_dot_Grpc_dot_OptimizerShared__pb2._EMPTY,
    output_type=mlos_dot_Grpc_dot_OptimizerShared__pb2._EMPTY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_OPTIMIZERSERVICE)

DESCRIPTOR.services_by_name['OptimizerService'] = _OPTIMIZERSERVICE

# @@protoc_insertion_point(module_scope)
