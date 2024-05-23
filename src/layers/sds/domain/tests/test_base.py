from contextlib import nullcontext as does_not_raise
from typing import ClassVar, Literal, Optional

import pytest
from etl_utils.ldif.model import DistinguishedName
from pydantic import BaseModel, Field, ValidationError
from sds.domain.base import (
    OBJECT_CLASS_FIELD_NAME,
    AliasLookupError,
    SdsBaseModel,
    _field_is_a_set,
    _force_optional,
    _generate_distinguished_name,
    _get_alias_for_field_name,
    _get_field_name_for_alias,
    _parse_and_validate_field,
    _strip_excluded_values_from_object_class,
    _unpack_sets,
    _validate_object_class,
)


def test__field_is_a_set():
    class MyModel(SdsBaseModel):
        not_a_set: str
        a_set: set[str]

    assert not _field_is_a_set(MyModel, "not_a_set")
    assert _field_is_a_set(MyModel, "a_set")


def test__strip_excluded_values_from_object_class():
    values = {OBJECT_CLASS_FIELD_NAME: {1, 2, 3}}
    _values = _strip_excluded_values_from_object_class(
        cls=None, values=values, excluded_object_class_values={2, 4}
    )
    assert _values == {OBJECT_CLASS_FIELD_NAME: {1, 3}}


def test__unpack_sets():
    class MyModel(SdsBaseModel):
        not_a_set: str
        not_a_set_but_too_many: str
        a_set: set[str]
        another_set: set[str]

    values = {
        "not_a_set": {"abc"},  # not a set, so should be unpacked
        "not_a_set_but_too_many": {"foo", "bar"},  # not a set, but can't be unpacked
        "a_set": {"1"},
        "another_set": {"1", "2", "3"},
    }
    _values = _unpack_sets(cls=MyModel, values=values)

    assert _values == {
        "not_a_set": "abc",  # unpacked
        "not_a_set_but_too_many": {"foo", "bar"},  # not unpacked
        "a_set": {"1"},
        "another_set": {"1", "2", "3"},
    }


def test__generate_distinguished_name():
    values = {
        "_distinguished_name": DistinguishedName(
            parts=(("foo", "bar"),),
        ),
    }
    _values = _generate_distinguished_name(cls=None, values=values)

    assert _values == {
        "distinguished_name": {"foo": "bar"},
    }


def test__generate_distinguished_name_when_not_provided():
    _values = _generate_distinguished_name(cls=None, values={"foo": "bar"})
    assert _values == {"foo": "bar"}


@pytest.mark.parametrize("object_class", ("foo", "FOO", "FoO"))
def test__validate_object_class(object_class):
    class MyModel(SdsBaseModel):
        OBJECT_CLASS: ClassVar[Literal["FoO"]] = "FoO"

    values = {OBJECT_CLASS_FIELD_NAME: object_class}
    _values = _validate_object_class(cls=MyModel, values=values)
    assert _values == values


def test__validate_object_class_fail():
    class MyModel(SdsBaseModel):
        OBJECT_CLASS: ClassVar[Literal["FoO"]] = "FoO"

    values = {OBJECT_CLASS_FIELD_NAME: "bar"}
    with pytest.raises(ValueError):
        _validate_object_class(cls=MyModel, values=values)


def test_alias_fields():
    class MyModel(SdsBaseModel):
        my_aliased_field: str = Field(alias="my-aliased-field")
        my_normal_field: str

    assert set(MyModel.alias_fields().keys()) == {
        "object_class",  # from SdsBaseModel
        "my-aliased-field",
        "changetype",  # from SdsBaseModel
        "my_normal_field",
    }


def test_no_extras():
    class MyModel(SdsBaseModel):
        pass

    with pytest.raises(ValidationError) as exc:
        MyModel(_distinguished_name=None, extra_field="not allowed")
    assert "extra fields not permitted" in exc.value.json()


class MyAliasModel(BaseModel):
    foo: str = Field(alias="bar")


@pytest.mark.parametrize(
    ["function", "input_string", "expected_output", "raises"],
    [
        (_get_field_name_for_alias, "bar", "foo", does_not_raise()),
        (_get_alias_for_field_name, "foo", "bar", does_not_raise()),
        (_get_field_name_for_alias, "foo", None, pytest.raises(AliasLookupError)),
        (_get_alias_for_field_name, "bar", None, pytest.raises(AliasLookupError)),
    ],
)
def test_get_field_name_for_alias(function, input_string, expected_output, raises):
    with raises:
        assert function(MyAliasModel, input_string) == expected_output


def test_force_optional():
    MyOptionalAliasModel = _force_optional(MyAliasModel)
    assert MyOptionalAliasModel is not MyAliasModel
    assert MyOptionalAliasModel.__fields__.keys() == MyAliasModel.__fields__.keys()
    with does_not_raise():
        MyOptionalAliasModel(bar=123)  # alias still works
        MyOptionalAliasModel()  # allowed to skip mandatory fields
    with pytest.raises(ValidationError):
        MyOptionalAliasModel(bar={})  # validation still works


@pytest.mark.parametrize(
    ["field", "value", "raises"],
    [
        ("my_field", "hi", does_not_raise()),
        ("myField", None, pytest.raises(AliasLookupError)),
        ("my_field", {}, pytest.raises(ValidationError)),
    ],
)
def test__parse_and_validate_field(field, value, raises):
    class MyModel(SdsBaseModel):
        my_field: str = Field(alias="myField")
        other_field: str

    with raises:
        _parse_and_validate_field(MyModel, field=field, value=value)


@pytest.mark.parametrize(
    ["field", "is_mandatory"],
    [
        ("my_field", True),
        ("other_field", False),
    ],
)
def test__parse_and_validate_field(field, is_mandatory):
    class MyModel(SdsBaseModel):
        my_field: str = Field(alias="myField")
        other_field: Optional[str]

    assert MyModel.is_mandatory_field(field) is is_mandatory


@pytest.mark.parametrize(
    ["field", "is_key_field"],
    [
        ("my_field", True),
        ("other_field", False),
    ],
)
def test_key_fields(field, is_key_field):
    class MyModel(SdsBaseModel):
        my_field: str = Field(alias="myField")
        other_field: Optional[str]

        @classmethod
        def key_fields(cls) -> tuple[str, ...]:
            return ("my_field",)

    assert MyModel.is_key_field(field) is is_key_field
