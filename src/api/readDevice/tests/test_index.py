import json
import os
from unittest import mock

import pytest
from domain.core.device import Device
from domain.core.enum import Environment, Status
from domain.core.product_key import ProductKeyType
from domain.core.root import Root
from domain.repository.device_reference_data_repository import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository import DeviceRepository
from domain.repository.epr_product_repository import EprProductRepository
from domain.repository.product_team_epr_repository import ProductTeamRepository
from domain.repository.questionnaire_repository import (
    QuestionnaireInstance,
    QuestionnaireRepository,
)
from event.json import json_loads

from test_helpers.dynamodb import mock_table
from test_helpers.response_assertions import _response_assertions

TABLE_NAME = "hiya"
ODS_CODE = "F5H1R"
PRODUCT_TEAM_ID = "F5H1R.641be376-3954-4339-822c-54071c9ff1a0"
PRODUCT_TEAM_NAME = "product-team-name"
PRODUCT_ID = "P.XXX-YYY"
PRODUCT_NAME = "cpm-product-name"
PRODUCT_TEAM_KEYS = [{"key_type": "product_team_id_alias", "key_value": "BAR"}]
DEVICE_NAME = "device"
PARTY_KEY = "F5H1R-850000"


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index(version):
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team_epr(
        name=PRODUCT_TEAM_NAME, keys=PRODUCT_TEAM_KEYS
    )

    with mock_table(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        # Set up ProductTeam in DB
        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        # Set up Product in DB
        epr_product = product_team.create_epr_product(
            name=PRODUCT_NAME, product_id=PRODUCT_ID
        )
        product_repo = EprProductRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_repo.write(epr_product)

        # Set up Device in DB
        device = epr_product.create_device(
            name=DEVICE_NAME, environment=Environment.DEV
        )
        device_repo = DeviceRepository(table_name=TABLE_NAME, dynamodb_client=client)
        device_repo.write(device)

        from api.readDevice.index import handler

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {
                    "product_team_id": str(product_team.id),
                    "product_id": str(epr_product.id.id),
                    "environment": "dev",
                    "device_id": str(device.id),
                },
            }
        )

    response_body = json_loads(result["body"])

    # Assertions for fields that must exactly match
    assert response_body["id"] == str(device.id)
    assert response_body["product_id"] == str(epr_product.id)
    assert response_body["product_team_id"] == str(product_team.id)
    assert response_body["environment"] == Environment.DEV
    assert response_body["name"] == device.name
    assert response_body["ods_code"] == device.ods_code
    assert response_body["updated_on"] is None
    assert response_body["deleted_on"] is None

    # Assertions for fields that only need to be included
    assert "product_team_id" in response_body
    assert "created_on" in response_body

    expected_headers = {
        "Content-Type": "application/json",
        "Version": version,
    }

    # Check response headers
    assert result["statusCode"] == 200
    assert result["headers"]["Content-Length"] == str(len(result["body"]))
    for key, value in expected_headers.items():
        assert result["headers"][key] == value


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_mhs_device(version):
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team_epr(
        name=PRODUCT_TEAM_NAME, keys=PRODUCT_TEAM_KEYS
    )

    with mock_table(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        # Set up ProductTeam in DB
        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        # Set up EPR Product in DB
        epr_product = product_team.create_epr_product(
            name=PRODUCT_NAME, product_id=PRODUCT_ID
        )
        epr_product.add_key(key_type=ProductKeyType.PARTY_KEY, key_value=PARTY_KEY)
        product_repo = EprProductRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_repo.write(epr_product)

        # set up mhs message set questionnaire responses
        mhs_message_set_questionnaire = QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
        )
        questionnaire_response = mhs_message_set_questionnaire.validate(
            data={
                "MHS SN": "bar",
                "MHS IN": "baz",
                "Interaction ID": "bar:baz",
                "MHS CPA ID": f"{PARTY_KEY}:bar:baz",
                "Unique Identifier": f"{PARTY_KEY}:bar:baz",
            }
        )
        questionnaire_response_2 = mhs_message_set_questionnaire.validate(
            data={
                "MHS SN": "bar2",
                "MHS IN": "baz2",
                "Interaction ID": "bar2:baz2",
                "MHS CPA ID": f"{PARTY_KEY}:bar2:baz2",
                "Unique Identifier": f"{PARTY_KEY}:bar2:baz2",
            },
        )

        # Set up DeviceReferenceData in DB
        device_reference_data = epr_product.create_device_reference_data(
            name="ABC1234-987654 - MHS Message Set", environment=Environment.DEV
        )
        device_reference_data.add_questionnaire_response(questionnaire_response)
        device_reference_data.add_questionnaire_response(questionnaire_response_2)
        device_reference_data_repo = DeviceReferenceDataRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        device_reference_data_repo.write(device_reference_data)

        # Set up Device in DB
        device: Device = epr_product.create_device(
            name="Product-MHS", environment=Environment.DEV
        )
        device.add_key(key_type="cpa_id", key_value=f"{PARTY_KEY}:bar:baz")
        device.add_key(key_type="cpa_id", key_value=f"{PARTY_KEY}:bar2:baz2")
        device.add_tag(party_key=PARTY_KEY)

        # set up spine mhs questionnaire response
        mhs_message_set_questionnaire = QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_MHS
        )
        spine_mhs_questionnaire_response = mhs_message_set_questionnaire.validate(
            data={
                "Address": "https://example.com",
                "Managing Organization": "Example Org",
                "MHS Party Key": "party-key-001",
                "Approver URP": "approver-123",
                "Date Approved": "2024-01-01",
                "Date DNS Approved": "2024-01-02",
                "Date Requested": "2024-01-03",
                "DNS Approver": "dns-approver-456",
                "MHS FQDN": "mhs.example.com",
                "Requestor URP": "requestor-789",
                "MHS Manufacturer Organisation": "AAA",
            }
        )
        device.add_questionnaire_response(spine_mhs_questionnaire_response)

        device.add_device_reference_data_id(
            device_reference_data_id=str(device_reference_data.id), path_to_data=["*"]
        )

        device_repo = DeviceRepository(table_name=TABLE_NAME, dynamodb_client=client)
        device_repo.write(device)

        from api.readDevice.index import handler

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {
                    "product_team_id": str(product_team.id),
                    "product_id": str(epr_product.id.id),
                    "environment": "dev",
                    "device_id": str(device.id),
                },
            }
        )

    response_body = json_loads(result["body"])

    # Assertions for fields that must exactly match
    assert response_body["id"] == str(device.id)
    assert response_body["product_id"] == str(epr_product.id)
    assert response_body["product_team_id"] == str(product_team.id)
    assert response_body["environment"] == Environment.DEV
    assert response_body["name"] == device.name
    assert response_body["ods_code"] == device.ods_code
    assert response_body["status"] == Status.ACTIVE
    assert response_body["deleted_on"] is None
    assert response_body["keys"] is not None
    assert response_body["tags"] is not None
    assert response_body["device_reference_data"] is not None

    # Assertions for fields that only need to be included
    assert "created_on" in response_body
    assert "spine_mhs/1" in response_body["questionnaire_responses"]

    # Assert drd questionnaire responses have been added
    assert "spine_mhs_message_sets/1" in response_body["questionnaire_responses"]

    for resp in response_body["questionnaire_responses"]["spine_mhs_message_sets/1"]:
        assert "MHS SN" in resp["data"]
        assert "MHS IN" in resp["data"]
        assert "Interaction ID" in resp["data"]

    expected_headers = {
        "Content-Type": "application/json",
        "Version": version,
    }

    # Check response headers
    assert result["statusCode"] == 200
    assert result["headers"]["Content-Length"] == str(len(result["body"]))
    for key, value in expected_headers.items():
        assert result["headers"][key] == value


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_mhs_device_adjusted_data(version):
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team_epr(
        name=PRODUCT_TEAM_NAME, keys=PRODUCT_TEAM_KEYS
    )

    with mock_table(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        # Set up ProductTeam in DB
        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        # Set up EPR Product in DB
        epr_product = product_team.create_epr_product(
            name=PRODUCT_NAME, product_id=PRODUCT_ID
        )
        epr_product.add_key(key_type=ProductKeyType.PARTY_KEY, key_value="F5H1R-850000")
        product_repo = EprProductRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_repo.write(epr_product)

        # set up mhs message set questionnaire responses
        mhs_message_set_questionnaire = QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
        )
        questionnaire_response = mhs_message_set_questionnaire.validate(
            data={
                "Interaction ID": "bar:baz",
                "MHS SN": "bar",
                "MHS IN": "baz",
                "MHS CPA ID": f"{PARTY_KEY}:bar:baz",
                "Unique Identifier": f"{PARTY_KEY}:bar:baz",
            }
        )
        questionnaire_response_2 = mhs_message_set_questionnaire.validate(
            data={
                "Interaction ID": "bar2:baz2",
                "MHS SN": "bar2",
                "MHS IN": "baz2",
                "MHS CPA ID": f"{PARTY_KEY}:bar2:baz2",
                "Unique Identifier": f"{PARTY_KEY}:bar2:baz2",
            },
        )

        # Set up DeviceReferenceData in DB
        device_reference_data = epr_product.create_device_reference_data(
            name="ABC1234-987654 - MHS Message Set", environment=Environment.DEV
        )
        device_reference_data.add_questionnaire_response(questionnaire_response)
        device_reference_data.add_questionnaire_response(questionnaire_response_2)
        device_reference_data_repo = DeviceReferenceDataRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        device_reference_data_repo.write(device_reference_data)

        # Set up Device in DB
        device: Device = epr_product.create_device(
            name="Product-MHS", environment=Environment.DEV
        )
        device.add_key(key_type="cpa_id", key_value="F5H1R-850000:urn:foo")
        device.add_key(key_type="cpa_id", key_value="F5H1R-850000:urn:foo2")
        device.add_tag(party_key="f5h1r-850000")

        # set up spine mhs questionnaire response
        spine_mhs_questionnaire = QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_MHS
        )
        spine_mhs_questionnaire_response = spine_mhs_questionnaire.validate(
            data={
                "Address": "http://example.com",
                "Managing Organization": "Example Org",
                "MHS Party Key": "party-key-001",
                "Approver URP": "approver-123",
                "Date Approved": "2024-01-01",
                "Date DNS Approved": "2024-01-02",
                "Date Requested": "2024-01-03",
                "DNS Approver": "dns-approver-456",
                "MHS FQDN": "mhs.example.com",
                "Requestor URP": "requestor-789",
                "MHS Manufacturer Organisation": "AAA",
            }
        )

        device.add_questionnaire_response(spine_mhs_questionnaire_response)

        device.add_device_reference_data_id(
            device_reference_data_id=str(device_reference_data.id),
            path_to_data=["Interaction ID", "MHS IN"],
        )

        device_repo = DeviceRepository(table_name=TABLE_NAME, dynamodb_client=client)
        device_repo.write(device)

        from api.readDevice.index import handler

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {
                    "product_team_id": str(product_team.id),
                    "product_id": str(epr_product.id.id),
                    "environment": "dev",
                    "device_id": str(device.id),
                },
            }
        )

    response_body = json_loads(result["body"])

    # Assertions for fields that must exactly match
    assert response_body["id"] == str(device.id)
    assert response_body["product_id"] == str(epr_product.id)
    assert response_body["product_team_id"] == str(product_team.id)
    assert response_body["name"] == device.name
    assert response_body["ods_code"] == device.ods_code
    assert response_body["status"] == Status.ACTIVE
    assert response_body["deleted_on"] is None
    assert response_body["keys"] is not None
    assert response_body["tags"] is not None
    assert response_body["device_reference_data"] is not None

    # Assertions for fields that only need to be included
    assert "created_on" in response_body
    assert "spine_mhs/1" in response_body["questionnaire_responses"]

    # Assert drd questionnaire responses have been added
    assert "spine_mhs_message_sets/1" in response_body["questionnaire_responses"]

    for resp in response_body["questionnaire_responses"]["spine_mhs_message_sets/1"]:
        assert "MHS SN" not in resp["data"]
        assert "MHS IN" in resp["data"]
        assert "Interaction ID" in resp["data"]

    expected_headers = {
        "Content-Type": "application/json",
        "Version": version,
    }

    # Check response headers
    assert result["statusCode"] == 200
    assert result["headers"]["Content-Length"] == str(len(result["body"]))
    for key, value in expected_headers.items():
        assert result["headers"][key] == value


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_as_device(version):
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team_epr(
        name=PRODUCT_TEAM_NAME, keys=PRODUCT_TEAM_KEYS
    )

    with mock_table(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        # Set up ProductTeam in DB
        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        # Set up EPR Product in DB
        epr_product = product_team.create_epr_product(
            name=PRODUCT_NAME, product_id=PRODUCT_ID
        )
        epr_product.add_key(key_type=ProductKeyType.PARTY_KEY, key_value="F5H1R-850000")
        product_repo = EprProductRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_repo.write(epr_product)

        # set up mhs message set questionnaire responses
        mhs_message_set_questionnaire = QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
        )
        questionnaire_response = mhs_message_set_questionnaire.validate(
            data={
                "Interaction ID": "bar:baz",
                "MHS SN": "bar",
                "MHS IN": "baz",
                "MHS CPA ID": f"{PARTY_KEY}:bar:baz",
                "Unique Identifier": f"{PARTY_KEY}:bar:baz",
            }
        )
        questionnaire_response_2 = mhs_message_set_questionnaire.validate(
            data={
                "Interaction ID": "bar2:baz2",
                "MHS SN": "bar2",
                "MHS IN": "baz2",
                "MHS CPA ID": f"{PARTY_KEY}:bar2:baz2",
                "Unique Identifier": f"{PARTY_KEY}:bar2:baz2",
            },
        )

        # Set up DeviceReferenceData in DB
        device_reference_data = epr_product.create_device_reference_data(
            name="ABC1234-987654 - MHS Message Set", environment=Environment.DEV
        )
        device_reference_data.add_questionnaire_response(questionnaire_response)
        device_reference_data.add_questionnaire_response(questionnaire_response_2)

        as_additional_interactions_questionnaire = QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
        )
        questionnaire_response_3 = as_additional_interactions_questionnaire.validate(
            data={
                "Interaction ID": "urn:foo3",
            }
        )
        questionnaire_response_4 = as_additional_interactions_questionnaire.validate(
            data={
                "Interaction ID": "urn:foo4",
            },
        )

        # Set up DeviceReferenceData in DB
        device_reference_data_as = epr_product.create_device_reference_data(
            name="ABC1234-987654 - AS Additional Interactions",
            environment=Environment.DEV,
        )
        device_reference_data_as.add_questionnaire_response(questionnaire_response_3)
        device_reference_data_as.add_questionnaire_response(questionnaire_response_4)

        device_reference_data_repo = DeviceReferenceDataRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        device_reference_data_repo.write(device_reference_data)
        device_reference_data_repo.write(device_reference_data_as)

        # Set up Device in DB
        device: Device = epr_product.create_device(
            name="Product-AS", environment=Environment.DEV
        )
        device.add_tag(party_key="f5h1r-850000")

        # set up spine as questionnaire response
        spine_as_questionnaire = QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_AS
        )
        spine_as_questionnaire_response = spine_as_questionnaire.validate(
            data={
                "ODS Code": "FH15R",
                "Client ODS Codes": ["FH15R"],
                "ASID": "foobar",
                "MHS Party Key": "P.123-XXX",
                "Approver URP": "approver-123",
                "Date Approved": "2024-01-01",
                "Requestor URP": "requestor-789",
                "Date Requested": "2024-01-03",
                "Product Key": "product-key-001",
                "MHS Manufacturer Organisation": "AAA",
                "Product Name": "my spine product",
                "Product Version": "2001.01",
                "Temp UID": None,
            }
        )
        device.add_questionnaire_response(spine_as_questionnaire_response)

        device.add_device_reference_data_id(
            device_reference_data_id=str(device_reference_data.id),
            path_to_data=["Interaction ID"],
        )
        device.add_device_reference_data_id(
            device_reference_data_id=str(device_reference_data_as.id),
            path_to_data=["Interaction ID"],
        )

        device_repo = DeviceRepository(table_name=TABLE_NAME, dynamodb_client=client)
        device_repo.write(device)

        from api.readDevice.index import handler

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {
                    "product_team_id": str(product_team.id),
                    "product_id": str(epr_product.id.id),
                    "environment": "dev",
                    "device_id": str(device.id),
                },
            }
        )

    response_body = json_loads(result["body"])
    # Assertions for fields that must exactly match
    assert response_body["id"] == str(device.id)
    assert response_body["product_id"] == str(epr_product.id)
    assert response_body["product_team_id"] == str(product_team.id)
    assert response_body["name"] == device.name
    assert response_body["ods_code"] == device.ods_code
    assert response_body["status"] == Status.ACTIVE
    assert response_body["deleted_on"] is None
    assert response_body["keys"] is not None
    assert response_body["tags"] is not None
    assert response_body["device_reference_data"] is not None

    # Assertions for fields that only need to be included
    assert "created_on" in response_body
    assert "spine_as/1" in response_body["questionnaire_responses"]

    # Assert drd questionnaire responses have been added
    assert "spine_mhs_message_sets/1" in response_body["questionnaire_responses"]
    for resp in response_body["questionnaire_responses"]["spine_mhs_message_sets/1"]:
        assert "MHS SN" not in resp["data"]
        assert "MHS IN" not in resp["data"]
        assert "Interaction ID" in resp["data"]

    assert (
        "spine_as_additional_interactions/1" in response_body["questionnaire_responses"]
    )

    for resp in response_body["questionnaire_responses"][
        "spine_as_additional_interactions/1"
    ]:
        assert "MHS SN" not in resp["data"]
        assert "MHS IN" not in resp["data"]
        assert "Interaction ID" in resp["data"]

    expected_headers = {
        "Content-Type": "application/json",
        "Version": version,
    }

    # Check response headers
    assert result["statusCode"] == 200
    assert result["headers"]["Content-Length"] == str(len(result["body"]))
    for key, value in expected_headers.items():
        assert result["headers"][key] == value


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_no_such_device(version):
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team_epr(
        name=PRODUCT_TEAM_NAME, keys=PRODUCT_TEAM_KEYS
    )
    with mock_table(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        # Set up ProductTeam in DB
        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        # Set up Product in DB
        epr_product = product_team.create_epr_product(
            name=PRODUCT_NAME, product_id=PRODUCT_ID
        )
        product_repo = EprProductRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_repo.write(epr_product)

        from api.readDevice.index import handler

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {
                    "product_team_id": str(product_team.id),
                    "product_id": str(epr_product.id),
                    "environment": "dev",
                    "device_id": "does not exist",
                },
            }
        )

    expected_result = json.dumps(
        {
            "errors": [
                {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": f"Could not find Device for key ('{product_team.id}', 'P.XXX-YYY', 'DEV', 'does not exist')",
                }
            ],
        }
    )

    expected = {
        "statusCode": 404,
        "body": expected_result,
        "headers": {
            "Content-Length": str(len(expected_result)),
            "Content-Type": "application/json",
            "Version": version,
        },
    }
    _response_assertions(
        result=result, expected=expected, check_body=True, check_content_length=True
    )


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_no_such_product(version):
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team_epr(
        name=PRODUCT_TEAM_NAME, keys=PRODUCT_TEAM_KEYS
    )
    with mock_table(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        # Set up ProductTeam in DB
        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        from api.readDevice.index import handler

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {
                    "product_team_id": str(product_team.id),
                    "product_id": "product that doesnt exist",
                    "environment": "dev",
                    "device_id": "does not exist",
                },
            }
        )

    expected_result = json.dumps(
        {
            "errors": [
                {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": f"Could not find EprProduct for key ('{product_team.id}', 'product that doesnt exist')",
                }
            ],
        }
    )

    expected = {
        "statusCode": 404,
        "body": expected_result,
        "headers": {
            "Content-Length": str(len(expected_result)),
            "Content-Type": "application/json",
            "Version": version,
        },
    }
    _response_assertions(
        result=result, expected=expected, check_body=True, check_content_length=True
    )


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_no_such_product_team(version):
    with mock_table(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.readDevice.index import handler

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {
                    "product_id": str(PRODUCT_ID),
                    "product_team_id": str(PRODUCT_TEAM_ID),
                    "environment": "dev",
                    "device_id": "123",
                },
            }
        )

    expected_result = json.dumps(
        {
            "errors": [
                {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": f"Could not find ProductTeam for key ('{PRODUCT_TEAM_ID}')",
                }
            ],
        }
    )

    expected = {
        "statusCode": 404,
        "body": expected_result,
        "headers": {
            "Content-Length": str(len(expected_result)),
            "Content-Type": "application/json",
            "Version": version,
        },
    }
    _response_assertions(
        result=result, expected=expected, check_body=True, check_content_length=True
    )


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_incorrect_env(version):
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team_epr(
        name=PRODUCT_TEAM_NAME, keys=PRODUCT_TEAM_KEYS
    )

    with mock_table(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        # Set up ProductTeam in DB
        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        # Set up Product in DB
        epr_product = product_team.create_epr_product(
            name=PRODUCT_NAME, product_id=PRODUCT_ID
        )
        product_repo = EprProductRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_repo.write(epr_product)

        # Set up Device in DB
        device = epr_product.create_device(
            name=DEVICE_NAME, environment=Environment.DEV
        )
        device_repo = DeviceRepository(table_name=TABLE_NAME, dynamodb_client=client)
        device_repo.write(device)

        from api.readDevice.index import handler

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {
                    "product_team_id": str(product_team.id),
                    "product_id": str(epr_product.id.id),
                    "environment": "prod",
                    "device_id": str(device.id),
                },
            }
        )

        expected_result = json.dumps(
            {
                "errors": [
                    {
                        "code": "RESOURCE_NOT_FOUND",
                        "message": f"Could not find Device for key ('{product_team.id}', '{epr_product.id.id}', 'PROD', '{device.id}')",
                    }
                ],
            }
        )

        expected = {
            "statusCode": 404,
            "body": expected_result,
            "headers": {
                "Content-Length": str(len(expected_result)),
                "Content-Type": "application/json",
                "Version": version,
            },
        }
        _response_assertions(
            result=result, expected=expected, check_body=True, check_content_length=True
        )
