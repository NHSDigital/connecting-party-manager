from functools import cache
from itertools import chain, combinations

from pydantic import BaseModel, Extra, root_validator


class SearchSDSQueryParams(BaseModel):
    def get_non_null_params(self):
        return self.dict(exclude_none=True)

    @classmethod
    @cache
    def allowed_field_combinations(cls) -> list[set[str]]:
        """
        This method is used to generate all allowed combinations of search fields
        for the given query parameters. Down the line this also used to generate
        Device.tags in the ETL
        """
        mandatory_fields, optional_fields = [], []
        for field_name, field in cls.__fields__.items():
            if field.required:
                mandatory_fields.append(field_name)
            else:
                optional_fields.append(field_name)

        n_minimum_optional_fields = 0 if mandatory_fields else 1
        n_optional_fields = len(optional_fields)
        optional_field_combinations = chain.from_iterable(
            combinations(optional_fields, n_fields)
            for n_fields in range(n_minimum_optional_fields, n_optional_fields + 1)
        )

        return [
            {*mandatory_fields, *_optional_field_combination}
            for _optional_field_combination in optional_field_combinations
        ]


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
