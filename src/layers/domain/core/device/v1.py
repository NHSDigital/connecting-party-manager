from collections import defaultdict
from datetime import datetime
from functools import cached_property
from urllib.parse import parse_qs, urlencode
from uuid import UUID, uuid4

import orjson
from attr import dataclass
from domain.core.aggregate_root import UPDATED_ON, AggregateRoot, event
from domain.core.base import BaseModel
from domain.core.cpm_system_id import ProductId
from domain.core.device_key import DeviceKey
from domain.core.enum import Environment, Status
from domain.core.error import DuplicateError, NotFoundError
from domain.core.event import Event, EventDeserializer
from domain.core.questionnaire import QuestionnaireResponse
from domain.core.timestamp import now
from domain.core.validation import DEVICE_NAME_REGEX
from pydantic import Field, root_validator

UPDATED_ON = "updated_on"
DEVICE_UPDATED_ON = f"device_{UPDATED_ON}"


class QuestionnaireNotFoundError(Exception):
    pass


class QuestionnaireResponseNotFoundError(Exception):
    pass


class DuplicateQuestionnaireResponse(Exception):
    pass


@dataclass(kw_only=True, slots=True)
class DeviceCreatedEvent(Event):
    id: str
    name: str
    environment: Environment
    product_team_id: UUID
    product_id: ProductId
    ods_code: str
    status: Status
    created_on: str
    updated_on: str = None
    deleted_on: str = None
    keys: list[DeviceKey]
    tags: list[str]
    questionnaire_responses: dict[str, dict[str, "QuestionnaireResponse"]]
    device_reference_data: dict[str, list[str]]


@dataclass(kw_only=True, slots=True)
class DeviceUpdatedEvent(Event):
    id: str
    name: str
    environment: Environment
    product_team_id: UUID
    product_id: ProductId
    ods_code: str
    status: Status
    created_on: str
    updated_on: str = None
    deleted_on: str = None
    keys: list[DeviceKey]
    tags: list[str]
    questionnaire_responses: dict[str, dict[str, "QuestionnaireResponse"]]
    device_reference_data: dict[str, list[str]]


@dataclass(kw_only=True, slots=True)
class DeviceDeletedEvent(Event):
    id: str
    name: str
    environment: Environment
    product_team_id: UUID
    product_id: ProductId
    ods_code: str
    status: Status
    created_on: str
    updated_on: str = None
    deleted_on: str = None
    keys: list[DeviceKey]
    tags: list[str]
    questionnaire_responses: dict[str, dict[str, "QuestionnaireResponse"]]
    deleted_tags: list[str] = None
    device_reference_data: dict[str, list[str]]


@dataclass(kw_only=True, slots=True)
class DeviceKeyAddedEvent(Event):
    new_key: dict
    id: str
    name: str
    environment: Environment
    product_team_id: UUID
    product_id: ProductId
    ods_code: str
    status: Status
    created_on: str
    updated_on: str = None
    deleted_on: str = None
    keys: list[DeviceKey]
    tags: list[str]
    questionnaire_responses: dict[str, dict[str, "QuestionnaireResponse"]]
    device_reference_data: dict[str, list[str]]


@dataclass(kw_only=True, slots=True)
class DeviceKeyDeletedEvent(Event):
    deleted_key: dict
    id: str
    keys: list[dict]
    tags: list[str]
    updated_on: str = None


@dataclass(kw_only=True, slots=True)
class DeviceTagAddedEvent(Event):
    new_tag: str
    id: str
    name: str
    environment: Environment
    product_team_id: UUID
    product_id: ProductId
    ods_code: str
    status: Status
    created_on: str
    updated_on: str = None
    deleted_on: str = None
    keys: list[dict]
    tags: list[str]
    questionnaire_responses: dict[str, dict[str, "QuestionnaireResponse"]]
    device_reference_data: dict[str, list[str]]


@dataclass(kw_only=True, slots=True)
class DeviceTagsAddedEvent(Event):
    new_tags: list[str]
    id: str
    name: str
    environment: Environment
    product_team_id: UUID
    product_id: ProductId
    ods_code: str
    status: Status
    created_on: str
    updated_on: str = None
    deleted_on: str = None
    keys: list[DeviceKey]
    tags: list[str]
    questionnaire_responses: dict[str, dict[str, "QuestionnaireResponse"]]
    device_reference_data: dict[str, list[str]]


@dataclass(kw_only=True, slots=True)
class DeviceTagsClearedEvent(Event):
    id: str
    keys: list[dict]
    deleted_tags: list[str]
    updated_on: str = None


@dataclass(kw_only=True, slots=True)
class QuestionnaireResponseUpdatedEvent(Event):
    id: str
    questionnaire_responses: dict[str, list[QuestionnaireResponse]]
    keys: list[DeviceKey]
    tags: list[str]
    updated_on: str = None


@dataclass(kw_only=True, slots=True)
class DeviceReferenceDataIdAddedEvent(Event):
    id: str
    device_reference_data: dict[str, list[str]]
    updated_on: str = None


class DeviceTag(BaseModel):
    """
    DeviceTag is a mechanism for indexing Device data. In DynamoDB then intention is for this
    to be translated into a duplicated record in the database, so that Devices with with the
    same DeviceTag can be queried directly, therefore mimicking efficient search-like behaviour.
    """

    __root__: list[tuple[str, str]]

    class Config:
        arbitrary_types_allowed = True
        keep_untouched = (cached_property,)

    @root_validator(pre=True)
    def encode_tag(cls, values: dict):
        initialised_with_root = "__root__" in values and len(values) == 1
        item_to_process = values["__root__"] if initialised_with_root else values

        # Case 1: query string is provided (__root__="foo=bar")
        if initialised_with_root and isinstance(item_to_process, str):
            _components = ((k, v) for k, (v,) in parse_qs(item_to_process).items())
        # Case 2: query components are provided (__root__=("foo", "bar"))
        elif initialised_with_root:
            _components = ((k, v) for k, v in item_to_process)
        # Case 3: query components are directly provided (("foo", "bar"))
        else:
            _components = ((k, str(v)) for k, v in item_to_process.items())

        case_insensitive_components = tuple(
            sorted((k, v.lower()) for k, v in _components)
        )
        return {"__root__": case_insensitive_components}

    def dict(self, *args, **kwargs):
        return self.components

    @cached_property
    def components(self):
        return tuple(self.__root__)

    @cached_property
    def hash(self):
        return hash(self.components)

    @property
    def value(self) -> str:
        return urlencode(self.components)

    def __hash__(self):
        return self.hash

    def __eq__(self, other: "DeviceTag"):
        return self.hash == other.hash


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
    status: Status = Field(default=Status.ACTIVE)
    environment: Environment = Field()
    product_id: ProductId = Field(immutable=True)
    product_team_id: str = Field(immutable=True)
    ods_code: str
    created_on: datetime = Field(default_factory=now, immutable=True)
    updated_on: datetime = Field(default=None)
    deleted_on: datetime = Field(default=None)
    keys: list[DeviceKey] = Field(default_factory=list)
    tags: set[DeviceTag] | list[DeviceTag] = Field(default_factory=set)
    questionnaire_responses: dict[str, list[QuestionnaireResponse]] = Field(
        default_factory=lambda: defaultdict(list)
    )
    device_reference_data: dict[str, list[str]] = Field(
        default_factory=lambda: defaultdict(list)
    )

    def state_exclude_tags(self) -> dict:
        """
        Returns a deepcopy, useful for bulk operations rather than dealing with events.

        Exclude tags as we shouldn't return tags to the user on create.
        """
        device_dict = orjson.loads(self.json())
        device_dict.pop("tags", None)
        return device_dict

    @event
    def update(self, **kwargs) -> DeviceUpdatedEvent:
        kwargs[UPDATED_ON] = now()
        device_data = self._update(data=kwargs)
        return DeviceUpdatedEvent(**device_data)

    @event
    def delete(self) -> DeviceDeletedEvent:
        deleted_on = now()
        deleted_tags = {t.value for t in self.tags}
        device_data = self._update(
            data=dict(
                status=Status.INACTIVE,
                updated_on=deleted_on,
                deleted_on=deleted_on,
                tags=set(),
            )
        )
        return DeviceDeletedEvent(**device_data, deleted_tags=deleted_tags)

    @event
    def add_key(self, key_type: str, key_value: str) -> DeviceKeyAddedEvent:
        device_key = DeviceKey(key_value=key_value, key_type=key_type)
        if device_key in self.keys:
            raise DuplicateError(
                f"It is forbidden to supply duplicate keys: '{key_type}':'{key_value}'"
            )
        self.keys.append(device_key)
        device_data = self.state()
        device_data["tags"] = {t.value for t in self.tags}
        device_data.pop(UPDATED_ON)  # The @event decorator will handle updated_on
        return DeviceKeyAddedEvent(new_key=device_key.dict(), **device_data)

    @event
    def delete_key(self, key_type: str, key_value: str) -> DeviceKeyDeletedEvent:
        device_key = DeviceKey(key_value=key_value, key_type=key_type)
        if device_key not in self.keys:
            raise NotFoundError(
                f"This device does not contain key '{key_type}':'{key_value}'"
            ) from None
        self.keys.remove(device_key)
        return DeviceKeyDeletedEvent(
            deleted_key=device_key.dict(),
            id=self.id,
            keys=[k.dict() for k in self.keys],
            tags=[t.value for t in self.tags],
        )

    @event
    def add_tag(self, **kwargs) -> DeviceTagAddedEvent:
        device_tag = DeviceTag(**kwargs)
        if device_tag in self.tags:
            raise DuplicateError(
                f"It is forbidden to supply duplicate tag: '{device_tag.value}'"
            )
        self.tags.add(device_tag)
        device_data = self.state()
        device_data["tags"] = {t.value for t in self.tags}
        device_data.pop(UPDATED_ON)  # The @event decorator will handle updated_on
        return DeviceTagAddedEvent(new_tag=device_tag.value, **device_data)

    @event
    def add_tags(self, tags: list[dict]) -> DeviceTagsAddedEvent:
        """Optimised bulk equivalent of performing device.add_tag sequentially."""
        new_tags = {DeviceTag(**tag) for tag in tags}
        duplicate_tags = self.tags.intersection(new_tags)
        if duplicate_tags:
            raise DuplicateError(
                f"It is forbidden to supply duplicate tags: {[t.value for t in duplicate_tags]}"
            )
        self.tags = self.tags.union(new_tags)
        device_data = self.state()
        device_data["tags"] = {t.value for t in self.tags}
        device_data.pop(UPDATED_ON)  # The @event decorator will handle updated_on
        return DeviceTagsAddedEvent(
            new_tags={tag.value for tag in new_tags}, **device_data
        )

    @event
    def clear_tags(self):
        deleted_tags = self.tags
        self.tags = set()
        device_data = self.state()
        return DeviceTagsClearedEvent(
            id=device_data["id"],
            keys=device_data["keys"],
            deleted_tags={tag.value for tag in deleted_tags},
        )

    @event
    def add_questionnaire_response(
        self, questionnaire_response: QuestionnaireResponse
    ) -> QuestionnaireResponseUpdatedEvent:
        questionnaire_id = questionnaire_response.questionnaire_id
        questionnaire_responses = self.questionnaire_responses[questionnaire_id]
        created_on = questionnaire_response.created_on

        current_created_ons = [qr.created_on for qr in questionnaire_responses]
        if created_on in current_created_ons:
            raise DuplicateQuestionnaireResponse(
                "This Device already contains a "
                f"response created on {created_on.isoformat()}"
                f"for Questionnaire {questionnaire_id}"
            )
        questionnaire_responses.append(questionnaire_response)

        return QuestionnaireResponseUpdatedEvent(
            id=self.id,
            keys=[k.dict() for k in self.keys],
            tags=[t.value for t in self.tags],
            questionnaire_responses={
                qid: [qr.dict() for qr in qrs]
                for qid, qrs in self.questionnaire_responses.items()
            },
        )

    @event
    def add_device_reference_data_id(
        self, device_reference_data_id: str, path_to_data: list[str]
    ) -> DeviceReferenceDataIdAddedEvent:
        self.device_reference_data[str(device_reference_data_id)] = path_to_data
        device_data = self.state()
        return DeviceReferenceDataIdAddedEvent(
            id=device_data["id"],
            device_reference_data=device_data["device_reference_data"],
        )

    def is_active(self):
        return self.status is Status.ACTIVE


class DeviceEventDeserializer(EventDeserializer):
    event_types = (
        DeviceCreatedEvent,
        DeviceUpdatedEvent,
        DeviceDeletedEvent,
        DeviceKeyAddedEvent,
        DeviceKeyDeletedEvent,
        DeviceTagAddedEvent,
        DeviceTagsClearedEvent,
        DeviceTagsAddedEvent,
        DeviceReferenceDataIdAddedEvent,
        QuestionnaireResponseUpdatedEvent,
    )
