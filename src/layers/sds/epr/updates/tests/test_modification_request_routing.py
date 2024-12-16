from unittest import mock

from sds.epr.updates.modification_request_routing import (
    route_as_modification_request,
    route_mhs_modification_request,
)


def mock_patch(module: str):
    return mock.patch(
        f"sds.epr.updates.modification_request_routing.{module}",
        return_value=[f"called '{module}'"],
    )


def test_route_mhs_modification_request():

    modification_request = {
        "distinguished_name": {
            "ou": "services",
            "o": "nhs",
            "unique_identifier": "123",
        },
        "objectclass": {"modify"},
        "uniqueidentifier": {"123"},
        "modifications": [
            ["add", "foo", "bar"],
            ["replace", "foo", "bar"],
            ["delete", "foo", "bar"],
        ],
    }

    with (
        mock_patch("process_request_to_add_to_mhs"),
        mock_patch("process_request_to_replace_in_mhs"),
        mock_patch("process_request_to_delete_from_mhs"),
    ):
        assert route_mhs_modification_request(
            request=modification_request,
            device=None,
            device_reference_data_repository=None,
            mhs_device_questionnaire=None,
            mhs_device_field_mapping=None,
            message_set_questionnaire=None,
            message_set_field_mapping=None,
            additional_interactions_questionnaire=None,
        ) == [
            "called 'process_request_to_add_to_mhs'",
            "called 'process_request_to_replace_in_mhs'",
            "called 'process_request_to_delete_from_mhs'",
        ]


def test_route_as_modification_request():

    modification_request = {
        "distinguished_name": {
            "ou": "services",
            "o": "nhs",
            "unique_identifier": "123",
        },
        "objectclass": {"modify"},
        "uniqueidentifier": {"123"},
        "modifications": [
            ["add", "foo", "bar"],
            ["replace", "foo", "bar"],
            ["delete", "foo", "bar"],
        ],
    }

    with (
        mock_patch("process_request_to_add_to_as"),
        mock_patch("process_request_to_replace_in_as"),
        mock_patch("process_request_to_delete_from_as"),
    ):
        assert route_as_modification_request(
            request=modification_request,
            device=None,
            device_reference_data_repository=None,
            accredited_system_questionnaire=None,
            accredited_system_field_mapping=None,
            message_set_questionnaire=None,
            message_set_field_mapping=None,
            additional_interactions_questionnaire=None,
        ) == [
            "called 'process_request_to_add_to_as'",
            "called 'process_request_to_replace_in_as'",
            "called 'process_request_to_delete_from_as'",
        ]
