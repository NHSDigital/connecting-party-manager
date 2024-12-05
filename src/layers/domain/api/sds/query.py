from pydantic import BaseModel, Extra, root_validator


class SearchSDSDeviceQueryParams(BaseModel, extra=Extra.forbid):
    nhs_id_code: str
    nhs_as_svc_ia: str
    nhs_mhs_manufacturer_org: str = None
    nhs_mhs_party_key: str = None

    @root_validator(pre=True)
    def client_to_id(cls, values: dict):
        nhs_as_client = values.pop("nhs_as_client", None)
        nhs_id_code = values.get("nhs_id_code")
        if nhs_as_client and not nhs_id_code:
            values["nhs_id_code"] = nhs_as_client
        return values

    def get_non_null_params(self):
        return self.dict(exclude_none=True)

    @classmethod
    def allowed_field_combinations(cls) -> list[set[str]]:
        return [
            {"nhs_id_code", "nhs_as_svc_ia"},
            {"nhs_id_code", "nhs_as_svc_ia", "nhs_mhs_party_key"},
        ]


class SearchSDSEndpointQueryParams(BaseModel, extra=Extra.forbid):
    nhs_id_code: str = None
    nhs_mhs_svc_ia: str = None
    nhs_mhs_party_key: str = None

    @root_validator
    def check_filters(cls, values: dict):
        count = 2
        non_empty_count = sum(
            1 for value in values.values() if value is not None and value != 0
        )
        if non_empty_count < count:
            raise ValueError(
                "At least 2 query parameters should be provided of type, nhs_id_code, nhs_mhs_svc_ia and nhs_mhs_party_key"
            )
        return values

    def get_non_null_params(self):
        return self.dict(exclude_none=True)
