from domain.core.reference import Reference

from .event import Event


class ProductTeamCreatedEvent(Event):
    def __init__(self, id: str, name: str, organisation: Reference, owner: Reference):
        self.id = id
        self.name = name
        self.organisation = organisation
        self.owner = owner
