from event.environment import BaseEnvironment
from event.logging.logger import setup_logger
from event.logging.step_decorators import logging_step_decorators
from event.step_chain import StepChain


class Environment(BaseEnvironment):
    pass


def do_some_auth(data, cache):
    return True


def render_policy(data, cache):
    authoriser_result = data["INIT"]["result"]
    method_arn = data["INIT"]["method_arn"]

    failure_raised = isinstance(authoriser_result, Exception)
    effect = "Deny" if failure_raised else "Allow"
    context = {"error": authoriser_result} if failure_raised else {}
    return {
        "principalId": __file__,
        "context": context,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": method_arn,
                }
            ],
        },
    }


cache = {**Environment.build().dict()}
step_decorators = [*logging_step_decorators]


def handler(event, context=None):
    setup_logger(service_name=__file__)

    step_chain = StepChain(step_chain=[do_some_auth], step_decorators=step_decorators)
    step_chain.run(cache=cache, init=event)

    post_step_chain = StepChain(
        step_chain=[render_policy], step_decorators=step_decorators
    )
    post_step_chain.run(
        init={"result": step_chain.result, "method_arn": event["methodArn"]}
    )
    return post_step_chain.result
