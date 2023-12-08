from typing import TypeVar

from pydantic import BaseModel

fhir_type = TypeVar("fhir_type")


def create_fhir_model_from_fhir_json(
    fhir_json: dict, fhir_models: list[type[BaseModel]], our_model: type[fhir_type]
) -> fhir_type:
    # Validate and parse against out ruleset
    fhir_model = our_model(**fhir_json)
    # Validate against the FHIR ruleset
    for _fhir_model in fhir_models:
        _fhir_model(**fhir_json)
    return fhir_model
