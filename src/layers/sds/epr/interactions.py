from typing import Counter

from domain.core.error import DuplicateInteractionIdError
from domain.core.questionnaire.v1 import QuestionnaireResponse

from .constants import SdsFieldName


def check_no_duplicate_interactions(
    questionnaire_responses: list[QuestionnaireResponse],
):
    interaction_counts = Counter(
        qr.data[SdsFieldName.INTERACTION_ID] for qr in questionnaire_responses
    )
    for interaction, count in interaction_counts.most_common():
        if count > 1:
            raise DuplicateInteractionIdError(
                f"Duplicate '{SdsFieldName.INTERACTION_ID}' provided: "
                f"value '{interaction}' occurs {count} times in the input."
            )
