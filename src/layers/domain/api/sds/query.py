from functools import cache
from itertools import chain, combinations
from typing import Optional

from pydantic import BaseModel, Extra, ValidationError, root_validator


class SearchSDSQueryParams(BaseModel):
    def get_non_null_params(self):
        return self.dict(exclude_none=True)

    @classmethod
    @cache
    def allowed_field_combinations(cls) -> list[tuple[str]]:
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
            (*mandatory_fields, *_optional_field_combination)
            for _optional_field_combination in optional_field_combinations
        ]


class SearchSDSDeviceQueryParams(SearchSDSQueryParams, extra=Extra.forbid):
    nhs_as_client: str
    nhs_as_svc_ia: str
    nhs_mhs_manufacturer_org: Optional[str] = None
    nhs_mhs_party_key: Optional[str] = None


class SearchSDSEndpointQueryParams(SearchSDSQueryParams, extra=Extra.forbid):
    nhs_id_code: Optional[str] = None
    nhs_mhs_svc_ia: Optional[str] = None
    nhs_mhs_party_key: Optional[str] = None

    @root_validator
    def check_filters(cls, values):
        count = 2
        non_empty_count = sum(
            1 for value in values.values() if value is not None and value != 0
        )
        if non_empty_count < count:
            raise ValidationError(
                "At least 2 query parameters should be provided of type, nhs_id_code, nhs_mhs_svc_ia and nhs_mhs_party_key"
            )
        return values
