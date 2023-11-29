from enum import StrEnum, auto
from uuid import UUID

from domain.core.aggregate_root import AggregateRoot
from domain.core.error import DuplicateError, NotFoundError
from domain.core.event import Event
from pydantic import BaseModel, Field


class ProductCreatedEvent(Event):
    """
    Raised when a new Product is created
    """

    def __init__(self, id, name, type, product_team_id, ods_code, ods_name, status):
        self.id = id
        self.name = name
        self.type = type
        self.product_team_id = product_team_id
        self.ods_code = ods_code
        self.ods_name = ods_name
        self.status = status


class ProductUpdatedEvent(Event):
    """
    Raised when a Product name or type is amended
    """

    def __init__(self, id, name, type):
        self.id = id
        self.name = name
        self.type = type


class ProductDeletedEvent(Event):
    """
    Raised when a Product has been deleted
    """

    def __init__(self, id):
        self.id = id


class RelationshipAddedEvent(Event):
    """
    Raised when a relationship has been created between two Products.
    """

    def __init__(self, id, target, type):
        self.id = id
        self.target = target
        self.type = type


class RelationshipRemovedEvent(Event):
    """
    Raised when a relationship has been removed from two Products.
    """

    def __init__(self, id, target):
        self.id = id
        self.target = target


class ProductKeyAddedEvent(Event):
    """
    Raised when a new Key (Product Id/ASID/SNow) has been added to a Product.
    """

    def __init__(self, id, key, type):
        self.id = id
        self.key = key
        self.type = type


class ProductKeyRemovedEvent(Event):
    """
    Raised when an existing Key is removed from a Product.
    """

    def __init__(self, id, key):
        self.id = id
        self.key = key


class RelationshipType(StrEnum):
    """
    How we classify the relationships between two products.
    """

    DEPENDENCY = auto()
    # Product is dependent upon / consumes another Product
    # https://nhsd-confluence.digital.nhs.uk/display/SPINE/CPM+Domain+Model#CPMDomainModel-Dependencies
    COMPONENT = auto()
    # Product is a sub-component of an existing Product
    # https://nhsd-confluence.digital.nhs.uk/display/SPINE/CPM+Domain+Model#CPMDomainModel-Ranges
    REVISION = auto()
    # Product is a revision of an existing Product
    # https://nhsd-confluence.digital.nhs.uk/display/SPINE/CPM+Domain+Model#CPMDomainModel-Versioning


class Relationship(BaseModel):
    """
    A relationship indicates that two Products are linked.  One product is the "Source" and the other is the "Destination"
    """

    type: RelationshipType


class ProductKeyType(StrEnum):
    PRODUCT_ID = auto()
    # XXX-XXX-XXX
    ACCREDITED_SYSTEM_ID = auto()
    # \d{1,12}
    SERVICE_NOW_ID = auto()
    # TBD


class ProductKey(BaseModel):
    """
    A Product Key is a secondary way of indexing / retrieving Products.  These are expected to be:
      Product Id                    - e.g. XXX-XXX-XXX
      Accredited System Id (ASID)   - e.g. 123456789012
      Service Now Id                - e.g. TBD
    """

    type: ProductKeyType


class ProductType(StrEnum):
    """
    A Product is to be classified as being one of the following.  These terms
    were provided by Aubyn Crawford in collaboration with Service Now.

    NOTE:
        A 'SERVICE' and 'API' is NOT what a developer would expect them to be.
        These are terms from the problem domain and relate to how Assurance
        is performed.
    """

    PRODUCT = auto()
    SERVICE = auto()
    API = auto()


class ProductStatus(StrEnum):
    """
    Indicates whether a record is active or has been deleted
    """

    ACTIVE = auto()
    INACTIVE = auto()


class Product(AggregateRoot):
    """
    An entity in the database.  It could model all sorts of different logical or
    physical entities:
    e.g.
        NRL (SERVICE)
        +-- NRL.v2 (API)
        |   +-- nrl (???)
        +-- NRL.v3 (API)
            +-- nrl-consumer-api (???)
            +-- nrl-producer-api (???)
    """

    id: UUID
    name: str = Field(pattern="^[a-z][a-z0-9_]+$")
    type: ProductType
    status: ProductStatus = Field(default=ProductStatus.ACTIVE)
    product_team_id: UUID
    ods_code: str
    ods_name: str
    relationships: dict[UUID, Relationship] = (lambda: {})()
    keys: dict[str, ProductKey] = (lambda: {})()

    def rename(self, name: str):
        """
        Demonstrating that `renaming` is a specific operation and not just a
        CRUD update.
        """
        raise NotImplementedError()

    def add_relationship(
        self, target: "Product", type: RelationshipType
    ) -> RelationshipAddedEvent:
        """
        Adds a relationship between two Products
        """
        if target.id in self.relationships:
            raise DuplicateError(f"Relationship {target.id} exists")
        self.relationships[target.id] = Relationship(type=type)
        event = RelationshipAddedEvent(id=self.id, target=target.id, type=type)
        return self.add_event(event=event)

    def remove_relationship(self, target: str) -> RelationshipRemovedEvent:
        """
        Removes an existing relationship between two Products
        TODO: Do we delete them or mark them inactive?
        """
        target_id = target.id if isinstance(target, Product) else target
        if target_id not in self.relationships:
            raise NotFoundError(f"Relationship {target_id} is unknown")
        del self.relationships[target_id]
        event = RelationshipRemovedEvent(id=self.id, target=target_id)
        return self.add_event(event=event)

    def add_key(self, key, type: ProductKeyType) -> ProductKeyAddedEvent:
        """
        Adds a new Key to a Product
        """
        if key in self.keys:
            raise DuplicateError(f"Key {key} exists")
        self.keys[key] = ProductKey(type=type)
        event = ProductKeyAddedEvent(id=self.id, key=key, type=type)
        return self.add_event(event=event)

    def remove_key(self, key: str) -> ProductKeyRemovedEvent:
        """
        Remove an existing key from a Product
        TODO: Do we delete them or mark inactive?
        """
        if key not in self.keys:
            raise NotFoundError(f"Key {key} is unknown")
        del self.keys[key]
        event = ProductKeyRemovedEvent(id=self.id, key=key)
        return self.add_event(event=event)

    def delete(self) -> list[Event]:
        """
        Delete the entire Product and all sub-entities.
        This method will generate all the events required to ensure that all
        associated records are removed.
        """
        events = (
            [
                self.remove_relationship(target)
                for target in list(self.relationships.keys())
            ]
            + [self.remove_key(key) for key in list(self.keys.keys())]
            + [ProductDeletedEvent(id=self.id)]
        )
        self.events = self.events + events
        return self.events
