"""
tldr;
We generate every possible tag (i.e. matching query) that can be
made against the provided data.

Background:

1. SDS models have fields that are either a list of values, or a single value;
2. SDS FHIR API (which CPM must support) needs to be able search for Devices
   by combinations of query parameters;
3. SDS FHIR API queries are against any value in a list, or a single value;
4. "tags" are our solution for creating indexed Devices that are searchable
   against every allowed combination of searchable fields.
"""

from collections.abc import Iterable
from itertools import product

from domain.api.sds.query import SearchSDSQueryParams


def _valid_tag_exists(tag_fields: set[str], data_fields: Iterable[str]) -> bool:
    return tag_fields.issubset(data_fields)


def is_list_like(value):
    return isinstance(value, Iterable) and not isinstance(value, str)


def _generate_all_matching_queries(
    data_to_query: dict[str, str | Iterable]
) -> list[tuple[tuple[str, str]]]:
    """
    Generate one dictionary for each combination of key-value pairs
    in the data_to_query (including one for each value in a multivalue field)
    """
    multi_value_key_values, single_value_key_values = [], []
    for field, value in data_to_query.items():
        if is_list_like(value):
            multi_value_key_values.append([(field, v) for v in value])
        else:
            single_value_key_values.append((field, value))

    return [
        (*single_value_key_values, *combo) for combo in product(*multi_value_key_values)
    ]


def sds_metadata_to_device_tags(
    data: dict[str, str | Iterable], model: SearchSDSQueryParams
) -> list[tuple[tuple[str, str]]]:
    """
    tldr;
    We generate every possible tag (i.e. matching query) that can be
    made against the provided data.

    Background:

    1. SDS models have fields that are either a list of values, or a single value;
    2. SDS FHIR API (which CPM must support) needs to be able search for Devices
       by combinations of query parameters;
    3. SDS FHIR API queries are against any value in a list, or a single value;
    4. "tags" are our solution for creating indexed Devices that are searchable
       against every allowed combination of searchable fields.
    """
    tags = []
    for tag_fields in model.allowed_field_combinations():
        if not _valid_tag_exists(tag_fields=tag_fields, data_fields=data.keys()):
            continue
        data_to_query = {k: v for k, v in data.items() if k in tag_fields}
        tags += _generate_all_matching_queries(data_to_query=data_to_query)
    return tags
