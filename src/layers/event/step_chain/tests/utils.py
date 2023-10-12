from event.step_chain import StepChain
from event.step_chain.types import FrozenDict


def step_data(init=None, kwargs=None):
    data = {StepChain.INIT: init}
    if kwargs is None:
        kwargs = {}
    data.update(kwargs)
    return FrozenDict(data)
