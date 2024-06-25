from types import FunctionType

from event.step_chain.errors import StepChainError

from .types import FrozenDict


class StepChain:
    """
    Function ("step") chaining with the following features:
        * Steps run in sequence
        * Steps expected to have the signature `f(data, cache) -> any`
        * Can access results of previous steps using `data[step]`
        * Can access "global" data from `cache`
        * Can apply decorators to all steps
        * Execute the pipeline with `StepChain.run`
        * Retrieve the final step's result from the `result` member

    Example:

        def a(data, cache):
            return {"blah", "hi"}

        def b(data, cache):
            return {"a's result": data[a]}

        step_chain = StepChain([a, b], step_decorators=[])
        step_chain.run(cache={}, init={"event": None})
        print(step_chain.data)
    """

    INIT = "INIT"

    def __init__(
        self, step_chain: list[FunctionType], step_decorators: list[FunctionType] = None
    ):
        if step_decorators is None:
            step_decorators = []

        if len(step_chain) != len(set(step_chain)):
            raise StepChainError(
                f"Duplicate step detected in step chain '{[step.__name__ for step in step_chain]}'"
            )

        # Decorate the steps in "reverse" order, which actually means that
        # they get applied in the logical order
        decorated_steps = step_chain
        for deco in reversed(step_decorators):
            decorated_steps = list(map(deco, decorated_steps))
        self.step_chain = decorated_steps

        # Store a mapping to the original unwrapped steps, so that the user
        # may look up data by the original step reference
        self.naked_step_lookup = dict(zip(decorated_steps, step_chain))

    def run(self, cache: dict = None, init: any = None):
        if cache is None:
            cache = {}

        data = FrozenDict(**{self.INIT: init})
        for step in self.step_chain:
            try:
                result = step(data=data, cache=cache)
            except Exception as exception:
                result = exception
            naked_step = self.naked_step_lookup[step]  # unwrap decorators off the step
            data = FrozenDict({**data, naked_step: result})
            if isinstance(result, Exception):
                break

        self.data = data
        self.result = result
