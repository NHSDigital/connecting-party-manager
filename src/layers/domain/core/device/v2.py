from collections import defaultdict
from datetime import datetime
from enum import StrEnum, auto
from functools import wraps
from typing import Callable, Optional, ParamSpec, TypeVar
from uuid import UUID, uuid4

import orjson
from attr import dataclass
from domain.core.aggregate_root import AggregateRoot
from domain.core.base import BaseModel
from domain.core.device_key.v2 import DeviceKey
from domain.core.enum import Status
from domain.core.error import DuplicateError, NotFoundError
from domain.core.event import Event, EventDeserializer
from domain.core.questionnaire.v2 import (
    QuestionnaireResponse,
    QuestionnaireResponseUpdatedEvent,
)
from domain.core.timestamp import now
from domain.core.validation import DEVICE_NAME_REGEX
from pydantic import Field, validator

TAG_SEPARATOR = "##"
TAG_COMPONENT_SEPARATOR = "##"
TAG_COMPONENT_CONTAINER_LEFT = "<<"
TAG_COMPONENT_CONTAINER_RIGHT = ">>"
UPDATED_ON = "updated_on"
DEVICE_UPDATED_ON = f"device_{UPDATED_ON}"


class QuestionnaireNotFoundError(Exception):
    pass


class QuestionnaireResponseNotFoundError(Exception):
    pass


class DuplicateQuestionnaireResponse(Exception):
    pass


class QuestionNotFoundError(Exception):
    pass


class EventUpdatedError(Exception):
    pass


@dataclass(kw_only=True, slots=True)
class DeviceCreatedEvent(Event):
    id: str
    name: str
    device_type: "DeviceType"
    product_team_id: UUID
    ods_code: str
    status: Status
    created_on: str
    updated_on: Optional[str] = None
    deleted_on: Optional[str] = None
    keys: list[DeviceKey]
    tags: list["DeviceTag"]
    questionnaire_responses: dict[str, dict[str, "QuestionnaireResponse"]]


@dataclass(kw_only=True, slots=True)
class DeviceUpdatedEvent(Event):
    id: str
    name: str
    device_type: "DeviceType"
    product_team_id: UUID
    ods_code: str
    status: Status
    created_on: str
    updated_on: str = None
    deleted_on: Optional[str] = None
    keys: list[DeviceKey]
    tags: list["DeviceTag"]
    questionnaire_responses: dict[str, dict[str, "QuestionnaireResponse"]]


@dataclass(kw_only=True, slots=True)
class DeviceKeyAddedEvent(Event):
    new_key: DeviceKey
    id: str
    name: str
    device_type: "DeviceType"
    product_team_id: UUID
    ods_code: str
    status: Status
    created_on: str
    updated_on: str = None
    deleted_on: Optional[str] = None
    keys: list[DeviceKey]
    tags: list["DeviceTag"]
    questionnaire_responses: dict[str, dict[str, "QuestionnaireResponse"]]


@dataclass(kw_only=True, slots=True)
class DeviceKeyDeletedEvent(Event):
    deleted_key: DeviceKey
    id: str
    keys: list[DeviceKey]
    tags: list["DeviceTag"]
    updated_on: str = None


@dataclass(kw_only=True, slots=True)
class DeviceTagAddedEvent(Event):
    new_tag: "DeviceTag"
    id: str
    name: str
    device_type: "DeviceType"
    product_team_id: UUID
    ods_code: str
    status: Status
    created_on: str
    updated_on: str = None
    deleted_on: Optional[str] = None
    keys: list[DeviceKey]
    tags: list["DeviceTag"]
    questionnaire_responses: dict[str, dict[str, "QuestionnaireResponse"]]


class DeviceType(StrEnum):
    """
    A Product is to be classified as being one of the following.  These terms
    were provided by Aubyn Crawford in collaboration with Service Now.

    NOTE:
        A 'SERVICE' and 'API' is NOT what a developer would expect them to be.
        These are terms from the problem domain and relate to how Assurance
        is performed.
    """

    PRODUCT = auto()
    ENDPOINT = auto()
    # SERVICE = auto()
    # API = auto()


class DeviceTag(BaseModel):
    components: list[tuple[str, str]]

    @validator("components")
    def sort_components(cls, components: list[tuple[str, str]]):
        return list(sorted(components, key=lambda elements: elements[0]))

    @property
    def value(self):
        return TAG_SEPARATOR.join(
            f"{TAG_COMPONENT_CONTAINER_LEFT}{key}{TAG_COMPONENT_SEPARATOR}{value}{TAG_COMPONENT_CONTAINER_RIGHT}"
            for key, value in self.components
        )

    def __hash__(self):
        return hash(tuple(self.components))


RT = TypeVar("RT")
P = ParamSpec("P")


def _set_updated_on(device: "Device", event: "Event"):
    if not hasattr(event, UPDATED_ON):
        raise EventUpdatedError(
            f"All returned events must have attribute '{UPDATED_ON}'"
        )
    updated_on = getattr(event, UPDATED_ON) or now()
    setattr(event, UPDATED_ON, updated_on)
    device.updated_on = updated_on


def event(fn: Callable[P, RT]) -> Callable[P, RT]:
    @wraps(fn)
    def wrapper(self: "Device", *args: P.args, **kwargs: P.kwargs) -> RT:
        _event = fn(self, *args, **kwargs)
        self.add_event(_event)
        _set_updated_on(device=self, event=_event)
        return _event

    return wrapper


class Device(AggregateRoot):
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

    id: UUID = Field(default_factory=uuid4, immutable=True)
    name: str = Field(regex=DEVICE_NAME_REGEX)
    device_type: DeviceType = Field(immutable=True)
    status: Status = Field(default=Status.ACTIVE)
    product_team_id: UUID
    ods_code: str
    created_on: datetime = Field(default_factory=now, immutable=True)
    updated_on: Optional[datetime] = Field(default=None)
    deleted_on: Optional[datetime] = Field(default=None)
    keys: list[DeviceKey] = Field(default_factory=list)
    tags: list[DeviceTag] = Field(default_factory=list)
    questionnaire_responses: dict[str, dict[str, QuestionnaireResponse]] = Field(
        default_factory=lambda: defaultdict(dict)
    )

    @event
    def update(self, **kwargs) -> DeviceUpdatedEvent:
        kwargs[UPDATED_ON] = now()
        device_data = self._update(data=kwargs)
        return DeviceUpdatedEvent(**device_data)

    @event
    def delete(self) -> DeviceUpdatedEvent:
        deleted_on = now()
        device_data = self._update(
            data=dict(
                status=Status.INACTIVE,
                updated_on=deleted_on,
                deleted_on=deleted_on,
            )
        )
        return DeviceUpdatedEvent(**device_data)

    @event
    def add_key(self, key_type: str, key_value: str) -> DeviceKeyAddedEvent:
        device_key = DeviceKey(key_value=key_value, key_type=key_type)
        if device_key in self.keys:
            raise DuplicateError(
                f"It is forbidden to supply duplicate keys: '{key_type}':'{key_value}'"
            )
        self.keys.append(device_key)
        device_data = self.state()
        device_data.pop(UPDATED_ON)  # The @event decorator will handle updated_on
        return DeviceKeyAddedEvent(new_key=device_key, **device_data)

    @event
    def delete_key(self, key_type: str, key_value: str) -> DeviceKeyDeletedEvent:
        device_key = DeviceKey(key_value=key_value, key_type=key_type)
        if device_key not in self.keys:
            raise NotFoundError(
                f"This device does not contain key '{key_type}':'{key_value}'"
            ) from None
        self.keys.remove(device_key)
        return DeviceKeyDeletedEvent(
            deleted_key=device_key,
            id=self.id,
            keys=[k.dict() for k in self.keys],
            tags=[t.dict() for t in self.tags],
        )

    @event
    def add_tag(self, **kwargs):
        components = list(map(tuple, kwargs.items()))
        device_tag = DeviceTag(components=components)
        if device_tag in self.tags:
            raise DuplicateError(
                f"It is forbidden to supply duplicate tag: '{device_tag.value}'"
            )
        self.tags.append(device_tag)
        device_data = self.state()
        device_data.pop(UPDATED_ON)  # The @event decorator will handle updated_on
        return DeviceTagAddedEvent(new_tag=device_tag, **device_data)

    @event
    def add_questionnaire_response(
        self, questionnaire_response: QuestionnaireResponse
    ) -> QuestionnaireResponseUpdatedEvent:
        questionnaire_id = questionnaire_response.questionnaire.id
        questionnaire_responses = self.questionnaire_responses[questionnaire_id]

        created_on_str = questionnaire_response.created_on.isoformat()
        if created_on_str in questionnaire_responses:
            raise DuplicateQuestionnaireResponse(
                "This Device already contains a "
                f"response created on {created_on_str}"
                f"for Questionnaire {questionnaire_id}"
            )
        questionnaire_responses[created_on_str] = questionnaire_response

        return QuestionnaireResponseUpdatedEvent(
            entity_id=self.id,
            entity_keys=[k.dict() for k in self.keys],
            entity_tags=[t.dict() for t in self.tags],
            questionnaire_responses={
                qid: {_created_on: qr.dict() for _created_on, qr in _qr.items()}
                for qid, _qr in self.questionnaire_responses.items()
            },
        )

    @event
    def update_questionnaire_response(
        self,
        questionnaire_response: QuestionnaireResponse,
    ) -> QuestionnaireResponseUpdatedEvent:
        questionnaire_id = questionnaire_response.questionnaire.id
        questionnaire_responses = self.questionnaire_responses.get(questionnaire_id)
        if questionnaire_responses is None:
            raise QuestionnaireNotFoundError(
                "This device does not contain a Questionnaire "
                f"with id '{questionnaire_id}'"
            ) from None

        created_on_str = questionnaire_response.created_on.isoformat()
        if created_on_str not in questionnaire_responses:
            raise QuestionnaireResponseNotFoundError(
                "This device does not contain a Questionnaire with a "
                f"response created on '{created_on_str}'"
            ) from None

        questionnaire_responses[created_on_str] = questionnaire_response

        return QuestionnaireResponseUpdatedEvent(
            entity_id=self.id,
            entity_keys=[k.dict() for k in self.keys],
            entity_tags=[t.dict() for t in self.tags],
            questionnaire_responses={
                qid: {_created_on: qr.dict() for _created_on, qr in _qr.items()}
                for qid, _qr in self.questionnaire_responses.items()
            },
        )

    def state(self) -> dict:
        """Returns a deepcopy of the Device itself, useful for bulk operations rather than dealing with events"""
        return orjson.loads(self.json())

    def is_active(self):
        return self.status is Status.ACTIVE


class DeviceEventDeserializer(EventDeserializer):
    event_types = (
        DeviceCreatedEvent,
        DeviceUpdatedEvent,
        DeviceKeyAddedEvent,
        DeviceKeyDeletedEvent,
        DeviceTagAddedEvent,
        QuestionnaireResponseUpdatedEvent,
    )
