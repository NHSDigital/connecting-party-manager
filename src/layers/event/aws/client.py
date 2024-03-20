import boto3


def dynamodb_client():
    """Explicitly pull this out so that it can be mocked globally"""
    return boto3.client("dynamodb")


def secretsmanager_client():
    """Explicitly pull this out so that it can be mocked globally"""
    return boto3.client("secretsmanager")
