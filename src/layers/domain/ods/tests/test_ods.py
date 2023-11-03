from http import HTTPStatus
from unittest import mock

import pytest
from domain.ods import OdsApiOfflineError, is_valid_ods_code
from requests import HTTPError


def _raise(status_code: int):
    raise HTTPError(status_code)


@pytest.mark.slow
@pytest.mark.parametrize(
    "ods_code",
    [
        "TAJ",
        "TAD",
        "TAH",
    ],
)
def test_is_valid_ods_code_returns_true(ods_code):
    assert is_valid_ods_code(ods_code=ods_code)


@pytest.mark.slow
@pytest.mark.parametrize(
    "ods_code",
    [
        "AAA111",
        "BBB111",
        "CCC111",
        "   ",
        " AAA ",
        "😊😊😊",
    ],
)
def test_is_valid_ods_code_returns_false(ods_code):
    assert not is_valid_ods_code(ods_code=ods_code)


@pytest.mark.slow
@mock.patch("domain.ods.ODS_API_ENDPOINT", "http://eihrieowheoirhe.com")
def test_is_valid_ods_code_raises_on_connection_error():
    with pytest.raises(OdsApiOfflineError) as exception_wrapper:
        is_valid_ods_code(ods_code="any_old_thing")
    assert exception_wrapper.exconly() == (
        "domain.ods.OdsApiOfflineError: 2 exceptions were raised "
        "whilst attempting to execute 'is_valid_ods_code' (3 sub-exceptions)"
    )


@pytest.mark.slow
@pytest.mark.parametrize(
    "status_code",
    range(HTTPStatus.INTERNAL_SERVER_ERROR, HTTPStatus.GATEWAY_TIMEOUT + 1),
)
@mock.patch("domain.ods.requests")
@mock.patch("domain.ods.BACKOFF_BASE_SECONDS", 0.1)  # to speed the test up
def test_is_valid_ods_code_raises_on_ods_internal_server_error(
    mocked_requests, status_code: HTTPStatus
):
    mocked_response = mock.Mock()
    mocked_response.status_code = status_code
    mocked_response.raise_for_status = lambda: _raise(status_code)
    mocked_requests.get.return_value = mocked_response

    with pytest.raises(OdsApiOfflineError) as exception_wrapper:
        is_valid_ods_code(ods_code="any_old_thing")
    assert exception_wrapper.exconly() == (
        "domain.ods.OdsApiOfflineError: 2 exceptions were raised "
        "whilst attempting to execute 'is_valid_ods_code' (3 sub-exceptions)"
    )
