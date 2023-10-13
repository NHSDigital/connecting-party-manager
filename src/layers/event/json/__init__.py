import json

from .errors import DuplicateKeyError


def dict_raise_on_duplicates(list_of_pairs):
    checked_pairs = {}
    for k, v in list_of_pairs:
        if k in checked_pairs:
            raise DuplicateKeyError("Duplicate key: %r" % (k,))
        checked_pairs[k] = v
    return checked_pairs


def json_loads(json_string):
    return json.loads(json_string, object_pairs_hook=dict_raise_on_duplicates)


def json_load(json_file_obj):
    return json.load(json_file_obj, object_pairs_hook=dict_raise_on_duplicates)
