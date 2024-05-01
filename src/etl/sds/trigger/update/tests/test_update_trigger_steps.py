from etl.sds.trigger.update.steps import (
    _get_changelog_entries_from_ldap,
    _parse_and_join_changelog_changes,
)

DISTINGUISHED_NAME = "changenumber=537507,cn=changelog,o=nhs"
RECORD = {
    "objectClass": [b"top", b"changeLogEntry", b"nhsExternalChangelogEntry"],
    "changeNumber": [b"537507"],
    "changeTime": [b"20240417072834Z"],
    "changeType": [b"add"],
}


def test__parse_and_join_changelog_changes_filters_out_people():
    organisational_units = ["foo", "people", "People", "foo", "foo"]

    changelog_entries = [
        (
            DISTINGUISHED_NAME,
            dict(
                **RECORD,
                targetDN=[
                    f"uniqueIdentifier=f1c55263f1ee924f460f,ou={ou},o=nhs".encode()
                ],
                changes=[f"\\nobjectClass: {ou}\\n".encode()],
            ),
        )
        for ou in organisational_units
    ]
    assert _parse_and_join_changelog_changes(
        data={_get_changelog_entries_from_ldap: changelog_entries}, cache=None
    ) == (
        "dn: o=nhs,ou=foo,uniqueIdentifier=f1c55263f1ee924f460f\nobjectclass: add\nchangetype: add\nobjectClass: foo\n\n"
        "dn: o=nhs,ou=foo,uniqueIdentifier=f1c55263f1ee924f460f\nobjectclass: add\nchangetype: add\nobjectClass: foo\n\n"
        "dn: o=nhs,ou=foo,uniqueIdentifier=f1c55263f1ee924f460f\nobjectclass: add\nchangetype: add\nobjectClass: foo"
    )
