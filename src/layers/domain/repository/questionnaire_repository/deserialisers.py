from domain.core.questionnaire import custom_rules
from domain.core.questionnaire.v1 import ALLOWED_ANSWER_TYPES_LOOKUP, NoSuchQuestionType


def _deserialise_answer_type(
    answer_type_name: str,
    allowed_answer_types_lookup: dict = ALLOWED_ANSWER_TYPES_LOOKUP,
) -> type:
    try:
        return allowed_answer_types_lookup[answer_type_name]
    except KeyError:
        raise NoSuchQuestionType(answer_type_name)


def _deserialise_answer_types(answer_type_names: list[str]) -> set[type]:
    return set(map(_deserialise_answer_type, answer_type_names))


def _deserialise_rule(rule_name: str, rules=custom_rules):
    return getattr(rules, rule_name)


def _deserialise_rules(rule_names: list[str]):
    return list(map(_deserialise_rule, rule_names))


QUESTION_DESERIALISERS = {
    "answer_types": _deserialise_answer_types,
    "validation_rules": _deserialise_rules,
}
