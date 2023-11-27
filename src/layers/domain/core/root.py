from .ods_organisation import OdsOrganisation
from .questionnaire import Questionnaire


class Root:
    """
    Domain entities that have no parent are created by this Root entity, in
    order to preserve the rule that all Aggregate Roots are created by other
    Aggregate Roots.
    """

    @staticmethod
    def create_ods_organisation(ods_code: str, name: str) -> OdsOrganisation:
        return OdsOrganisation(ods_code=ods_code, name=name)

    @staticmethod
    def create_questionnaire(id: str, name: str) -> Questionnaire:
        return Questionnaire(id=id, name=name)
