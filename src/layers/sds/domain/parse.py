from typing import IO, Callable, Generator

from etl_utils.ldif.ldif import parse_ldif
from etl_utils.ldif.model import DistinguishedName
from sds.domain.nhs_mhs_cp import NhsMhsCp

from .base import OBJECT_CLASS_FIELD_NAME, SdsBaseModel
from .nhs_accredited_system import NhsAccreditedSystem
from .nhs_mhs import NhsMhs
from .nhs_mhs_action import NhsMhsAction
from .nhs_mhs_service import NhsMhsService
from .organizational_unit import OrganizationalUnit


class UnknownSdsModel(Exception):
    pass


MODELS = (
    OrganizationalUnit,
    NhsAccreditedSystem,
    NhsMhsAction,
    NhsMhsService,
    NhsMhs,
    NhsMhsCp,
)

EMPTY_SET = set()


def parse_ldif_to_sds(
    file_opener: Callable[[str | bytes], IO],
    path_or_data: str | bytes,
    skip: list[int] = None,  # required because of bad test data
) -> Generator[SdsBaseModel, None, None]:
    for i, (distinguished_name, record) in enumerate(
        parse_ldif(file_opener=file_opener, path_or_data=path_or_data)
    ):
        if skip and i in skip:
            continue
        try:
            yield _parse_sds_record(
                distinguished_name=distinguished_name, record=record
            )
        except Exception as exc:
            raise ExceptionGroup(f"Failed to parse record {i}\n{record}", [exc])


def _parse_sds_record(
    distinguished_name: DistinguishedName,
    record: dict,
    models: tuple[type[SdsBaseModel]] = MODELS,
):
    object_class = record.get(OBJECT_CLASS_FIELD_NAME, EMPTY_SET)

    model = None
    for _model in models:
        if any(map(_model.matches_object_class, object_class)):
            model = _model
            break
    if model is not None:
        return model(_distinguished_name=distinguished_name, **record)
    raise UnknownSdsModel(f"Could not find a model to parse record\n{record}")