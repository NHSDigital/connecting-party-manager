from itertools import product
from typing import Iterable

from domain.api.sds.query import SearchSDSQueryParams
from domain.core.device.v2 import Device, DeviceTag
from sds.cpm_translation.constants import UNIQUE_IDENTIFIER


def update_in_list_of_dict(obj: list[dict[str, str]], key, value: list):
    found = False
    items_to_remove = []
    for idx, item in enumerate(obj):
        if key not in item:
            continue
        found = True
        # Replace the value, if it is truthy
        del item[key]
        if value:
            item[key] = value
        # If the item is now empty, mark it for removal
        if not item:
            items_to_remove.append(idx)

    # If the key was never found, create a new item
    if value and not found:
        obj.append({key: value})

    # Create a new list from non-marked items
    for idx in sorted(items_to_remove, reverse=True):
        del obj[idx]


def get_in_list_of_dict(obj: list[dict[str, str]], key):
    return next((item[key] for item in obj if key in item), None)


def _cross_product(matrix: list[list[dict]]) -> list[dict]:
    """
    For a outer-list of inner-list of items, returns every
    combination of containing one item per inner-list, for example:
    (NB: integers used for illustrative purposes)

        [1, 2, 3]
        [4, 5]

    would yield

        [1, 4], [1, 5], [2, 4], [2, 5], [3, 4], [3, 5]
    """
    return [
        dict({k: v for d in combo for k, v in d.items()}) for combo in product(*matrix)
    ]


def _sds_metadata_to_device_tags(
    data: dict[str, str | Iterable], tag_fields: list
) -> list[dict]:
    tag_components_multi = []
    tag_components_flat = {}
    for field in tag_fields:
        value = data.get(field, None)
        if not value:
            return []
        if isinstance(value, Iterable) and not isinstance(value, str):
            tag_components_multi.append([{field: v} for v in value])
        else:
            tag_components_flat[field] = value

    return [
        {**tag_components_flat, **combo}
        for combo in _cross_product(tag_components_multi)
    ]


def sds_metadata_to_device_tags(
    data: dict[str, str | Iterable], model: SearchSDSQueryParams
):
    tags = []
    for tag_fields in model.allowed_field_combinations():
        tags += _sds_metadata_to_device_tags(data=data, tag_fields=tag_fields)
    tags += _sds_metadata_to_device_tags(data=data, tag_fields=[UNIQUE_IDENTIFIER])
    return tags


def set_device_tags(
    device: Device, data: dict[str, str | Iterable], model: SearchSDSQueryParams
):
    tags = sds_metadata_to_device_tags(data=data, model=model)
    device.add_tags(tags=tags)


def set_device_tags_bulk(
    device: Device, data: dict[str, str | Iterable], model: SearchSDSQueryParams
):
    """
    Optimisation over `set_device_tags`:

    Avoids using the domain method Device.add_tags as no need to check for
    tag consistency in bulk operations.
    """
    tags = sds_metadata_to_device_tags(data=data, model=model)
    device.tags = [DeviceTag(**tag) for tag in tags]
