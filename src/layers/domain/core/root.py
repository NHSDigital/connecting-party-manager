from .ods_organisation import OdsOrganisation
from .questionnaire import Questionnaire
from .user import User


class Root:
    """
    Domain entities that have no parent are created by this Root entity, in
    order to preserve the rule that all Aggregate Roots are created by other
    Aggregate Roots.
    """

    @staticmethod
    def create_ods_organisation(id: str, name: str) -> OdsOrganisation:
        return OdsOrganisation(id, name)

    @staticmethod
    def create_user(id: str, name: str) -> User:
        return User(id, name)

    @staticmethod
    def create_questionnaire(id: str, name: str) -> Questionnaire:
        return Questionnaire(id, name)
