from io import BytesIO, StringIO
from unittest import mock

import boto3
import pytest
from etl_utils.ldif.ldif import (
    DistinguishedName,
    filter_and_group_ldif_from_s3_by_property,
    filter_ldif_from_s3_by_property,
    ldif_dump,
    parse_ldif,
)
from moto import mock_aws

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

# Same as the above with comments but all keys lower cased
DUMPED_SAMPLE_LDIF = """dn: dc=com,dc=example,ou=test
changetype: add
objectclass: organizationalUnit
objectclass: top
ou: test

dn: dc=com,dc=example,ou=test
changetype: modify
add: description
description: First description value
description: Second description value
-
replace: postalcode
postalcode: 12345
-
delete: seealso
-

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
            "changetype": {"modify"},
            "modifications": [
                (
                    "add",
                    "description",
                    {"First description value", "Second description value"},
                ),
                (
                    "replace",
                    "postalcode",
                    {"12345"},
                ),
                (
                    "delete",
                    "seealso",
                    set(),
                ),
            ],
        },
    ),
    (
        DistinguishedName(parts=(("dc", "com"), ("dc", "example"), ("ou", "test"))),
        {
            "changetype": {"delete"},
        },
    ),
]

SAMPLE_LDIF_DATA_ADD = """
# Modify an entry
dn: ou=test,dc=example,dc=com
changetype: add
description: First description value
description: Second description value
"""

PARSED_LDIF_DATA_ADD = (
    DistinguishedName(parts=(("dc", "com"), ("dc", "example"), ("ou", "test"))),
    {
        "changetype": {"add"},
        "description": {"First description value", "Second description value"},
    },
)


SAMPLE_LDIF_DATA_DELETE = """
# Modify an entry
dn: ou=test,dc=example,dc=com
changetype: delete
description: First description value
"""

PARSED_LDIF_DATA_DELETE = (
    DistinguishedName(parts=(("dc", "com"), ("dc", "example"), ("ou", "test"))),
    {
        "changetype": {"delete"},
        "description": {"First description value"},
    },
)


SAMPLE_LDIF_DATA_COMPLEX_MODIFY = """
# Modify an entry
dn: ou=test,dc=example,dc=com
changetype: modify
add: description
description: First description value
description: Second description value
-
add: shoeSize
shoeSize: 123
-
add: description
description: Third description value
description: Fourth description value
-
replace: postalCode
postalCode: 12345
-
delete: seeAlso
-
replace: postalCode
postalCode: 45678
postalCode: 54321
-
"""


PARSED_LDIF_DATA_COMPLEX_MODIFY = (
    DistinguishedName(parts=(("dc", "com"), ("dc", "example"), ("ou", "test"))),
    {
        "changetype": {"modify"},
        "modifications": [
            (
                "add",
                "description",
                {"First description value", "Second description value"},
            ),
            (
                "add",
                "shoesize",
                {"123"},
            ),
            (
                "add",
                "description",
                {"Third description value", "Fourth description value"},
            ),
            (
                "replace",
                "postalcode",
                {"12345"},
            ),
            (
                "delete",
                "seealso",
                set(),
            ),
            (
                "replace",
                "postalcode",
                {"45678", "54321"},
            ),
        ],
    },
)


UPDATE_TRIGGER_LDIF_MODIFY_EXAMPLE = """
dn: uniqueIdentifier=000173655515,ou=Services,o=nhs
changeType: modify
add: nhsAsClient
nhsAsClient: AAA
-
objectClass: modify
objectClass: top
uniqueIdentifier: 000173655515
"""

PARSED_UPDATE_TRIGGER_LDIF_MODIFY = (
    DistinguishedName(
        parts=(("o", "nhs"), ("ou", "services"), ("uniqueidentifier", "000173655515"))
    ),
    {
        "changetype": {"modify"},
        "modifications": [
            (
                "add",
                "nhsasclient",
                {"AAA"},
            )
        ],
        "objectclass": {"modify", "top"},
        "uniqueidentifier": {"000173655515"},
    },
)

LDIF_TO_FILTER_AND_GROUP_EXAMPLE = """
dn: uniqueIdentifier=AAA1
myField: AAA
myOtherField: 123

dn: uniqueIdentifier=BBB1
myfield: BBB
myOtherField: 123

dn: uniqueIdentifier=BBB2
myfield: BBB
myOtherField: 123

dn: uniqueIdentifier=AAA2
myfield: AAA
myOtherField: 123

dn: uniqueIdentifier=AAA3
myField: AAA
myOtherField: 234

dn: uniqueIdentifier=BBB3
myfield: BBB
myOtherField: 123
"""

FILTERED_AND_GROUPED_LDIF_TO_FILTER_AND_GROUP_EXAMPLE = """
dn: uniqueIdentifier=AAA1
myField: AAA
myOtherField: 123

dn: uniqueIdentifier=AAA2
myfield: AAA
myOtherField: 123

dn: uniqueIdentifier=BBB1
myfield: BBB
myOtherField: 123

dn: uniqueIdentifier=BBB2
myfield: BBB
myOtherField: 123

dn: uniqueIdentifier=BBB3
myfield: BBB
myOtherField: 123
"""

LDIF_TO_FILTER_AND_GROUP_EXAMPLE_BASE_64 = """
dn: uniqueIdentifier=AAA1
myField:: QUFB
myOtherField: 123

dn: uniqueIdentifier=BBB1
myfield: BBB
myOtherField: 123

dn: uniqueIdentifier=BBB2
myfield: BBB
myOtherField: 123

dn: uniqueIdentifier=AAA2
myfield: AAA
myOtherField: 123

dn: uniqueIdentifier=AAA3
myField: AAA
myOtherField: 234

dn: uniqueIdentifier=BBB3
myfield:: QkJC
myOtherField: 123
"""

FILTERED_AND_GROUPED_LDIF_TO_FILTER_AND_GROUP_EXAMPLE = """
dn: uniqueIdentifier=AAA1
myField:: QUFB
myOtherField: 123

dn: uniqueIdentifier=AAA2
myfield: AAA
myOtherField: 123

dn: uniqueIdentifier=BBB1
myfield: BBB
myOtherField: 123

dn: uniqueIdentifier=BBB2
myfield: BBB
myOtherField: 123

dn: uniqueIdentifier=BBB3
myfield:: QkJC
myOtherField: 123
"""


@pytest.mark.parametrize(
    ("raw_distinguished_name", "parsed_distinguished_name"),
    (
        [
            "foo=FOO",
            DistinguishedName(
                parts=(("foo", "foo"),),
            ),
        ],
        [
            "foo=FOO,bar.baz=BAR.BAZ",
            DistinguishedName(
                parts=(
                    ("bar.baz", "bar.baz"),
                    ("foo", "foo"),
                ),
            ),
        ],
    ),
)
def test_distinguished_name(raw_distinguished_name: str, parsed_distinguished_name):
    distinguished_name = DistinguishedName.parse(raw_distinguished_name)
    assert distinguished_name == parsed_distinguished_name
    assert sorted(distinguished_name.raw.split(",")) == sorted(
        raw_distinguished_name.lower().split(",")
    )


@pytest.mark.parametrize(
    ("file_opener", "path_or_data"),
    ([StringIO, SAMPLE_LDIF_DATA], [BytesIO, SAMPLE_LDIF_DATA.encode()]),
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
    data = io.getvalue().decode()
    assert data == DUMPED_SAMPLE_LDIF


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


@mock.patch(
    "etl_utils.ldif.ldif._smart_open",
    return_value=BytesIO(LDIF_TO_FILTER_AND_GROUP_EXAMPLE.encode()),
)
def test_filter_and_group_ldif_from_s3_by_property(mocked_open):
    with mock_aws():
        s3_client = boto3.client("s3")
        filtered_ldif = filter_and_group_ldif_from_s3_by_property(
            s3_client=s3_client,
            s3_path="s3://dummy_bucket/dummy_key",
            group_field="myField",
            filter_terms=[("myOtherField", "123")],
        )
    assert (
        "".join(data.tobytes().decode() for data in filtered_ldif)
        == FILTERED_AND_GROUPED_LDIF_TO_FILTER_AND_GROUP_EXAMPLE
    )


@mock.patch(
    "etl_utils.ldif.ldif._smart_open",
    return_value=BytesIO(LDIF_TO_FILTER_AND_GROUP_EXAMPLE_BASE_64.encode()),
)
def test_filter_and_group_ldif_from_s3_by_property_with_b64encoded_group(mocked_open):
    with mock_aws():
        s3_client = boto3.client("s3")
        filtered_ldif = filter_and_group_ldif_from_s3_by_property(
            s3_client=s3_client,
            s3_path="s3://dummy_bucket/dummy_key",
            group_field="myField",
            filter_terms=[("myOtherField", "123")],
        )
    assert (
        "".join(data.tobytes().decode() for data in filtered_ldif)
        == FILTERED_AND_GROUPED_LDIF_TO_FILTER_AND_GROUP_EXAMPLE
    )


@pytest.mark.parametrize(
    ["raw_ldif", "parsed_ldif"],
    [
        (SAMPLE_LDIF_DATA_COMPLEX_MODIFY, PARSED_LDIF_DATA_COMPLEX_MODIFY),
        (SAMPLE_LDIF_DATA_DELETE, PARSED_LDIF_DATA_DELETE),
        (SAMPLE_LDIF_DATA_ADD, PARSED_LDIF_DATA_ADD),
        (UPDATE_TRIGGER_LDIF_MODIFY_EXAMPLE, PARSED_UPDATE_TRIGGER_LDIF_MODIFY),
    ],
)
def test_parse_ldif_changes(raw_ldif, parsed_ldif):
    ((dn, record),) = parse_ldif(file_opener=StringIO, path_or_data=raw_ldif)
    _dn, _record = parsed_ldif
    assert dn == _dn
    assert record == _record


def test_parse_ldif_multiple_changes():
    raw_ldif = "\n\n".join(
        (
            SAMPLE_LDIF_DATA_COMPLEX_MODIFY,
            SAMPLE_LDIF_DATA_DELETE,
            SAMPLE_LDIF_DATA_ADD,
            SAMPLE_LDIF_DATA_ADD,
            SAMPLE_LDIF_DATA_DELETE,
            SAMPLE_LDIF_DATA_COMPLEX_MODIFY,
        )
    )
    expected_parsed_ldif = [
        PARSED_LDIF_DATA_COMPLEX_MODIFY,
        PARSED_LDIF_DATA_DELETE,
        PARSED_LDIF_DATA_ADD,
        PARSED_LDIF_DATA_ADD,
        PARSED_LDIF_DATA_DELETE,
        PARSED_LDIF_DATA_COMPLEX_MODIFY,
    ]

    records = [
        record for _, record in parse_ldif(file_opener=StringIO, path_or_data=raw_ldif)
    ]
    expected_records = [record for _, record in expected_parsed_ldif]
    assert records == expected_records
