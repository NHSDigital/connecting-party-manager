from io import BytesIO, StringIO
from tempfile import NamedTemporaryFile
from unittest import mock

import boto3
import pytest
from etl_utils.ldif.ldif import (
    DistinguishedName,
    filter_ldif_from_s3_by_property,
    ldif_dump,
    parse_ldif,
)
from moto import mock_aws
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

# Same as the above with comments and hyphens removed, and all keys lower cased
DUMPED_SAMPLE_LDIF = """dn: dc=com,dc=example,ou=test
changetype: add
objectclass: organizationalUnit
objectclass: top
ou: test

dn: dc=com,dc=example,ou=test
add: description
changetype: modify
delete: seeAlso
description: First description value
description: Second description value
postalcode: 12345
replace: postalCode

dn: dc=com,dc=example,ou=test
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
    assert sorted(distinguished_name.raw.split(",")) == sorted(
        raw_distinguished_name.split(",")
    )


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


def test_dumped_ldif_same_as_initial():
    parsed_initial_ldif = list(
        parse_ldif(file_opener=StringIO, path_or_data=SAMPLE_LDIF_DATA)
    )
    parsed_dumped_ldif = list(
        parse_ldif(file_opener=StringIO, path_or_data=DUMPED_SAMPLE_LDIF)
    )
    assert parsed_initial_ldif == parsed_dumped_ldif


def test_ldif_dump():
    io = BytesIO()
    ldif_dump(fp=io, obj=PARSED_SAMPLE_LDIF)
    assert io.getvalue().decode() == DUMPED_SAMPLE_LDIF


@mock.patch(
    "etl_utils.ldif.ldif._smart_open", return_value=BytesIO(SAMPLE_LDIF_DATA.encode())
)
def test_filter_ldif_from_s3_by_property(mocked_open):
    with mock_aws():
        s3_client = boto3.client("s3")
        filtered_ldif = filter_ldif_from_s3_by_property(
            s3_client=s3_client,
            s3_path="s3://dummy_bucket/dummy_key",
            filter_terms=[("changeType", "Modify")],
        )
    assert filtered_ldif.tobytes().decode() == SAMPLE_LDIF_DATA_MODIFY

    ((modify_record),) = parse_ldif(file_opener=BytesIO, path_or_data=filtered_ldif)

    assert modify_record in parse_ldif(
        file_opener=StringIO, path_or_data=SAMPLE_LDIF_DATA
    )
