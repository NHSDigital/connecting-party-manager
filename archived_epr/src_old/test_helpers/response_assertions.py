def _assert_key_value(key, value, result, check_body, check_content_length):
    if (
        (key == "Content-Length" and check_content_length)
        or (key == "body" and check_body)
        or key not in {"Content-Length", "body"}
    ):
        assert result[key] == value


def _response_assertions(
    result, expected, check_body=False, check_content_length=False
):
    for key, value in expected.items():
        assert key in result
        if isinstance(value, dict):
            _response_assertions(result=result.get(key, {}), expected=value)
        elif key != "headers":
            _assert_key_value(key, value, result, check_body, check_content_length)
