from notify.operations import send_notification

EXAMPLE_DOT_COM = "https://httpbin.org"


def test_send_notification():
    response = send_notification(EXAMPLE_DOT_COM, foo=[123], bar="abc")
    assert len(response) > 0
