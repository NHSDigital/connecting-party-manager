import re
from abc import ABC, ABCMeta

from attr import has as is_dataclass

ExportedEventTypeDef = dict[str, dict]
ExportedEventsTypeDef = list[ExportedEventTypeDef]


def _camel_case_to_snake_case(x: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", x).lower()


class MetaEvent(ABCMeta):
    @property
    def public_name(cls):
        return _camel_case_to_snake_case(cls.__name__)

    def __init_subclass__(cls):
        if not is_dataclass(cls):
            raise TypeError(
                "All subclasses of 'Event' should be decorated with @attr.dataclass"
            )
        super().__init_subclass__()


class Event(ABC, metaclass=MetaEvent):
    """
    The base class for all events that are raised by CPM.  This class exists
    to classify the events, and constrain their use in generics, rather than
    provide features.
    Domain events will be propagated out to external systems.
    """

    @property
    def public_name(self):
        return self.__class__.public_name


class EventDeserializer(ABC):
    """
    Base class for deserializing exported events
    e.g. for use with the repository pattern
    """

    event_types: tuple[type[Event]]

    @classmethod
    def parse(self, exported_event: ExportedEventTypeDef) -> Event:
        ((event_name, event_data),) = exported_event.items()
        for event_type in self.event_types:
            if event_name == event_type.public_name:
                return event_type(**event_data)
        raise NotImplementedError(f"Not implemented parsing of {event_name}")
