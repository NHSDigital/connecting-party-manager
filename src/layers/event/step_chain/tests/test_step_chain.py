from functools import wraps

import pytest
from event.step_chain import StepChain
from event.step_chain.errors import StepChainError
from event.step_chain.types import FrozenDict


def test_step_chain():
    cache = {"foo": "FOO"}

    def a(data, cache):
        cache["foo"] = "OOF"
        cache["bar"] = "BAR"
        return {"blah", "hi"}

    def b(data, cache):
        cache["foo"] = "fool"
        return {"a's result": data[a]}

    step_chain = StepChain(step_chain=[a, b], step_decorators=[])
    step_chain.run(cache=cache, init={"event": None})

    assert step_chain.result == {"a's result": {"blah", "hi"}}
    assert step_chain.data == FrozenDict(
        {
            StepChain.INIT: {"event": None},
            a: {"blah", "hi"},
            b: {"a's result": {"blah", "hi"}},
        }
    )
    assert cache == {"foo": "fool", "bar": "BAR"}


def test_step_chain_with_error():
    cache = {}

    class MyException(Exception):
        pass

    my_exception = MyException()

    def a(data, cache):
        raise my_exception

    def b(data, cache):
        return {"a's result": data[a]}

    step_chain = StepChain(step_chain=[a, b], step_decorators=[])
    step_chain.run(cache=cache, init={"event": None})

    assert isinstance(step_chain.result, MyException)
    assert step_chain.data == FrozenDict(
        {StepChain.INIT: {"event": None}, a: my_exception}
    )


def test_step_chain_with_decorators():
    cache = {}

    def mutate_cache(function):
        @wraps(function)
        def wrapper(data, cache):
            cache["foo"] = cache.get("foo", "") + "foo"
            return function(data=data, cache=cache)

        return wrapper

    def also_mutate_cache(function):
        @wraps(function)
        def wrapper(data, cache):
            cache["foo"] = cache.get("foo", "") + "bar"
            return function(data=data, cache=cache)

        return wrapper

    def a(data, cache):
        return {"cache_contents": dict(cache)}

    def b(data, cache):
        return {"cache_contents": dict(cache)}

    step_chain = StepChain(
        step_chain=[a, b], step_decorators=[mutate_cache, also_mutate_cache]
    )
    step_chain.run(cache=cache)

    assert step_chain.result == {"cache_contents": {"foo": "foobarfoobar"}}
    assert step_chain.data == FrozenDict(
        {
            StepChain.INIT: None,
            a: {"cache_contents": {"foo": "foobar"}},
            b: {"cache_contents": {"foo": "foobarfoobar"}},
        }
    )
    assert cache == {"foo": "foobarfoobar"}


def test_step_chain_no_duplicate_steps_allowed():
    def a():
        pass

    with pytest.raises(StepChainError):
        StepChain(step_chain=[a, a])
