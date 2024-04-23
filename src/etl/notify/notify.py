def handler(event: list[dict], context=None):
    for item in event:
        if item.get("error_message") is not None:
            return "fail"
    return "pass"
