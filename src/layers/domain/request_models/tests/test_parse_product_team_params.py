import pytest
from domain.request_models.v1 import CreateProductTeamIncomingParams
from pydantic import ValidationError

from test_helpers.sample_data import (
    CPM_PRODUCT_TEAM_EXTRA_PARAMS,
    CPM_PRODUCT_TEAM_ID,
    CPM_PRODUCT_TEAM_NO_ID,
)


def test_product_team():
    product_team = CreateProductTeamIncomingParams(**CPM_PRODUCT_TEAM_NO_ID)
    assert isinstance(product_team, CreateProductTeamIncomingParams)
    assert product_team.keys == CPM_PRODUCT_TEAM_NO_ID["keys"]
    assert product_team.ods_code == CPM_PRODUCT_TEAM_NO_ID["ods_code"]
    assert product_team.name == CPM_PRODUCT_TEAM_NO_ID["name"]


def test_product_team_with_id_raises_error():
    with pytest.raises(ValidationError) as exc:
        CreateProductTeamIncomingParams(**CPM_PRODUCT_TEAM_ID)

    assert exc.value.model is CreateProductTeamIncomingParams


def test_validate_product_team_raises_no_extra_fields():
    with pytest.raises(ValidationError) as exc:
        CreateProductTeamIncomingParams(**CPM_PRODUCT_TEAM_EXTRA_PARAMS)

    assert exc.value.model is CreateProductTeamIncomingParams