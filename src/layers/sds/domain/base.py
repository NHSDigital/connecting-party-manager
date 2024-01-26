from typing import ClassVar, Literal

from etl_utils.ldif.model import DistinguishedName
from pydantic import BaseModel, Extra, root_validator
from pydantic.fields import ModelField

OBJECT_CLASS_FIELD_NAME = "objectclass"
_EXCLUDED_OBJECT_CLASS_VALUES = {"nhsExternalChangelogEntry", "top"}
_EXCLUDED_OBJECT_CLASS_VALUES_LOWER = set(map(str.lower, _EXCLUDED_OBJECT_CLASS_VALUES))
EXCLUDED_OBJECT_CLASS_VALUES = (
    _EXCLUDED_OBJECT_CLASS_VALUES | _EXCLUDED_OBJECT_CLASS_VALUES_LOWER
)
SET_ALIAS_NAME = f"{set[str]}"


def _field_is_a_set(cls: "SdsBaseModel", field_name) -> bool:
    field = cls.alias_fields().get(field_name)
    return field is not None and str(field.outer_type_) == SET_ALIAS_NAME


def _strip_excluded_values_from_object_class(
    cls: "SdsBaseModel",
    values: dict,
    excluded_object_class_values=EXCLUDED_OBJECT_CLASS_VALUES,
) -> dict:
    object_class = values.get(OBJECT_CLASS_FIELD_NAME)
    if object_class:
        values[OBJECT_CLASS_FIELD_NAME] = object_class - excluded_object_class_values
    return values


def _unpack_sets(cls: "SdsBaseModel", values: dict) -> dict:
    _values = {}
    for field_name, field_values in values.items():
        if (
            isinstance(field_values, set)
            and len(field_values) == 1
            and not _field_is_a_set(cls=cls, field_name=field_name)
        ):
            (v,) = field_values
        else:
            v = field_values
        _values[field_name] = v
    return _values


def _generate_distinguished_name(cls: "SdsBaseModel", values: dict) -> dict:
    _distinguished_name: DistinguishedName = values.pop("_distinguished_name")
    if _distinguished_name is not None:
        values["distinguished_name"] = dict(_distinguished_name.parts)
    return values


def _validate_object_class(cls: "SdsBaseModel", values: dict) -> dict:
    object_class: str = values.get(OBJECT_CLASS_FIELD_NAME)
    if object_class and not cls.matches_object_class(object_class=object_class):
        raise ValueError(
            f"'{OBJECT_CLASS_FIELD_NAME}' (value '{object_class}') must equal {cls.OBJECT_CLASS}"
        )
    return values


class SdsBaseModel(BaseModel):
    _distinguished_name: DistinguishedName
    OBJECT_CLASS: ClassVar[Literal[""]] = ""
    object_class: Literal[""]

    class Config:
        extra = Extra.forbid
        allow_population_by_field_name = True

    @classmethod
    def matches_object_class(cls, object_class: str) -> bool:
        return object_class.lower() == cls.OBJECT_CLASS.lower()

    @classmethod
    def alias_fields(cls) -> dict[str, ModelField]:
        return {
            (model_field.alias if model_field.alias else model_field): model_field
            for model_field in cls.__fields__.values()
        }

    @root_validator(pre=True)
    def preprocess_inputs(cls, values):
        for transform in (
            _generate_distinguished_name,
            _strip_excluded_values_from_object_class,
            _unpack_sets,
            _validate_object_class,
        ):
            values = transform(cls=cls, values=values)
        return values
