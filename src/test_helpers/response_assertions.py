def _response_assertions(
    result, expected, check_body=False, check_content_length=False
):
    for key, value in expected.items():
        assert key in result
        if isinstance(value, dict):
            _response_assertions(result=result.get(key, {}), expected=value)
        if key != "Location" and key != "headers":
            if key != "Content-Length" and key != "body":
                assert result[key] == value
            else:
                if key == "Content-Length" and check_content_length:
                    assert result[key] == value
                if key == "body" and check_body:
                    assert result[key] == value
