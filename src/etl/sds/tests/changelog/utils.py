from collections import deque
from pathlib import Path
from typing import Any, Generator, Literal, Protocol

from domain.core.enum import Environment
from domain.repository.cpm_product_repository.v1 import CpmProduct, CpmProductRepository
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceData,
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository.v1 import Device, DeviceRepository
from domain.repository.product_team_repository.v1 import (
    ProductTeam,
    ProductTeamRepository,
)
from event.json import json_load
from mypy_boto3_dynamodb import DynamoDBClient
from pydantic import ValidationError

PATH_TO_HERE = Path(__file__).parent / "changelog_components"


def read_ldif(relative_path: str):
    with open(PATH_TO_HERE / relative_path) as f:
        return f.read().strip("\n")


def create_modify_ldif(
    *relative_paths: str,
    device_type: Literal["accredited_system", "message_handling_system"],
):
    with open(PATH_TO_HERE / "modify" / device_type / "base.ldif") as f:
        base = f.read()

    components = list(
        map(lambda path: read_ldif(f"modify/{device_type}/{path}"), relative_paths)
    )
    return base.replace("<<TEMPLATE>>", "\n-\n".join(components))


class Handler(Protocol):
    def __call__(self, event, context) -> dict[str, any]: ...


class Scenario(Protocol):
    @property
    def extract_input(self) -> str: ...

    @property
    def database_initial_state(self) -> str: ...

    @property
    def extract_output(self) -> str: ...

    @property
    def transform_output(self) -> str: ...

    @property
    def load_output(self) -> str: ...

    @property
    def expected_errors(self) -> list[str]: ...


class _Scenario:
    def __init__(self, file_path: str, extract_input: list[str]):
        self.root = Path(file_path).parent
        self.name = self.root.name
        self.extract_input = "\n\n".join(extract_input)

    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if name == "expected_errors":
                expected_errors = []
                error_files = filter(
                    lambda path: path.suffix == ".error", self.root.iterdir()
                )
                for path in error_files:
                    with open(file=path) as f:
                        expected_errors.append(f.read())
                return expected_errors
            else:
                with open(self.root / f"{name}.json") as f:
                    return json_load(f)


obj_likes = (list, set, deque, tuple, dict)


def convert_list_likes(obj):
    if isinstance(obj, (list, set, deque, tuple)):
        _list = list if any(isinstance(item, obj_likes) for item in obj) else sorted
        _obj = _list(map(convert_list_likes, obj))
    elif isinstance(obj, dict):
        _obj = {k: convert_list_likes(v) for k, v in obj.items()}
    else:
        _obj = obj
    return _obj


def as_domain_object(
    obj: dict,
) -> ProductTeam | CpmProduct | Device | DeviceReferenceData:
    errors = []
    for model in (ProductTeam, CpmProduct, Device, DeviceReferenceData):
        try:
            instance = model(**obj)
            if instance.state().keys() == obj.keys():
                return instance
        except ValidationError as e:
            errors.append(str(e))
    msg = "\n\n".join(errors)
    raise ValueError(f"Could not find a model for {obj}. Tried the following:\n{msg}")


def read_all(
    table_name: str, db_client: "DynamoDBClient"
) -> Generator[ProductTeam | CpmProduct | Device | DeviceReferenceData, None, None]:
    product_team_repo = ProductTeamRepository(table_name, db_client)
    product_repo = CpmProductRepository(table_name, db_client)
    device_repo = DeviceRepository(table_name, db_client)
    drd_repo = DeviceReferenceDataRepository(table_name, db_client)

    for product_team in product_team_repo.search():
        yield product_team
        for product in product_repo.search(product_team_id=product_team.id):
            yield product
            yield from device_repo.search(
                product_team_id=product_team.id,
                product_id=product.id,
                environment=Environment.PROD,
            )
            yield from drd_repo.search(
                product_team_id=product_team.id,
                product_id=product.id,
                environment=Environment.PROD,
            )


ADD_ACCREDITED_SYSTEM = read_ldif("add/accredited_system.ldif")
ADD_ANOTHER_ACCREDITED_SYSTEM_IN_SAME_PRODUCT = read_ldif(
    "add/accredited_system.SameProduct.ldif"
)
ADD_ANOTHER_ACCREDITED_SYSTEM_IN_SAME_PRODUCT_TEAM = read_ldif(
    "add/accredited_system.SameProductTeam.DifferentProduct.ldif"
)
ADD_ACCREDITED_SYSTEM_IN_SAME_PRODUCT_AS_MHS = read_ldif(
    "add/accredited_system.SameProductAsMhs.ldif"
)
DELETE_ACCREDITED_SYSTEM = read_ldif("delete/accredited_system.ldif")
ADD_MESSAGE_HANDLING_SYSTEM = read_ldif("add/message_handling_system.ldif")
DELETE_MESSAGE_HANDLING_SYSTEM = read_ldif("delete/message_handling_system.ldif")
DELETE_UNKNOWN_ENTITY = read_ldif("delete/unknown_entity.ldif")
MODIFY_UNKNOWN_ENTITY = read_ldif("modify/unknown_entity.ldif")

ADD_ANOTHER_MESSAGE_HANDLING_SYSTEM = read_ldif(
    "add/message_handling_system.AnotherWithDifferentUniqueIdentifier.ldif"
)
ADD_ANOTHER_MESSAGE_HANDLING_SYSTEM_WITH_SAME_UNIQUE_IDENTIFIER = read_ldif(
    "add/message_handling_system.AnotherWithSameUniqueIdentifier.ldif"
)
ADD_ANOTHER_MESSAGE_HANDLING_SYSTEM_IN_SAME_PRODUCT = read_ldif(
    "add/message_handling_system.SameProduct.ldif"
)
ADD_ANOTHER_MESSAGE_HANDLING_SYSTEM_IN_SAME_PRODUCT_TEAM = read_ldif(
    "add/message_handling_system.SameProductTeam.DifferentProduct.ldif"
)
