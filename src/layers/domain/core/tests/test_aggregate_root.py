from dataclasses import dataclass

from domain.core.aggregate_root import AggregateRoot
from domain.core.event import Event


def test_export_events():
    @dataclass
    class MyEvent(Event):
        my_value: str

    @dataclass
    class MyOtherEvent(Event):
        my_value: str
        my_other_value: str

    root = AggregateRoot()
    root.add_event(MyEvent(my_value="foo"))
    root.add_event(MyOtherEvent(my_value="foo", my_other_value="bar"))
    root.add_event(MyEvent(my_value="bar"))

    assert root.export_events() == [
        {"my_event": {"my_value": "foo"}},
        {"my_other_event": {"my_value": "foo", "my_other_value": "bar"}},
        {"my_event": {"my_value": "bar"}},
    ]
