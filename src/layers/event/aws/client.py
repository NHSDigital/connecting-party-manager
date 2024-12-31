from typing import TYPE_CHECKING

import boto3

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBClient
    from mypy_boto3_secretsmanager import SecretsManagerClient


def dynamodb_client() -> "DynamoDBClient":
    """Explicitly pull this out so that it can be mocked globally"""
    return boto3.client("dynamodb")


def secretsmanager_client() -> "SecretsManagerClient":
    """Explicitly pull this out so that it can be mocked globally"""
    return boto3.client("secretsmanager")
