import pytest
from domain.fhir.r4.cpm_model import Organization
from pydantic import ValidationError


@pytest.mark.parametrize(
    "data",
    [
        (
            {
                "resourceType": "",
                "id": "org123",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
            }
        ),
        (
            {
                "resourceType": None,
                "id": "org123",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
            }
        ),
        (
            {
                "resourceType": "foobar",
                "id": "org123",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": "",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": None,
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": "org123",
                "name": "",
                "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": "org123",
                "name": None,
                "partOf": {"identifier": {"id": "parent_org", "value": "Parent Org"}},
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": "org123",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "", "value": "Parent Org"}},
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": "org123",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": None, "value": "Parent Org"}},
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": "org123",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "parent_org", "value": ""}},
            }
        ),
        (
            {
                "resourceType": "Organization",
                "id": "org123",
                "name": "Example Organization",
                "partOf": {"identifier": {"id": "parent_org", "value": None}},
            }
        ),
    ],
)
def test_organization_null_string_validates_failure(data):
    with pytest.raises(ValidationError):
        Organization(**data)
