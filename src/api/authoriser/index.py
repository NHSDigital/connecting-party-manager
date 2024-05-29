import boto3
from domain.logging.step_decorators import logging_step_decorators
from event.environment import BaseEnvironment
from event.logging.logger import setup_logger
from event.step_chain import StepChain

from api.authoriser.errors import AuthoriserError


class Environment(BaseEnvironment):
    ENVIRONMENT: str


environment = Environment.build()
CLIENT = boto3.client("secretsmanager")


def _read_cpm_apikey() -> str:
    secret_name = f"{environment.ENVIRONMENT}-apigee-cpm-apikey"
    response = CLIENT.get_secret_value(SecretId=secret_name)
    return response["SecretString"]


def authenticate_apikey(data, cache):
    provided_apikey = data["INIT"]["headers"]["apikey"]
    cpm_apikey_value = _read_cpm_apikey()

    if provided_apikey != cpm_apikey_value:
        raise AuthoriserError(
            "Provided apikey in request does not match the Connecting Party Manager apikey"
        )

    return True


def render_policy(data, cache):
    authoriser_result = data["INIT"]["result"]
    method_arn = data["INIT"]["method_arn"]

    failure_raised = isinstance(authoriser_result, Exception)
    effect = "Deny" if failure_raised else "Allow"
    context = {"error": str(authoriser_result)} if failure_raised else {}
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

    step_chain = StepChain(
        step_chain=[authenticate_apikey], step_decorators=step_decorators
    )
    step_chain.run(cache=cache, init=event)

    post_step_chain = StepChain(
        step_chain=[render_policy], step_decorators=step_decorators
    )
    post_step_chain.run(
        init={"result": step_chain.result, "method_arn": event["methodArn"]}
    )
    return post_step_chain.result
