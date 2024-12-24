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
from sds.epr.constants import EprNameTemplate
from sds.epr.creators import (
    create_epr_product,
    create_epr_product_team,
    create_message_sets,
    create_mhs_device,
)
from sds.epr.utils import (
    is_additional_interactions_device_reference_data,
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
    device_reference_data_repository: DeviceReferenceDataRepository, product: CpmProduct
) -> DeviceReferenceData | None:
    device_reference_datas = device_reference_data_repository.search(
        product_team_id=product.product_team_id,
        product_id=product.id,
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
