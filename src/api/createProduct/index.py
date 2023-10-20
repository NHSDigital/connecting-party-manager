from event.environment import BaseEnvironment
from event.logging.logger import setup_logger
from event.logging.step_decorators import logging_step_decorators
from event.response.steps import response_steps
from event.step_chain import StepChain
from event.versioning.steps import get_steps_for_requested_version, versioning_steps


class Environment(BaseEnvironment):
    SOMETHING: str


cache = {**Environment.build().dict()}
step_decorators = [*logging_step_decorators]
pre_steps = [*versioning_steps]
post_steps = [*response_steps]


def handler(event: dict, context=None):
    setup_logger(service_name=__file__)

    pre_step_chain = StepChain(
        step_chain=versioning_steps, step_decorators=step_decorators
    )
    pre_step_chain.run(init={"event": event, "api_index_file_path": __file__})

    if isinstance(pre_step_chain.result, Exception):
        result = pre_step_chain.result
    else:
        steps = pre_step_chain.data[get_steps_for_requested_version]
        step_chain = StepChain(step_chain=steps, step_decorators=step_decorators)
        step_chain.run(cache=cache, init=event)
        result = step_chain.result

    post_step_chain = StepChain(step_chain=post_steps, step_decorators=step_decorators)
    post_step_chain.run(init=result)
    return post_step_chain.result
