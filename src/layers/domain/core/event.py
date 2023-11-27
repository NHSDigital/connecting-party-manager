from abc import ABC


class Event(ABC):
    """
    The base class for all events that are raised by CPM.  This class exists
    to classify the events, and constrain their use in generics, rather than
    provide features.
    Domain events will be propagated out to external systems.
    """

    pass
