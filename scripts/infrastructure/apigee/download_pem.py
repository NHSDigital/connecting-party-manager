import sys
from typing import Literal

import boto3

from test_helpers.aws_session import aws_session
from test_helpers.constants import PROJECT_ROOT
from test_helpers.terraform import read_terraform_output


def _read_pem_data() -> str:
    with aws_session():
        client = boto3.client("secretsmanager")
        aws_environment = read_terraform_output("environment.value")
        secret_name = f"{aws_environment}-apigee-credentials"

        response = client.get_secret_value(SecretId=secret_name)
    return response["SecretString"]


def _save_pem_data(data: str, apigee_stage: Literal["ptl", "prod"]):
    path = (
        PROJECT_ROOT / f"infrastructure/apigee/{apigee_stage}/.proxygen/private_key.pem"
    )
    with open(path, "w") as f:
        f.write(data)
    return path


if __name__ == "__main__":
    _, apigee_stage = sys.argv
    data = _read_pem_data()
    path = _save_pem_data(data=data, apigee_stage=apigee_stage)
    print(f"Downloaded pem to {path}")  # noqa: T201
