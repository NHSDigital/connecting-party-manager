from dataclasses import asdict
from typing import TypeVar

from domain.core.error import ImmutableFieldError, UnknownFields
from pydantic import BaseModel, Field, validate_model

from .event import Event, ExportedEventsTypeDef

K = TypeVar("K")
V = TypeVar("V")


def _validate_model(model, input_data):
    """
    Shallow wrapper around pydantic's 'validate_model' to raise an error
    if one was discovered during validation of the input_data against the model
    """
    _, _, error = validate_model(model=model, input_data=input_data)
    if error is not None:
        raise error


class AggregateRoot(BaseModel):
    """
    Entities in the domain are arranged as collections, known as Aggregates, and
    one object in that collection is called the Aggregate Root.  The Aggregate
    Root object owns all the other objects in the aggregate.  Deleting the root
    deletes them.

    e.g. Products include relationships and keys.
        Product
        +-- Relationship
        +-- ProductKey

    Amendments to the AggregateRoot will results in events being added to an
    internal `events` property
    """

    class Config:
        """
        Events are not pydantic classes
        """

        arbitrary_types_allowed = True

    events: list[Event] = Field(default_factory=list, exclude=True)

    def add_event(self, event: Event) -> Event:
        """
        Add an event to the internal queue
        """
        self.events.append(event)
        return event

    def clear_events(self):
        """
        Clear events stored on the AR once they've been processed (e.g. passed
        to the event bus or for testing purposes)
        """
        self.events.clear()

    def export_events(self) -> ExportedEventsTypeDef:
        """
        Export events in a form that is independent of the domain. The form is:

            [
                {"event_name_in_snake_case": {"event_data": "event_value", ...}},
                ...
            ]

        for example:

            [
                {"device_created_event": {"id": "123", ...}},
                {"device_key_added_event": {"key_type": "asid", ...}},
                ...
            ]

        """
        return [{event.public_name: asdict(event)} for event in self.events]

    @property
    def model_fields(self) -> set[str]:
        return set(
            field_name
            for field_name in self.__fields__
            if self.__fields__[field_name].field_info.exclude is not True
        )

    @property
    def immutable_fields(self) -> set[str]:
        return set(
            field_name
            for field_name in self.__fields__
            if self.__fields__[field_name].field_info.extra.get("immutable") is True
        )

    def _update(self, data: dict[K, V]) -> dict[K, V]:
        fields_to_update = set(data)
        unknown_fields = fields_to_update - self.model_fields
        if unknown_fields:
            raise UnknownFields(", ".join(unknown_fields))

        immutable_fields = fields_to_update.intersection(self.immutable_fields)
        if immutable_fields:
            raise ImmutableFieldError(", ".join(immutable_fields))

        _data = self.dict()
        _data.update(data)
        _validate_model(model=self.__class__, input_data=_data)

        for field, value in data.items():
            setattr(self, field, value)
        return _data
