from typing import ClassVar, Literal, Self

import orjson
from etl_utils.ldif.model import DistinguishedName
from pydantic import BaseModel, Extra, Field, root_validator
from pydantic.fields import ModelField
from sds.domain.constants import ChangeType

OBJECT_CLASS_FIELD_NAME = "objectclass"
_EXCLUDED_OBJECT_CLASS_VALUES = {"nhsExternalChangelogEntry", "top"}
_EXCLUDED_OBJECT_CLASS_VALUES_LOWER = set(map(str.lower, _EXCLUDED_OBJECT_CLASS_VALUES))
_EXCLUDED_OBJECT_CLASS_VALUES_TITLE = set(map(str.title, _EXCLUDED_OBJECT_CLASS_VALUES))
_EXCLUDED_OBJECT_CLASS_VALUES_UPPER = set(map(str.upper, _EXCLUDED_OBJECT_CLASS_VALUES))
EXCLUDED_OBJECT_CLASS_VALUES = (
    _EXCLUDED_OBJECT_CLASS_VALUES
    | _EXCLUDED_OBJECT_CLASS_VALUES_LOWER
    | _EXCLUDED_OBJECT_CLASS_VALUES_TITLE
    | _EXCLUDED_OBJECT_CLASS_VALUES_UPPER
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
    _object_class = values.get(OBJECT_CLASS_FIELD_NAME)
    object_class = set(_object_class) if _object_class else _object_class
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
    _distinguished_name: DistinguishedName = values.pop("_distinguished_name", None)
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


def _is_iterable(obj):
    return isinstance(obj, (set, list, tuple))


def orjson_dumps(v, *, default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


class SdsBaseModel(BaseModel):
    _distinguished_name: DistinguishedName
    OBJECT_CLASS: ClassVar[Literal[""]] = ""
    object_class: Literal[""]
    change_type: ChangeType = Field(alias="changetype", default=ChangeType.ADD)

    class Config:
        extra = Extra.forbid
        allow_population_by_field_name = True
        json_dumps = orjson_dumps

    @classmethod
    def matches_object_class(cls, object_class: str) -> bool:
        return object_class.lower() == cls.OBJECT_CLASS.lower()

    @classmethod
    def alias_fields(cls) -> dict[str, ModelField]:
        return {
            (model_field.alias if model_field.alias else model_field): model_field
            for model_field in cls.__fields__.values()
        }

    @classmethod
    def get_field_name_for_alias(cls, alias) -> str:
        try:
            (field_name,) = (
                field_name
                for field_name, model_field in cls.__fields__.items()
                if model_field.alias == alias
            )
        except ValueError:
            raise ValueError(f"No field with alias '{alias}' found")
        return field_name

    @classmethod
    def get_alias_for_field_name(cls, field) -> str:
        (field_name,) = (
            model_field.alias
            for field_name, model_field in cls.__fields__.items()
            if field_name == field
        )
        return field_name

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

    def as_questionnaire_response_responses(self) -> list[dict[str, list]]:
        data = orjson.loads(self.json(exclude_none=True, exclude={"change_type"}))
        return [{k: (v if _is_iterable(v) else [v])} for k, v in data.items()]

    @classmethod
    def force_optional(cls) -> type[Self]:
        _model = type(f"{cls.__name__}-subclass", (cls,), {})
        for field in _model.__fields__.values():
            field.required = False
        return _model

    @classmethod
    def parse_and_validate_field(cls, field: str, value: list | set):
        _model = cls.force_optional()
        field_alias = cls.get_alias_for_field_name(field=field)
        _value = set(value) if isinstance(value, list) else value
        instance = _model(**{field_alias: _value})
        parsed_value = getattr(instance, field)
        return parsed_value

    @classmethod
    def is_mandatory_field(cls, field: str):
        return cls.__fields__[field].required
