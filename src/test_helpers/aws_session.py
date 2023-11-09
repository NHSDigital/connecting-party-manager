import os
from contextlib import contextmanager
from datetime import datetime
from functools import cache
from typing import Generator

import boto3

from test_helpers.terraform import read_terraform_output

DEFAULT_WORKSPACE = "dev"
SECRET_ID = "nhse-cpm--mgmt--{env}-account-id-v1.0.0"


def _aws_account_id_from_secret(env: str):
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=SECRET_ID.format(env=env))
    return response["SecretString"]


def _get_access_token(account_id: str = None):
    sts_client = boto3.client("sts")
    current_time = datetime.utcnow().timestamp()
    response = sts_client.assume_role(
        RoleArn=f"arn:aws:iam::{account_id}:role/NHSDeploymentRole",
        RoleSessionName=f"role--{current_time}",
    )

    access_key_id = response["Credentials"]["AccessKeyId"]
    secret_access_key = response["Credentials"]["SecretAccessKey"]
    session_token = response["Credentials"]["SessionToken"]
    return access_key_id, secret_access_key, session_token


@cache
def aws_session_env_vars() -> boto3.Session:
    env = read_terraform_output("environment.value")
    account_id = _aws_account_id_from_secret(env=env)
    access_key_id, secret_access_key, session_token = _get_access_token(
        account_id=account_id
    )
    return {
        "AWS_ACCESS_KEY_ID": access_key_id,
        "AWS_SECRET_ACCESS_KEY": secret_access_key,
        "AWS_SESSION_TOKEN": session_token,
    }


@contextmanager
def aws_session() -> Generator[None, None, None]:
    original_env = dict(os.environ)
    env_vars = aws_session_env_vars()

    exception = None
    try:
        boto3.DEFAULT_SESSION = None
        os.environ.update(env_vars)
        yield
    except Exception as _exception:
        exception = _exception
    finally:
        boto3.DEFAULT_SESSION = None
        os.environ = original_env

    if exception:
        raise exception
