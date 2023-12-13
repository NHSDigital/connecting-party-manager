from typing import Literal

import pytest
from domain.fhir_translation.parse import create_fhir_model_from_fhir_json
from pydantic import BaseModel, Extra, StrictStr, ValidationError


class FhirModel(BaseModel):
    value: str


class AnotherFhirModel(BaseModel):
    value: Literal["hiya"]


class StrictFhirModel(BaseModel):
    value: StrictStr


class OurFhirModel(BaseModel, extra=Extra.forbid):
    value: Literal["hiya"]


def test_validate_our_model_raises_no_extra_fields():
    with pytest.raises(ValidationError) as exc:
        create_fhir_model_from_fhir_json(
            fhir_json={"value": "hiya", "something_else": "oops"},
            fhir_models=[FhirModel, StrictFhirModel],
            our_model=OurFhirModel,
        )
    assert exc.value.model is OurFhirModel


def test_validate_our_model_raises_error():
    with pytest.raises(ValidationError) as exc:
        create_fhir_model_from_fhir_json(
            fhir_json={"value": "not_hiya"},
            fhir_models=[FhirModel, StrictFhirModel],
            our_model=OurFhirModel,
        )
    assert exc.value.model is OurFhirModel


def test_validate_their_model_raises_error():
    with pytest.raises(ValidationError) as exc:
        create_fhir_model_from_fhir_json(
            fhir_json={"value": "not_hiya"},
            fhir_models=[AnotherFhirModel],
            our_model=StrictFhirModel,
        )
    assert exc.value.model is AnotherFhirModel
