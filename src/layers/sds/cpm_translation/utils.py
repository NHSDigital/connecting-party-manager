from collections import ChainMap
from itertools import product


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
    for item in obj:
        value = item.get(key)
        if value is not None:
            return value
    return None


def questionnaire_response_answers_to_device_tags(answers, tag_fields):
    tag_components = []
    for field in tag_fields:
        value = get_in_list_of_dict(obj=answers, key=field)
        if not value:
            return []
        tag_components.append([{field: v} for v in value])

    return [
        dict(ChainMap(*_tag_components)) for _tag_components in product(*tag_components)
    ]
