from functools import cache

import boto3


@cache
def dynamodb_client():
    """Explicitly pull this out so that it can be mocked globally"""
    return boto3.client("dynamodb")
