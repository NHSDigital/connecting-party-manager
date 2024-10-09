def validate_result_body(result_body, devices, params):
    if isinstance(devices, dict):  # Single device scenario
        devices = [devices]
    for index, result in enumerate(result_body):
        validate_device(result, devices[index])
        validate_keys(result["keys"], devices[index])
        validate_tags(result["tags"])
        validate_questionnaire_responses(result, devices[index], params)


def validate_device(result, device):
    assert result["status"] == "active"
    assert result["name"] == device["device_name"]


def validate_keys(keys, device):
    for key in keys:
        assert key["key_value"] == device["device_key"]


def validate_tags(tags):
    assert tags == []  # The tags field is dropped due to being chunky


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


def validate_product_result_body(result_body, products):
    if isinstance(products, dict):  # single product
        products = [products]
    assert sorted(result_body, key=lambda d: d["id"]) == sorted(
        products, key=lambda d: d["id"]
    )
