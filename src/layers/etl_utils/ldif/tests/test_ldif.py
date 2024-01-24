from io import BytesIO, StringIO
from tempfile import NamedTemporaryFile
from unittest import mock

import pytest
from etl_utils.ldif.ldif import (
    DistinguishedName,
    filter_ldif_from_s3_by_property,
    parse_ldif,
)
from pytest_lazyfixture import lazy_fixture

# Lifted from https://ldap.com/ldif-the-ldap-data-interchange-format/
SAMPLE_LDIF_DATA = """
# Add an entry
dn: ou=test,dc=example,dc=com
changetype: add
objectClass: top
objectClass: organizationalUnit
ou: test

# Modify an entry
dn: ou=test,dc=example,dc=com
changetype: modify
add: description
description: First description value
description: Second description value
-
replace: postalCode
postalCode: 12345
-
delete: seeAlso
-

# Delete an entry
dn: ou=test,dc=example,dc=com
changetype: delete
"""

SAMPLE_LDIF_DATA_MODIFY = """
# Modify an entry
dn: ou=test,dc=example,dc=com
changetype: modify
add: description
description: First description value
description: Second description value
-
replace: postalCode
postalCode: 12345
-
delete: seeAlso
-
"""

PARSED_SAMPLE_LDIF = [
    (
        DistinguishedName(parts=(("dc", "com"), ("dc", "example"), ("ou", "test"))),
        {
            "changetype": {"add"},
            "objectclass": {"organizationalUnit", "top"},
            "ou": {"test"},
        },
    ),
    (
        DistinguishedName(parts=(("dc", "com"), ("dc", "example"), ("ou", "test"))),
        {
            "add": {"description"},
            "changetype": {"modify"},
            "delete": {"seeAlso"},
            "description": {"First description value", "Second description value"},
            "postalcode": {"12345"},
            "replace": {"postalCode"},
        },
    ),
    (
        DistinguishedName(parts=(("dc", "com"), ("dc", "example"), ("ou", "test"))),
        {
            "changetype": {"delete"},
        },
    ),
]


@pytest.fixture
def sample_ldif_data_as_filepath():
    with NamedTemporaryFile() as f:
        f.write(SAMPLE_LDIF_DATA.encode())
        f.seek(0)
        yield f.name


@pytest.mark.parametrize(
    ("raw_distinguished_name", "parsed_distinguished_name"),
    (
        [
            "foo=FOO",
            DistinguishedName(
                parts=(("foo", "FOO"),),
            ),
        ],
        [
            "foo=FOO,bar.baz=BAR.BAZ",
            DistinguishedName(
                parts=(
                    ("bar.baz", "BAR.BAZ"),
                    ("foo", "FOO"),
                ),
            ),
        ],
    ),
)
def test_distinguished_name(raw_distinguished_name, parsed_distinguished_name):
    distinguished_name = DistinguishedName.parse(raw_distinguished_name)
    assert distinguished_name == parsed_distinguished_name


@pytest.mark.parametrize(
    ("file_opener", "path_or_data"),
    (
        [StringIO, SAMPLE_LDIF_DATA],
        [BytesIO, SAMPLE_LDIF_DATA.encode()],
        [open, lazy_fixture("sample_ldif_data_as_filepath")],
    ),
)
def test_parse_ldif(file_opener, path_or_data):
    parsed_ldif = list(parse_ldif(file_opener=file_opener, path_or_data=path_or_data))
    assert parsed_ldif == PARSED_SAMPLE_LDIF


@mock.patch(
    "etl_utils.ldif.ldif._smart_open", return_value=BytesIO(SAMPLE_LDIF_DATA.encode())
)
def test_filter_ldif_from_s3_by_property(mocked_open):
    filtered_ldif = filter_ldif_from_s3_by_property(
        bucket="dummy_bucket", key="dummy_key", filter_terms=[("changeType", "Modify")]
    )
    assert filtered_ldif.tobytes().decode() == SAMPLE_LDIF_DATA_MODIFY

    ((modify_record),) = parse_ldif(file_opener=BytesIO, path_or_data=filtered_ldif)

    assert modify_record in parse_ldif(
        file_opener=StringIO, path_or_data=SAMPLE_LDIF_DATA
    )
