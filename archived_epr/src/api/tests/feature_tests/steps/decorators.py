from functools import wraps
from types import FunctionType

from behave import given as _given
from behave import then as _then
from behave import when as _when

from api.tests.feature_tests.steps.context import Context
from api.tests.feature_tests.steps.postman import notes_as_postman_vars
from api.tests.feature_tests.steps.table import expand_macro


def _behave_decorator(description: str, behave_decorator: FunctionType) -> FunctionType:
    _deco = behave_decorator(description)

    def deco(fn):
        @wraps(fn)
        def wrapper(context: Context, **kwargs):
            endpoint = kwargs.get("endpoint")
            if endpoint:
                context.postman_endpoint = notes_as_postman_vars(endpoint)
                kwargs["endpoint"] = expand_macro(endpoint, context=context)
            return fn(context, **kwargs)

        return _deco(wrapper)

    return deco


def given(description: str):
    return _behave_decorator(description=description, behave_decorator=_given)


def when(description: str):
    return _behave_decorator(description=description, behave_decorator=_when)


def then(description: str):
    return _behave_decorator(description=description, behave_decorator=_then)
