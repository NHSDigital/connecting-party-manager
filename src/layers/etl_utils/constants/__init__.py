from collections import deque
from enum import StrEnum

CHANGELOG_NUMBER = "changelog-number"
CHANGELOG_BASE = "cn=Changelog,o=nhs"
LDAP_FILTER_ALL = "(objectClass=*)"
FILTERED_OUT = "FILTERED-OUT"
EMPTY_LDIF = ""
EMPTY_ARRAY = deque()
LDIF_RECORD_DELIMITER = "\n\n"

UNSUPPORTED_ORGANISATIONAL_UNITS = {
    b"ou=people",
    b"ou=organisations",
    b"ou=workgroups",
    b"ou=referencedata",
}


class ChangelogAttributes(StrEnum):
    FIRST_CHANGELOG_NUMBER = "firstchangenumber"
    LAST_CHANGELOG_NUMBER = "lastchangenumber"


class WorkerKey(StrEnum):
    EXTRACT = "input--extract/unprocessed"
    TRANSFORM = "input--transform/unprocessed"
    LOAD = "input--load/unprocessed"
