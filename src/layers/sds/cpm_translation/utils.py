def update_in_list_of_dict(obj: list[dict[str, str]], key, value):
    for item in obj:
        if key in item:
            if not value:
                item.pop(key)
            else:
                item[key] = value
            return
    obj.append({key: value})


def get_in_list_of_dict(obj: list[dict[str, str]], key):
    for item in obj:
        value = item.get(key)
        if value is not None:
            return value
    return None
