from event.json import json_loads

TABLE_NAME = "hiya"
ODS_CODE = "F5H1R"
PRODUCT_TEAM_ID = "F5H1R.641be376-3954-4339-822c-54071c9ff1a0"
PRODUCT_TEAM_NAME = "product-team-name"
PRODUCT_ID = "P.XXX-YYY"
PRODUCT_NAME = "cpm-product-name"
PRODUCT_TEAM_KEYS = [{"key_type": "product_team_id_alias", "key_value": "BAR"}]


def test_index():
    from api.readQuestionnaire.index import handler

    response = handler(
        event={
            "headers": {"version": "1"},
            "pathParameters": {"questionnaire_id": "spine_mhs"},
        }
    )
    assert response["statusCode"] == 200

    response_body: dict = json_loads(response["body"])
    json_schema: dict = response_body.pop("json_schema")
    assert response_body == {
        "name": "spine_mhs",
        "version": "1",
    }
    assert len(json_schema["properties"]) == 25


def test_index_no_such_questionnaire():
    from api.readQuestionnaire.index import handler

    response = handler(
        event={
            "headers": {"version": "1"},
            "pathParameters": {"questionnaire_id": "oops"},
        }
    )
    assert response["statusCode"] == 404

    response_body = json_loads(response["body"])
    assert response_body == {
        "errors": [
            {
                "code": "RESOURCE_NOT_FOUND",
                "message": "Could not find Questionnaire for key ('oops')",
            },
        ],
    }
