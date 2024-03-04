from domain.core.event import Event


def test_public_name():
    class MyEvent(Event):
        pass

    assert MyEvent.public_name == "my_event"
    assert MyEvent().public_name == "my_event"
