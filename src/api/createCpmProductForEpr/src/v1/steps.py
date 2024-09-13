from types import FunctionType

from domain.api.common_steps.create_product import (
    after_steps,
    before_steps,
    create_cpm_product,
    read_product_team,
)
from domain.core.cpm_product import CpmProduct
from domain.core.cpm_system_id.v1 import PartyKeyId
from domain.core.product_key.v1 import ProductKeyType
from domain.core.product_team.v3 import ProductTeam
from domain.repository.cpm_system_id_repository import CpmSystemIdRepository


def get_latest_party_key(data, cache) -> PartyKeyId:
    party_key_repo = CpmSystemIdRepository[PartyKeyId](
        table_name=cache["DYNAMODB_TABLE"],
        dynamodb_client=cache["DYNAMODB_CLIENT"],
        model=PartyKeyId,
    )
    return party_key_repo.read()


def generate_party_key(data, cache) -> str:
    party_key: PartyKeyId = data[get_latest_party_key]
    product_team: ProductTeam = data[read_product_team]
    return PartyKeyId.create(
        current_number=party_key.latest_number, ods_code=product_team.ods_code
    )


def add_party_key_to_product(
    data: dict[FunctionType, CpmProduct | PartyKeyId], cache
) -> str:
    product: CpmProduct = data[create_cpm_product]
    party_key: PartyKeyId = data[generate_party_key]
    product.add_key(key_type=ProductKeyType.PARTY_KEY, key_value=party_key.id)


def write_party_key(data: dict[FunctionType, CpmProduct | PartyKeyId], cache) -> str:
    party_key_repo = CpmSystemIdRepository[PartyKeyId](
        table_name=cache["DYNAMODB_TABLE"],
        dynamodb_client=cache["DYNAMODB_CLIENT"],
        model=PartyKeyId,
    )
    party_key: PartyKeyId = data[generate_party_key]
    return party_key_repo.create_or_update(party_key)


steps = [
    *before_steps,
    get_latest_party_key,
    generate_party_key,
    add_party_key_to_product,
    write_party_key,
    *after_steps,
]
