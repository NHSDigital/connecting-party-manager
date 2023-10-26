import os
from unittest import mock


def test_index():
    with mock.patch.dict(os.environ, {"SOMETHING": "hiya"}, clear=True):
        import api.authoriser.index as index

        result = index.handler(event={"methodArn": "foo"})
    assert result == {
        "principalId": index.__file__,
        "context": {},
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": "foo",
                }
            ],
        },
    }
