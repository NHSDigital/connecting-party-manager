from dataclasses import dataclass

import pytest
from domain.core.aggregate_root import AggregateRoot
from domain.core.error import ImmutableFieldError, UnknownFields
from domain.core.event import Event
from pydantic import Field, ValidationError


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


def test_model_fields():
    class MyModel(AggregateRoot):
        field_1: str
        field_2: str = Field(exclude=True)
        field_3: int

    my_model = MyModel(field_1="foo", field_2="bar", field_3=1)
    assert my_model.model_fields == {"field_1", "field_3"}


def test_immutable_fields():
    class MyModel(AggregateRoot):
        field_1: str
        field_2: str = Field(immutable=True, exclude=True)
        field_3: int = Field(immutable=True)
        field_4: int

    my_model = MyModel(field_1="foo", field_2="bar", field_3=1, field_4=2)
    assert my_model.immutable_fields == {"field_2", "field_3"}


def test__update():
    class MyModel(AggregateRoot):
        field_1: str
        field_2: str
        field_3: int

    my_model = MyModel(field_1="foo", field_2="bar", field_3=1)
    data = my_model._update({"field_2": "BAR", "field_3": 23})

    assert data == {"field_1": "foo", "field_2": "BAR", "field_3": 23}


def test__update_unknown_field():
    class MyModel(AggregateRoot):
        pass

    my_model = MyModel()
    with pytest.raises(UnknownFields):
        my_model._update({"field_2": "BAR"})


def test__update_immutable_field_error():
    class MyModel(AggregateRoot):
        field_1: str = Field(immutable=True)

    my_model = MyModel(field_1="bar")
    with pytest.raises(ImmutableFieldError):
        my_model._update({"field_1": "BAR"})


def test__update_bad_data():
    class MyModel(AggregateRoot):
        field_1: int

    my_model = MyModel(field_1=123)
    with pytest.raises(ValidationError):
        my_model._update({"field_1": "BAR"})
