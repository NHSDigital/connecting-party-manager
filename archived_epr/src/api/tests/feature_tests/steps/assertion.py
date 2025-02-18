import json

IGNORE = "<< ignore >>"


def error_message(*args, label=""):
    if label:
        label = (label,)
    return "\n".join(map(stringify, ("", *label, *args, "")))


def should_ignore(expected, received, key, expected_value):
    if expected_value == IGNORE:
        expected.pop(key)
        received.pop(key, None)
        return True
    return False


def handle_dict_values(expected_value, received_value):
    if isinstance(expected_value, dict) and isinstance(received_value, dict):
        _pop_ignore(expected=expected_value, received=received_value)


def handle_list_values(expected_value, received_value):
    if isinstance(expected_value, list) and isinstance(received_value, list):
        for a, b in zip(received_value, expected_value):
            if isinstance(a, dict) and isinstance(b, dict):
                _pop_ignore(expected=b, received=a)


def _pop_ignore(expected: dict, received: dict):
    """If any of expected's values are IGNORE, remove them from both."""

    for key in list(expected):
        expected_value = expected[key]

        if should_ignore(expected, received, key, expected_value):
            continue

        if isinstance(received, dict):
            received_value = received.get(key)

            handle_dict_values(expected_value, received_value)

            handle_list_values(expected_value, received_value)


def _fix_backslashes(json_data: dict):
    if "errors" in json_data and isinstance(json_data["errors"], list):
        for error in json_data["errors"]:
            if "message" in error and isinstance(error["message"], str):
                error["message"] = error["message"].replace("\\\\", "\\")


def stringify(item) -> str:
    if isinstance(item, (list, dict)):
        return json.dumps(item)
    return str(item)


def assert_same_type(expected, received, label=""):
    assert type(expected) is type(received), error_message(
        type(expected).__name__,
        "is different from",
        type(received).__name__,
        label=label,
    )


def assert_equal(expected, received, label=""):
    if isinstance(expected, dict):
        _fix_backslashes(json_data=expected)
        _pop_ignore(expected=expected, received=received)
    if isinstance(expected, list):
        handle_list_values(expected_value=expected, received_value=received)
    assert expected == received, error_message(
        expected, "does not equal", received, label=label
    )


def assert_many(assertions, expected, received):
    if not (len(expected) == len(received) == len(assertions)):
        raise ValueError(
            "Bad test setup: assertions, expected, received do not have equal length"
        )

    exceptions = []
    for _expected, _received, assertion in zip(expected, received, assertions):
        try:
            assertion(expected=_expected, received=_received)
        except AssertionError as exception:
            exceptions.append(exception)
    if exceptions:
        raise ExceptionGroup("Feature test errors:", exceptions)


def assert_same_length(expected, received, label=""):
    assert len(expected) == len(received), error_message(
        expected, "has a different number of items from", received, label=label
    )


def assert_is_subset(expected: dict, received: dict, path=None):
    """
    Asymmetric assertion that the values of all paths in 'expected'
    are equal to those in 'received'
    """
    if path is None:
        path = [""]

    for key, expected_value in expected.items():

        # Sometimes AWS remaps keys, but not consistently
        amzn_remapped_key = f"x-amzn-Remapped-{key}"
        if key not in received and amzn_remapped_key in received:
            key = amzn_remapped_key

        # Key must exist
        assert key in received, error_message("Could not find key", key, "in", received)

        # Values must be of the same type
        received_value = received[key]
        assert_same_type(
            expected=expected_value, received=received_value, label=f"{'.'.join(path)}:"
        )

        # Recurse if dict
        if isinstance(expected_value, dict):
            assert_is_subset(
                expected=expected_value, received=received_value, path=path + [key]
            )
        # Iterate if list of dict
        elif (
            expected_value
            and isinstance(expected_value, list)
            and all(isinstance(item, dict) for item in expected_value)
        ):
            for idx, (expected_item, received_item) in enumerate(
                zip(expected_value, received_value)
            ):
                assert_is_subset(
                    expected=expected_item,
                    received=received_item,
                    path=path + [key, str(idx)],
                )
        # Otherwise values must be equal
        else:
            assert_equal(
                expected=expected_value,
                received=received_value,
                label=f"{'.'.join(path+[key])}:",
            )
