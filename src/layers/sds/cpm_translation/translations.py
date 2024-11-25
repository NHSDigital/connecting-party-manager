# from functools import partial
# from itertools import filterfalse
# from typing import Generator

# import orjson
# from domain.api.sds.query import (
#     SearchSDSDeviceQueryParams,
#     SearchSDSEndpointQueryParams,
# )
# from domain.core.device.v2 import Device, DeviceType
# from domain.core.device_key.v1 import DeviceKeyType
# from domain.core.product_team.v2 import ProductTeam
# from domain.core.root.v2 import Root
# from domain.core.validation import DEVICE_KEY_SEPARATOR
# from domain.repository.device_repository.v2 import DeviceRepository
# from sds.domain.nhs_accredited_system import NhsAccreditedSystem
# from sds.domain.nhs_mhs import NhsMhs
# from sds.domain.parse import UnknownSdsModel
# from sds.domain.sds_deletion_request import SdsDeletionRequest
# from sds.domain.sds_modification_request import SdsModificationRequest

# from .constants import (
#     BAD_UNIQUE_IDENTIFIERS,
#     DEFAULT_ORGANISATION,
#     DEFAULT_PRODUCT_TEAM,
#     EXCEPTIONAL_ODS_CODES,
# )
# from .modify_device import update_device_metadata
# from .modify_key import NotAnSdsKey, get_modify_key_function
# from .utils import set_device_tags, set_device_tags_bulk, update_in_list_of_dict


# def accredited_system_ids(
#     nhs_accredited_system: NhsAccreditedSystem,
# ) -> Generator[tuple[str, str], None, None]:
#     for ods_code in nhs_accredited_system.nhs_as_client or [DEFAULT_ORGANISATION]:
#         yield ods_code, DEVICE_KEY_SEPARATOR.join(
#             (ods_code, nhs_accredited_system.unique_identifier)
#         )


# def scoped_party_key(nhs_mhs: NhsMhs) -> str:
#     return DEVICE_KEY_SEPARATOR.join(
#         map(
#             str.strip,
#             (getattr(nhs_mhs, key) for key in NhsMhs.key_fields()),
#         )
#     )


# def create_product_team(ods_code: str) -> ProductTeam:
#     if ods_code in EXCEPTIONAL_ODS_CODES:
#         product_team = ProductTeam(**DEFAULT_PRODUCT_TEAM, ods_code=ods_code)
#     else:
#         organisation = Root.create_ods_organisation(ods_code=ods_code)
#         product_team = organisation.create_product_team(**DEFAULT_PRODUCT_TEAM)
#     return product_team


# def nhs_accredited_system_to_cpm_devices(
#     nhs_accredited_system: NhsAccreditedSystem, bulk: bool
# ) -> Generator[Device, None, None]:
#     unique_identifier = nhs_accredited_system.unique_identifier
#     product_name = nhs_accredited_system.nhs_product_name or unique_identifier
#     raw_questionnaire_response_answers = nhs_accredited_system.export()
#     questionnaire_response_answers = (
#         nhs_accredited_system.as_questionnaire_response_answers(
#             data=raw_questionnaire_response_answers
#         )
#     )

#     questionnaire = NhsAccreditedSystem.questionnaire()

#     for (
#         ods_code,
#         accredited_system_id,
#     ) in accredited_system_ids(nhs_accredited_system):
#         update_in_list_of_dict(
#             obj=questionnaire_response_answers,
#             key="nhs_as_client",
#             value=[ods_code],
#         )
#         _questionnaire_response = questionnaire.respond(
#             responses=questionnaire_response_answers
#         )
#         _organisation = Root.create_ods_organisation(ods_code=ods_code)
#         _product_team = _organisation.create_product_team(**DEFAULT_PRODUCT_TEAM)
#         _device = _product_team.create_device(
#             name=product_name, device_type=DeviceType.PRODUCT
#         )
#         _device.add_key(
#             key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID,
#             key_value=accredited_system_id,
#         )
#         _device.add_questionnaire_response(
#             questionnaire_response=_questionnaire_response
#         )
#         if bulk:
#             set_device_tags_bulk(
#                 device=_device,
#                 data=raw_questionnaire_response_answers,
#                 model=SearchSDSDeviceQueryParams,
#             )
#         else:
#             set_device_tags(
#                 device=_device,
#                 data=raw_questionnaire_response_answers,
#                 model=SearchSDSDeviceQueryParams,
#             )
#         yield _device


# def nhs_mhs_to_cpm_device(nhs_mhs: NhsMhs, bulk: bool) -> Device:
#     ods_code = nhs_mhs.nhs_id_code
#     _scoped_party_key = scoped_party_key(nhs_mhs)
#     product_name = nhs_mhs.nhs_product_name or _scoped_party_key
#     raw_questionnaire_response_answers = orjson.loads(
#         nhs_mhs.json(exclude_none=True, exclude={"change_type"})
#     )
#     questionnaire_response_answers = nhs_mhs.as_questionnaire_response_answers(
#         data=raw_questionnaire_response_answers
#     )

#     questionnaire = NhsMhs.questionnaire()
#     questionnaire_response = questionnaire.respond(
#         responses=questionnaire_response_answers
#     )

#     product_team = create_product_team(ods_code=ods_code)
#     device = product_team.create_device(
#         name=product_name, device_type=DeviceType.ENDPOINT
#     )
#     device.add_key(
#         key_type=DeviceKeyType.MESSAGE_HANDLING_SYSTEM_ID,
#         key_value=_scoped_party_key,
#     )
#     device.add_questionnaire_response(questionnaire_response=questionnaire_response)
#     if bulk:
#         set_device_tags_bulk(
#             device=device,
#             data=raw_questionnaire_response_answers,
#             model=SearchSDSEndpointQueryParams,
#         )
#     else:
#         set_device_tags(
#             device=device,
#             data=raw_questionnaire_response_answers,
#             model=SearchSDSEndpointQueryParams,
#         )
#     return device


# def modify_devices(
#     modification_request: SdsModificationRequest, repository: DeviceRepository
# ) -> Generator[Device, None, None]:
#     devices = repository.query_by_tag(
#         unique_identifier=modification_request.unique_identifier, drop_tags_field=False
#     )

#     # Only apply modifications if there are devices to modify
#     modifications = modification_request.modifications if devices else []

#     _devices = devices
#     for modification_type, field, new_values in modifications:
#         device_type = _devices[0].device_type
#         model = NhsAccreditedSystem if device_type is DeviceType.PRODUCT else NhsMhs
#         field_name = model.get_field_name_for_alias(alias=field)

#         try:
#             modify_key = get_modify_key_function(
#                 model=model,
#                 field_name=field_name,
#                 modification_type=modification_type,
#             )
#             _devices = list(
#                 modify_key(devices=_devices, field_name=field_name, value=new_values)
#             )
#         except NotAnSdsKey:
#             update_metadata = partial(
#                 update_device_metadata,
#                 model=model,
#                 modification_type=modification_type,
#                 field_alias=field,
#                 new_values=new_values,
#             )
#             _active_devices = list(filter(Device.is_active, _devices))
#             _inactive_devices = list(filterfalse(Device.is_active, _devices))
#             _devices = [*map(update_metadata, _active_devices), *_inactive_devices]
#     yield from _devices


# def delete_devices(
#     deletion_request: SdsDeletionRequest, repository: DeviceRepository
# ) -> list[Device]:
#     devices = []
#     for _device in repository.query_by_tag(
#         unique_identifier=deletion_request.unique_identifier, drop_tags_field=False
#     ):
#         _device.delete()
#         devices.append(_device)
#     return devices


# def translate(obj: dict[str, str], repository: DeviceRepository, bulk: bool):
#     if obj.get("unique_identifier") in BAD_UNIQUE_IDENTIFIERS:
#         return []

#     object_class = obj["object_class"].lower()
#     if object_class == NhsAccreditedSystem.OBJECT_CLASS:
#         nhs_accredited_system = NhsAccreditedSystem.construct(**obj)
#         devices = nhs_accredited_system_to_cpm_devices(
#             nhs_accredited_system=nhs_accredited_system, bulk=bulk
#         )
#     elif object_class == NhsMhs.OBJECT_CLASS:
#         nhs_mhs = NhsMhs.construct(**obj)
#         device = nhs_mhs_to_cpm_device(nhs_mhs=nhs_mhs, bulk=bulk)
#         devices = [device]
#     elif object_class == SdsDeletionRequest.OBJECT_CLASS:
#         deletion_request = SdsDeletionRequest.construct(**obj)
#         devices = delete_devices(
#             deletion_request=deletion_request, repository=repository
#         )
#     elif object_class == SdsModificationRequest.OBJECT_CLASS:
#         modification_request = SdsModificationRequest.construct(**obj)
#         devices = modify_devices(
#             modification_request=modification_request, repository=repository
#         )
#     else:
#         raise UnknownSdsModel(
#             f"No translation available for models with object class '{object_class}'"
#         )
#     return devices
