from pydantic import BaseModel


def create_fhir_model_from_fhir_json[
    FhirType
](
    fhir_json: dict, fhir_models: list[type[BaseModel]], our_model: type[FhirType]
) -> FhirType:
    # Validate and parse against out ruleset
    fhir_model = our_model(**fhir_json)
    # Validate against the FHIR ruleset
    for _fhir_model in fhir_models:
        _fhir_model(**fhir_json)
    return fhir_model
