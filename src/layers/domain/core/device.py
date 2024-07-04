from collections import defaultdict
from copy import deepcopy
from datetime import datetime
from enum import StrEnum, auto
from itertools import chain
from typing import Any, Optional
from uuid import UUID, uuid4

from attr import dataclass, field
from domain.core.questionnaire import (
    QuestionnaireInstanceEvent,
    QuestionnaireResponse,
    QuestionnaireResponseAddedEvent,
    QuestionnaireResponseDeletedEvent,
    QuestionnaireResponseUpdatedEvent,
)
from pydantic import Field

from .aggregate_root import AggregateRoot
from .device_key import DeviceKey, DeviceKeyType
from .error import DuplicateError, NotFoundError
from .event import Event, EventDeserializer
from .validation import DEVICE_NAME_REGEX


class QuestionnaireNotFoundError(Exception):
    pass


class QuestionnaireResponseNotFoundError(Exception):
    pass


class QuestionNotFoundError(Exception):
    pass


@dataclass(kw_only=True, slots=True)
class DeviceCreatedEvent(Event):
    id: str
    name: str
    type: "DeviceType"
    product_team_id: UUID
    ods_code: str
    keys: list[DeviceKey]
    questionnaire_responses: dict[str, list[QuestionnaireResponse]]
    status: "DeviceStatus"
    created_on: str
    updated_on: Optional[str] = None
    deleted_on: Optional[str] = None
    _trust: bool = field(alias="_trust", default=False)


@dataclass(kw_only=True, slots=True)
class DeviceStateEvent(Event):
    id: str
    name: str
    type: "DeviceType"
    product_team_id: UUID
    ods_code: str
    keys: list[DeviceKey]
    questionnaire_responses: dict[str, list[QuestionnaireResponse]]
    status: "DeviceStatus"
    created_on: str
    updated_on: Optional[str] = None
    deleted_on: Optional[str] = None
    _trust: bool = field(alias="_trust", default=False)


@dataclass(kw_only=True, slots=True)
class DeviceUpdatedEvent(Event):
    id: str
    name: str
    type: "DeviceType"
    product_team_id: UUID
    keys: list[DeviceKey]
    questionnaire_responses: dict[str, list[QuestionnaireResponse]]
    ods_code: str
    status: "DeviceStatus"
    created_on: str
    updated_on: str
    deleted_on: Optional[str] = None


@dataclass(kw_only=True, slots=True)
class DeviceKeyAddedEvent(Event):
    id: str
    key: str
    key_type: DeviceKeyType


@dataclass(kw_only=True, slots=True)
class DeviceKeyDeletedEvent(Event):
    id: str
    key: str
    remaining_keys: list[DeviceKey]


@dataclass(kw_only=True, slots=True)
class DeviceIndexAddedEvent(Event):
    id: str
    questionnaire_id: str
    question_name: str
    value: str


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


class DeviceStatus(StrEnum):
    ACTIVE = auto()
    INACTIVE = auto()  # "soft" delete


def _get_unique_answers(
    questionnaire_responses: list[QuestionnaireResponse], question_name: str
):
    all_responses = chain.from_iterable(
        _questionnaire_response.responses
        for _questionnaire_response in questionnaire_responses
    )
    matching_responses = filter(
        lambda response: question_name in response, all_responses
    )
    matching_response_answers = (
        answer for responses in matching_responses for answer in responses.values()
    )
    unique_answers = set(chain.from_iterable(matching_response_answers))
    return unique_answers


def _get_questionnaire_responses(
    questionnaire_responses: dict[str, list[QuestionnaireResponse]],
    questionnaire_id: str,
) -> list[QuestionnaireResponse]:
    _questionnaire_responses = questionnaire_responses.get(questionnaire_id)
    if _questionnaire_responses is None:
        raise QuestionnaireNotFoundError(
            f"This device does not contain a Questionnaire with id '{questionnaire_id}'"
        )
    elif not _questionnaire_responses:
        raise QuestionnaireResponseNotFoundError(
            f"This device does not contain a QuestionnaireResponse for Questionnaire with id '{questionnaire_id}'"
        )
    return _questionnaire_responses


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
    type: DeviceType = Field(immutable=True)
    status: DeviceStatus = Field(default=DeviceStatus.ACTIVE)
    product_team_id: UUID
    ods_code: str
    created_on: datetime = Field(default_factory=datetime.utcnow, immutable=True)
    updated_on: Optional[datetime] = Field(default=None)
    deleted_on: Optional[datetime] = Field(default=None)
    keys: list[DeviceKey] = Field(default_factory=list)
    questionnaire_responses: dict[str, list[QuestionnaireResponse]] = Field(
        default_factory=lambda: defaultdict(list)
    )
    indexes: set[tuple[str, str, Any]] = Field(default_factory=set, exclude=True)

    def update(self, **kwargs) -> DeviceUpdatedEvent:
        if "updated_on" not in kwargs:
            kwargs["updated_on"] = datetime.utcnow()
        device_data = self._update(data=kwargs)
        event = DeviceUpdatedEvent(**device_data)
        return self.add_event(event)

    def delete(self) -> DeviceUpdatedEvent:
        deletion_datetime = datetime.utcnow()
        return self.update(
            status=DeviceStatus.INACTIVE,
            updated_on=deletion_datetime,
            deleted_on=deletion_datetime,
        )

    def state(self):
        device = deepcopy(self)  # deep copy?
        device.events = [DeviceStateEvent(**device.dict())]
        return device

    def add_key(self, key_type: str, key: str) -> DeviceKeyAddedEvent:
        existing_keys = {
            (_device_key.key, _device_key.device_type) for _device_key in self.keys
        }
        if (key, key_type) in existing_keys:
            raise DuplicateError(
                f"It is forbidden to supply duplicate keys: ({key_type}) '{key}'"
            )

        device_key = DeviceKey(key=key, device_type=key_type)
        self.keys.append(device_key)
        event = DeviceKeyAddedEvent(id=self.id, key=key, key_type=key_type)
        return self.add_event(event)

    def delete_key(self, key: str) -> DeviceKeyDeletedEvent:
        device_key = next(
            (device_key for device_key in self.keys if device_key.key == key), None
        )
        if device_key is None:
            raise NotFoundError(f"This device does not contain key '{key}'") from None

        self.keys.remove(device_key)
        event = DeviceKeyDeletedEvent(id=self.id, key=key, remaining_keys=self.keys)
        return self.add_event(event)

    def add_questionnaire_response(
        self,
        questionnaire_response: QuestionnaireResponse,
        _questionnaire: dict = None,
        _trust=False,
    ) -> list[QuestionnaireInstanceEvent, QuestionnaireResponseAddedEvent]:
        _questionnaire = _questionnaire or questionnaire_response.questionnaire.dict()

        questionnaire_responses = self.questionnaire_responses[
            questionnaire_response.questionnaire.id
        ]
        questionnaire_response_index = len(questionnaire_responses)
        questionnaire_responses.append(questionnaire_response)
        questionnaire_used_already = questionnaire_response_index > 0

        events = []
        if not questionnaire_used_already:
            questionnaire_event = QuestionnaireInstanceEvent(
                entity_id=self.id,
                questionnaire_id=questionnaire_response.questionnaire.id,
                **_questionnaire,
            )
            events.append(questionnaire_event)
            self.add_event(questionnaire_event)

        questionnaire_response_event = QuestionnaireResponseAddedEvent(
            entity_id=self.id,
            questionnaire_response_index=questionnaire_response_index,
            questionnaire_id=questionnaire_response.questionnaire.id,
            responses=questionnaire_response.responses,
            _trust=_trust,
        )
        events.append(questionnaire_response_event)
        self.add_event(questionnaire_response_event)

        return events

    def update_questionnaire_response(
        self,
        questionnaire_response: QuestionnaireResponse,
        questionnaire_response_index: int,
    ) -> QuestionnaireResponseUpdatedEvent:
        questionnaire_responses = self.questionnaire_responses.get(
            questionnaire_response.questionnaire.id
        )
        if questionnaire_responses is None:
            raise QuestionnaireNotFoundError(
                "This device does not contain a Questionnaire "
                f"with id '{questionnaire_response.questionnaire.id}'"
            ) from None

        try:
            questionnaire_responses[
                questionnaire_response_index
            ] = questionnaire_response
        except IndexError:
            raise QuestionnaireResponseNotFoundError(
                "This device does not contain a Questionnaire with a "
                f"response at index '{questionnaire_response_index}'"
            ) from None

        event = QuestionnaireResponseUpdatedEvent(
            entity_id=self.id,
            questionnaire_id=questionnaire_response.questionnaire.id,
            questionnaire_response_index=questionnaire_response_index,
            responses=questionnaire_response.responses,
        )
        return self.add_event(event)

    def delete_questionnaire_response(
        self, questionnaire_id: str, questionnaire_response_index: int
    ) -> QuestionnaireResponseDeletedEvent:
        questionnaire_responses = self.questionnaire_responses.get(questionnaire_id)
        if questionnaire_responses is None:
            raise QuestionnaireNotFoundError(
                "This device does not contain a Questionnaire "
                f"with id '{questionnaire_id}'"
            ) from None

        try:
            questionnaire_responses.pop(questionnaire_response_index)
        except IndexError:
            raise QuestionnaireResponseNotFoundError(
                "This device does not contain a Questionnaire with a "
                f"response at index '{questionnaire_response_index}'"
            ) from None

        if len(questionnaire_responses) == 0:
            self.questionnaire_responses.pop(questionnaire_id)

        event = QuestionnaireResponseDeletedEvent(
            entity_id=self.id,
            questionnaire_id=questionnaire_id,
            questionnaire_response_index=questionnaire_response_index,
        )
        return self.add_event(event)

    def is_active(self):
        return self.status is DeviceStatus.ACTIVE


class DeviceEventDeserializer(EventDeserializer):
    event_types = (
        DeviceCreatedEvent,
        DeviceUpdatedEvent,
        DeviceKeyAddedEvent,
        DeviceKeyDeletedEvent,
        DeviceIndexAddedEvent,
        QuestionnaireResponseAddedEvent,
        QuestionnaireResponseUpdatedEvent,
        QuestionnaireResponseDeletedEvent,
        QuestionnaireInstanceEvent,
    )
