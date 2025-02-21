import re

import pytest
from domain.core.product_team_epr import ProductTeam, ProductTeamCreatedEvent
from domain.core.root import Root
from domain.request_models import CreateProductTeamIncomingParams
from pydantic import ValidationError


@pytest.mark.parametrize(
    "keys,name",
    [
        [
            [
                {
                    "key_type": "product_team_id_alias",
                    "key_value": "ae28e872-843d-4e2e-9f0b-b5d3c42d441f",
                }
            ],
            " ",
        ],
    ],
)
def test__create_product_team_bad_name(keys: list, name: str):
    org = Root.create_ods_organisation(ods_code="AB123")

    with pytest.raises(ValidationError):
        org.create_product_team_epr(name=name, keys=keys)


@pytest.mark.parametrize(
    "keys,name",
    [
        [
            [
                {
                    "key_type": "product_team_id",
                    "key_value": "ae28e872-843d-4e2e-9f0b-b5d3c42d441f",
                }
            ],
            "FOOBAR",
        ],
    ],
)
def test__create_product_team_bad_key_type(keys: list, name: str):
    org = Root.create_ods_organisation(ods_code="AB123")

    with pytest.raises(ValidationError):
        org.create_product_team_epr(name=name, keys=keys)


@pytest.mark.parametrize(
    "keys,name,ods_code",
    [
        [
            [
                {
                    "key_type": "product_team_id_alias",
                    "key_value": "ae28e872-843d-4e2e-9f0b-b5d3c42d441f",
                }
            ],
            "First",
            "AB123",
        ],
        [
            [
                {
                    "key_type": "product_team_id_alias",
                    "key_value": "edf90c3a-f865-4dd9-9ab9-400e6ebc02e0",
                }
            ],
            "Second",
            "AB123",
        ],
        [
            [
                {
                    "key_type": "product_team_id_alias",
                    "key_value": "f9518c12-6c83-4544-97db-d9dd1d64da97",
                }
            ],
            "Third",
            "AB123",
        ],
        [
            [{"key_type": "product_team_id_alias", "key_value": "foobar"}],
            "Fourth",
            "AB123",
        ],
    ],
)
def test__create_product_team(
    keys: list,
    name: str,
    ods_code: str,
):
    product_team = ProductTeam(name=name, ods_code=ods_code, keys=keys)
    generated_id = product_team.id
    assert isinstance(product_team, ProductTeam)
    assert re.match(rf"{ods_code}\.[0-9a-fA-F-]{{36}}", generated_id)
    assert product_team.keys == keys
    assert product_team.name == name
    assert product_team.ods_code == ods_code


@pytest.mark.parametrize(
    "id,keys,name,ods_code",
    [
        [
            None,
            [
                {
                    "key_type": "product_team_id_alias",
                    "key_value": "ae28e872-843d-4e2e-9f0b-b5d3c42d441f",
                }
            ],
            "First",
            "AB123",
        ],
        [
            None,
            [
                {
                    "key_type": "product_team_id_alias",
                    "key_value": "edf90c3a-f865-4dd9-9ab9-400e6ebc02e0",
                }
            ],
            "Second",
            "AB123",
        ],
        [
            None,
            [
                {
                    "key_type": "product_team_id_alias",
                    "key_value": "f9518c12-6c83-4544-97db-d9dd1d64da97",
                }
            ],
            "Third",
            "AB123",
        ],
        [
            None,
            [{"key_type": "product_team_id_alias", "key_value": "foobar"}],
            "Fourth",
            "AB123",
        ],
    ],
)
def test__create_product_team_provided_id_equals_none_is_ignored(
    id: str,
    keys: list,
    name: str,
    ods_code: str,
):
    product_team = ProductTeam(id=id, name=name, ods_code=ods_code, keys=keys)
    generated_id = product_team.id
    assert isinstance(product_team, ProductTeam)
    assert re.match(rf"{ods_code}\.[0-9a-fA-F-]{{36}}", generated_id)
    assert product_team.keys == keys
    assert product_team.name == name
    assert product_team.ods_code == ods_code


@pytest.mark.parametrize(
    "keys,name",
    [
        [
            [
                {
                    "key_type": "product_team_id_alias",
                    "key_value": "ae28e872-843d-4e2e-9f0b-b5d3c42d441f",
                }
            ],
            "First",
        ],
        [
            [
                {
                    "key_type": "product_team_id_alias",
                    "key_value": "edf90c3a-f865-4dd9-9ab9-400e6ebc02e0",
                }
            ],
            "Second",
        ],
        [
            [
                {
                    "key_type": "product_team_id_alias",
                    "key_value": "f9518c12-6c83-4544-97db-d9dd1d64da97",
                }
            ],
            "Third",
        ],
        [[{"key_type": "product_team_id_alias", "key_value": "foobar"}], "Fourth"],
    ],
)
def test__create_product_team_from_org_no_id(
    keys: str,
    name: str,
):
    org = Root.create_ods_organisation(ods_code="AB123")

    result = org.create_product_team_epr(keys=keys, name=name)
    event = result.events[0]

    assert isinstance(result, ProductTeam)
    generated_id = result.id
    assert re.match(rf"{org.ods_code}\.[0-9a-fA-F-]{{36}}", generated_id)
    assert result.keys == keys
    assert result.name == name
    assert result.ods_code == org.ods_code

    generated_id = event.id
    assert len(result.events) == 1
    assert isinstance(event, ProductTeamCreatedEvent)
    assert re.match(rf"{org.ods_code}\.[0-9a-fA-F-]{{36}}", generated_id)
    assert event.keys == keys
    assert event.name == name
    assert event.ods_code == org.ods_code


@pytest.mark.parametrize(
    "id,keys,name",
    [
        [
            None,
            [
                {
                    "key_type": "product_team_id_alias",
                    "key_value": "ae28e872-843d-4e2e-9f0b-b5d3c42d441f",
                }
            ],
            "First",
        ],
        [
            "FOOBAR",
            [
                {
                    "key_type": "product_team_id_alias",
                    "key_value": "edf90c3a-f865-4dd9-9ab9-400e6ebc02e0",
                }
            ],
            "Second",
        ],
    ],
)
def test__create_product_team_from_org_id_raises_error(
    id: str,
    keys: str,
    name: str,
):
    org = Root.create_ods_organisation(ods_code="AB123")

    with pytest.raises(TypeError):
        org.create_product_team_epr(id=id, name=name, keys=keys)


@pytest.mark.parametrize(
    "params",
    [
        {
            "keys": [
                {
                    "key_type": "product_team_id_alias",
                    "key_value": "edf90c3a-f865-4dd9-9ab9-400e6ebc02e0",
                }
            ],
            "ods_code": "AB123",
            "name": "FooBar",
        },
    ],
)
def test__create_product_team_with_incoming_params(
    params: dict,
):
    incoming_params = CreateProductTeamIncomingParams(**params)
    org = Root.create_ods_organisation(incoming_params.ods_code)

    result = org.create_product_team_epr(**incoming_params.dict(exclude={"ods_code"}))
    event = result.events[0]

    assert isinstance(result, ProductTeam)
    assert len(result.events) == 1
    assert isinstance(event, ProductTeamCreatedEvent)

    result_generated_id = result.id
    event_generated_id = event.id
    assert re.match(rf"{params["ods_code"]}\.[0-9a-fA-F-]{{36}}", result_generated_id)
    assert re.match(rf"{params["ods_code"]}\.[0-9a-fA-F-]{{36}}", event_generated_id)

    assert result.keys == params["keys"]
    assert result.name == params["name"]
    assert result.ods_code == org.ods_code

    assert event.keys == params["keys"]
    assert event.name == params["name"]
    assert event.ods_code == org.ods_code
