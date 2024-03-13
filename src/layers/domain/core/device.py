from collections import defaultdict
from dataclasses import dataclass
from enum import StrEnum, auto
from uuid import UUID, uuid4

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


@dataclass(kw_only=True, slots=True)
class DeviceCreatedEvent(Event):
    id: str
    name: str
    type: "DeviceType"
    product_team_id: UUID
    ods_code: str
    status: "DeviceStatus"


@dataclass(kw_only=True, slots=True)
class DeviceUpdatedEvent(Event):
    id: str
    name: str
    type: "DeviceType"
    product_team_id: UUID
    ods_code: str
    status: "DeviceStatus"


@dataclass(kw_only=True, slots=True)
class DeviceKeyAddedEvent(Event):
    id: str
    key: str
    type: DeviceKeyType


@dataclass(kw_only=True, slots=True)
class DeviceKeyDeletedEvent(Event):
    id: str
    key: str


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
    keys: dict[str, DeviceKey] = Field(default_factory=dict, exclude=True)
    questionnaire_responses: dict[str, list[QuestionnaireResponse]] = Field(
        default_factory=lambda: defaultdict(list), exclude=True
    )

    def update(self, **kwargs) -> DeviceUpdatedEvent:
        device_data = self._update(data=kwargs)
        event = DeviceUpdatedEvent(**device_data)
        return self.add_event(event)

    def delete(self) -> DeviceUpdatedEvent:
        return self.update(status=DeviceStatus.INACTIVE)

    def add_key(self, type: str, key: str) -> DeviceKeyAddedEvent:
        if key in self.keys:
            raise DuplicateError(f"It is forbidden to supply duplicate keys: '{key}'")
        device_key = DeviceKey(key=key, type=type)
        self.keys[key] = device_key
        event = DeviceKeyAddedEvent(id=self.id, **device_key.dict())
        return self.add_event(event)

    def delete_key(self, key: str) -> DeviceKeyDeletedEvent:
        try:
            device_key = self.keys.pop(key)
        except KeyError:
            raise NotFoundError(f"This device does not contain key '{key}'") from None
        event = DeviceKeyDeletedEvent(id=self.id, key=device_key.key)
        return self.add_event(event)

    def add_questionnaire_response(
        self, questionnaire_response: QuestionnaireResponse
    ) -> list[QuestionnaireInstanceEvent, QuestionnaireResponseAddedEvent]:
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
                **questionnaire_response.questionnaire.dict(),
            )
            events.append(self.add_event(questionnaire_event))

        questionnaire_response_event = QuestionnaireResponseAddedEvent(
            entity_id=self.id,
            questionnaire_response_index=questionnaire_response_index,
            questionnaire_id=questionnaire_response.questionnaire.id,
            responses=questionnaire_response.responses,
        )
        events.append(self.add_event(questionnaire_response_event))

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


class DeviceEventDeserializer(EventDeserializer):
    event_types = (
        DeviceCreatedEvent,
        DeviceUpdatedEvent,
        DeviceKeyAddedEvent,
        DeviceKeyDeletedEvent,
        QuestionnaireResponseAddedEvent,
        QuestionnaireResponseUpdatedEvent,
        QuestionnaireResponseDeletedEvent,
        QuestionnaireInstanceEvent,
    )
