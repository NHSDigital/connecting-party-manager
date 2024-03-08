from dataclasses import asdict

from pydantic import BaseModel, Field

from .event import Event, ExportedEventsTypeDef


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
