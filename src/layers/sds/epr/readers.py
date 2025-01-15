from domain.core.cpm_product.v1 import CpmProduct
from domain.core.device.v1 import Device
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.enum import Environment
from domain.core.product_team.v1 import ProductTeam
from domain.core.questionnaire.v1 import QuestionnaireResponse
from domain.repository.cpm_product_repository.v1 import CpmProductRepository
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository.v1 import DeviceRepository
from domain.repository.errors import ItemNotFound
from domain.repository.product_team_repository.v1 import ProductTeamRepository
from sds.epr.constants import ADDITIONAL_INTERACTIONS_SUFFIX, EprNameTemplate
from sds.epr.creators import (
    create_additional_interactions,
    create_as_device,
    create_epr_product,
    create_epr_product_team,
    create_message_sets,
    create_mhs_device,
)
from sds.epr.utils import (
    is_additional_interactions_device_reference_data,
    is_as_device,
    is_message_set_device_reference_data,
    is_mhs_device,
)


def read_or_create_epr_product_team(
    ods_code: str, product_team_repository: ProductTeamRepository
) -> ProductTeam:
    try:
        product_team = product_team_repository.read(
            id=EprNameTemplate.PRODUCT_TEAM_KEY.format(ods_code=ods_code)
        )
    except ItemNotFound:
        product_team = create_epr_product_team(ods_code=ods_code)
    return product_team


def read_or_create_epr_product(
    product_team: ProductTeam,
    product_name: str,
    party_key: str,
    product_repository: CpmProductRepository,
) -> CpmProduct:
    try:
        product = product_repository.read(product_team_id=product_team.id, id=party_key)
    except ItemNotFound:
        product = create_epr_product(
            product_team=product_team, product_name=product_name, party_key=party_key
        )
    return product


def read_additional_interactions_if_exists(
    device_reference_data_repository: DeviceReferenceDataRepository,
    product_team_id: str,
    product_id: str,
) -> DeviceReferenceData | None:
    device_reference_datas = device_reference_data_repository.search(
        product_team_id=product_team_id,
        product_id=product_id,
        environment=Environment.PROD,
    )

    additional_interactions = None
    try:
        (additional_interactions,) = filter(
            is_additional_interactions_device_reference_data, device_reference_datas
        )
    except ValueError:
        pass
    return additional_interactions


def read_or_create_empty_message_sets(
    product: CpmProduct,
    party_key: str,
    device_reference_data_repository: DeviceReferenceDataRepository,
) -> DeviceReferenceData:
    device_reference_datas = device_reference_data_repository.search(
        product_team_id=product.product_team_id,
        product_id=product.id,
        environment=Environment.PROD,
    )

    try:
        (message_sets,) = filter(
            is_message_set_device_reference_data, device_reference_datas
        )
    except ValueError:
        message_sets = create_message_sets(
            product=product, party_key=party_key, message_set_data=[]
        )
    return message_sets


def read_or_create_mhs_device(
    device_repository: DeviceRepository,
    cpa_id: str,
    party_key: str,
    product_team: ProductTeam,
    product: CpmProduct,
    message_sets: DeviceReferenceData,
    mhs_device_data: QuestionnaireResponse,
) -> Device:
    devices = device_repository.search(
        product_team_id=product_team.id,
        product_id=product.id,
        environment=Environment.PROD,
    )
    try:
        (mhs_device,) = filter(is_mhs_device, devices)
    except ValueError:
        mhs_device = create_mhs_device(
            product=product,
            party_key=party_key,
            mhs_device_data=mhs_device_data,
            cpa_ids=[cpa_id],
            message_sets_id=message_sets.id,
        )
    return mhs_device


def read_or_create_empty_additional_interactions(
    product: CpmProduct,
    party_key: str,
    device_reference_data_repository: DeviceReferenceDataRepository,
) -> DeviceReferenceData:
    device_reference_datas = device_reference_data_repository.search(
        product_team_id=product.product_team_id,
        product_id=product.id,
        environment=Environment.PROD,
    )

    try:
        (additional_interactions,) = filter(
            is_additional_interactions_device_reference_data, device_reference_datas
        )
    except ValueError:
        additional_interactions = create_additional_interactions(
            product=product, party_key=party_key, additional_interactions_data=[]
        )
    return additional_interactions


def asid_equals(as_device: Device, asid: str) -> bool:
    (_asid,) = (k.key_value for k in as_device.keys)
    return _asid == asid


def read_or_create_as_device(
    device_repository: DeviceRepository,
    asid: str,
    party_key: str,
    product_team: ProductTeam,
    product: CpmProduct,
    message_sets: DeviceReferenceData,
    additional_interactions: DeviceReferenceData,
    accredited_system_device_data: QuestionnaireResponse,
    as_tags: list[dict],
) -> Device:
    devices = device_repository.search(
        product_team_id=product_team.id,
        product_id=product.id,
        environment=Environment.PROD,
    )
    try:
        as_devices = filter(is_as_device, devices)
        (as_device,) = filter(lambda d: asid_equals(d, asid), as_devices)
    except ValueError:
        as_device = create_as_device(
            product=product,
            party_key=party_key,
            asid=asid,
            as_device_data=accredited_system_device_data,
            message_sets_id=message_sets.id,
            additional_interactions_id=additional_interactions.id,
            as_tags=as_tags,
        )
    return as_device


def read_message_sets_from_mhs_device(
    mhs_device: Device,
    device_reference_data_repository: DeviceReferenceDataRepository,
) -> DeviceReferenceData:
    (message_sets_id,) = mhs_device.device_reference_data.keys()
    return device_reference_data_repository.read(
        product_team_id=mhs_device.product_team_id,
        product_id=mhs_device.product_id,
        id=message_sets_id,
        environment=Environment.PROD,
    )


def read_drds_from_as_device(
    as_device: Device,
    device_reference_data_repository: DeviceReferenceDataRepository,
) -> tuple[DeviceReferenceData, DeviceReferenceData]:
    # Relies on message sets drd being added first and additional interation drd id always being added second
    (message_sets_id, additional_interactions_id) = (
        as_device.device_reference_data.keys()
    )
    message_sets = device_reference_data_repository.read(
        product_team_id=as_device.product_team_id,
        product_id=as_device.product_id,
        id=message_sets_id,
        environment=Environment.PROD,
    )
    additional_interactions = device_reference_data_repository.read(
        product_team_id=as_device.product_team_id,
        product_id=as_device.product_id,
        id=additional_interactions_id,
        environment=Environment.PROD,
    )
    # Conditional to check the drds were returned in the expected order
    if message_sets.name.endswith(ADDITIONAL_INTERACTIONS_SUFFIX):
        message_sets, additional_interactions = additional_interactions, message_sets
    return message_sets, additional_interactions
