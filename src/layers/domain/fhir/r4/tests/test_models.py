import pytest
from domain.fhir.r4.cpm_model import ContactPoint, Organization
from pydantic import ValidationError


def test_contactpoint_email_validates_failure():
    with pytest.raises(ValidationError):
        result = ContactPoint(system="email", value="foobar")


def test_organization_email_validates_failure():
    invalid_email_organization_data = {
        "resourceType": "Organization",
        "id": "org123",
        "name": "Example Organization",
        "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
        "contact": [
            {
                "name": {"text": "Mr Foobar"},
                "telecom": [{"system": "email", "value": "invalid_email"}],
            }
        ],
    }
    with pytest.raises(ValidationError):
        Organization(**invalid_email_organization_data)


@pytest.mark.parametrize(
    "data",
    [
        (
            {
                "resourceType": "Organization",
                "id": "org123",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
                "contact": [],
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": "org123",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
                "contact": [
                    {
                        "name": {"text": "Mr Foobar"},
                        "telecom": [{"system": "email", "value": "test@email.com"}],
                    },
                    {
                        "name": {"text": "Mr Foobar"},
                        "telecom": [{"system": "email", "value": "test@email.com"}],
                    },
                ],
            }
        ),
    ],
)
def test_organization_contact_validates_one_item_failure(data):
    with pytest.raises(ValidationError):
        Organization(**data)


@pytest.mark.parametrize(
    "data",
    [
        (
            {
                "resourceType": "",
                "id": "org123",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
                "contact": [
                    {
                        "name": {"text": "Mr Foobar"},
                        "telecom": [{"system": "email", "value": "test@email.com"}],
                    }
                ],
            }
        ),
        (
            {
                "resourceType": None,
                "id": "org123",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
                "contact": [
                    {
                        "name": {"text": "Mr Foobar"},
                        "telecom": [{"system": "email", "value": "test@email.com"}],
                    }
                ],
            }
        ),
        (
            {
                "resourceType": "foobar",
                "id": "org123",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
                "contact": [
                    {
                        "name": {"text": "Mr Foobar"},
                        "telecom": [{"system": "email", "value": "test@email.com"}],
                    }
                ],
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": "",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
                "contact": [
                    {
                        "name": {"text": "Mr Foobar"},
                        "telecom": [{"system": "email", "value": "test@email.com"}],
                    }
                ],
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": None,
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
                "contact": [
                    {
                        "name": {"text": "Mr Foobar"},
                        "telecom": [{"system": "email", "value": "test@email.com"}],
                    }
                ],
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": "org123",
                "name": "",
                "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
                "contact": [
                    {
                        "name": {"text": "Mr Foobar"},
                        "telecom": [{"system": "email", "value": "test@email.com"}],
                    }
                ],
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": "org123",
                "name": None,
                "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
                "contact": [
                    {
                        "name": {"text": "Mr Foobar"},
                        "telecom": [{"system": "email", "value": "test@email.com"}],
                    }
                ],
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": "org123",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "", "value": "Parent Org"}},
                "contact": [
                    {
                        "name": {"text": "Mr Foobar"},
                        "telecom": [{"system": "email", "value": "test@email.com"}],
                    }
                ],
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": "org123",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": None, "value": "Parent Org"}},
                "contact": [
                    {
                        "name": {"text": "Mr Foobar"},
                        "telecom": [{"system": "email", "value": "test@email.com"}],
                    }
                ],
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": "org123",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "parent_org", "value": ""}},
                "contact": [
                    {
                        "name": {"text": "Mr Foobar"},
                        "telecom": [{"system": "email", "value": "test@email.com"}],
                    }
                ],
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": "org123",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "parent_org", "value": None}},
                "contact": [
                    {
                        "name": {"text": "Mr Foobar"},
                        "telecom": [{"system": "email", "value": "test@email.com"}],
                    }
                ],
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": "org123",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
                "contact": [
                    {
                        "name": {"text": ""},
                        "telecom": [{"system": "email", "value": "test@email.com"}],
                    }
                ],
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": "org123",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
                "contact": [
                    {
                        "name": {"text": None},
                        "telecom": [{"system": "email", "value": "test@email.com"}],
                    }
                ],
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": "org123",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
                "contact": [
                    {
                        "name": {"text": "Mr Foobar"},
                        "telecom": [{"system": "", "value": "test@email.com"}],
                    }
                ],
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": "org123",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
                "contact": [
                    {
                        "name": {"text": "Mr Foobar"},
                        "telecom": [{"system": None, "value": "test@email.com"}],
                    }
                ],
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": "org123",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
                "contact": [
                    {
                        "name": {"text": "Mr Foobar"},
                        "telecom": [{"system": "telephone", "value": "test@email.com"}],
                    }
                ],
            }
        ),
    ],
)
def test_organization_null_string_validates_failure(data):
    with pytest.raises(ValidationError):
        Organization(**data)
