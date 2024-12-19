from collections import defaultdict
from datetime import datetime
from uuid import UUID, uuid4

from attr import dataclass
from domain.core.aggregate_root import AggregateRoot, event
from domain.core.cpm_system_id import ProductId
from domain.core.device import DuplicateQuestionnaireResponse
from domain.core.device.v1 import QuestionnaireResponseNotFoundError
from domain.core.enum import Status
from domain.core.event import Event, EventDeserializer
from domain.core.questionnaire import QuestionnaireResponse
from domain.core.timestamp import now
from domain.core.validation import DEVICE_NAME_REGEX
from pydantic import Field


@dataclass(kw_only=True, slots=True)
class DeviceReferenceDataCreatedEvent(Event):
    id: str
    name: str
    status: Status
    product_id: ProductId
    product_team_id: UUID
    ods_code: str
    created_on: str
    updated_on: str = None
    deleted_on: str = None


@dataclass(kw_only=True, slots=True)
class QuestionnaireResponseUpdatedEvent(Event):
    """
    This is adding the inital questionnaire response from the event body request.
    """

    id: str
    questionnaire_responses: dict[str, list[QuestionnaireResponse]]
    updated_on: str = None


class DeviceReferenceData(AggregateRoot):
    """An object to hold boilerplate Device QuestionnaireResponses"""

    id: UUID = Field(default_factory=uuid4, immutable=True)
    name: str = Field(regex=DEVICE_NAME_REGEX)
    status: Status = Field(default=Status.ACTIVE)
    product_id: ProductId = Field(immutable=True)
    product_team_id: str = Field(immutable=True)
    ods_code: str = Field(immutable=True)
    questionnaire_responses: dict[str, list[QuestionnaireResponse]] = Field(
        default_factory=lambda: defaultdict(list)
    )
    created_on: datetime = Field(default_factory=now, immutable=True)
    updated_on: datetime | None = Field(default=None)
    deleted_on: datetime | None = Field(default=None)

    @event
    def add_questionnaire_response(
        self, questionnaire_response: QuestionnaireResponse
    ) -> QuestionnaireResponseUpdatedEvent:
        questionnaire_id = questionnaire_response.questionnaire_id
        questionnaire_responses = self.questionnaire_responses[questionnaire_id]

        current_created_ons = {qr.created_on for qr in questionnaire_responses}
        if questionnaire_response.created_on in current_created_ons:
            raise DuplicateQuestionnaireResponse(
                "This Device already contains a "
                f"response created on {questionnaire_response.created_on.isoformat()}"
                f"for Questionnaire {questionnaire_id}"
            )
        questionnaire_responses.append(questionnaire_response)

        return QuestionnaireResponseUpdatedEvent(
            id=self.id,
            questionnaire_responses={
                q_name: [qr.dict() for qr in qrs]
                for q_name, qrs in self.questionnaire_responses.items()
            },
        )

    @event
    def remove_questionnaire(
        self, questionnaire_id: str
    ) -> QuestionnaireResponseUpdatedEvent:
        self.questionnaire_responses[questionnaire_id] = []
        return QuestionnaireResponseUpdatedEvent(
            id=self.id,
            questionnaire_responses={
                q_name: [qr.dict() for qr in qrs]
                for q_name, qrs in self.questionnaire_responses.items()
            },
        )

    @event
    def remove_questionnaire_response(
        self, questionnaire_id: str, questionnaire_response_id: str
    ) -> QuestionnaireResponseUpdatedEvent:
        qid_to_remove = str(questionnaire_response_id)
        questionnaire_response_ids = [
            str(qr.id) for qr in self.questionnaire_responses[questionnaire_id]
        ]

        try:
            idx_to_remove = questionnaire_response_ids.index(qid_to_remove)
        except ValueError:
            raise QuestionnaireResponseNotFoundError(
                f"Could not find QuestionnaireResponse {qid_to_remove}"
            )
        else:
            self.questionnaire_responses[questionnaire_id].pop(idx_to_remove)

        return QuestionnaireResponseUpdatedEvent(
            id=self.id,
            questionnaire_responses={
                q_name: [qr.dict() for qr in qrs]
                for q_name, qrs in self.questionnaire_responses.items()
            },
        )


class DeviceReferenceDataEventDeserializer(EventDeserializer):
    event_types = (
        DeviceReferenceDataCreatedEvent,
        QuestionnaireResponseUpdatedEvent,
    )
