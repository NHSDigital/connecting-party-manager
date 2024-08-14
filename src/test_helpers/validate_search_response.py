def validate_result_body(result_body, devices, params):
    if isinstance(devices, dict):  # Single device scenario
        devices = [devices]
    for index, result in enumerate(result_body):
        validate_device(result, devices[index])
        validate_keys(result["keys"], devices[index])
        validate_tags(result["tags"], params)
        validate_questionnaire_responses(result, devices[index], params)


def validate_device(result, device):
    assert result["status"] == "active"
    assert result["name"] == device["device_name"]


def validate_keys(keys, device):
    for key in keys:
        assert key["key_value"] == device["device_key"]


def validate_tags(tags, params):
    for tag in tags:
        for key, value in params.items():
            assert [key, value] in tag["components"]


def validate_questionnaire_responses(result, device, params):
    questionnaire_responses = result["questionnaire_responses"][
        f"spine_{device['device_name']}/1"
    ]
    iter_items = iter(questionnaire_responses.items())
    _, iter_value = next(iter_items)
    filter_count = 0
    for answer in iter_value["answers"]:
        filter_count += check_answer(answer, params)
    assert filter_count == len(params)


def check_answer(answer, params):
    count = 0
    for key, value in params.items():
        if key in answer:
            assert value in answer[key]
            count += 1
    return count
