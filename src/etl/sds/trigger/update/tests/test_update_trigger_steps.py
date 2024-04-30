from etl.sds.trigger.update.steps import (
    _get_changelog_entries_from_ldap,
    _parse_and_join_changelog_changes,
)

DISTINGUISHED_NAME = "changenumber=537507,cn=changelog,o=nhs"
RECORD_WITHOUT_CHANGES = {
    "objectClass": [b"top", b"changeLogEntry", b"nhsExternalChangelogEntry"],
    "changeNumber": [b"537507"],
    "changeTime": [b"20240417072834Z"],
    "changeType": [b"add"],
    "targetDN": [b"uniqueIdentifier=f1c55263f1ee924f460f,ou=Services,o=nhs"],
}

RAW_NHS_MHS = b"\\nobjectClass: nhsMhs\\nobjectClass: top\\nnhsApproverURP: uniqueidentifier=555050304105,uniqueidentifier=555008548101,uid=555008545108,ou=people, o=nhs\\nnhsContractPropertyTemplateKey: 14\\nnhsDateApproved: 20240417082830\\nnhsDateDNSApproved: 20240417082830\\nnhsDateRequested: 20240417082818\\nnhsDNSApprover: uniqueidentifier=555050304105,uniqueidentifier=555008548101,uid=555008545108,ou=people, o=nhs\\nnhsEPInteractionType: ebXML\\nnhsIDCode: X26\\nnhsMHSAckRequested: never\\nnhsMhsCPAId: f1c55263f1ee924f460f\\nnhsMHSDuplicateElimination: never\\nnhsMHSEndPoint: https://simple-sync.intspineservices.nhs.uk/\\nnhsMhsFQDN: simple-sync.intspineservices.nhs.uk\\nnhsMHsIN: QUPA_IN050000UK32\\nnhsMhsIPAddress: 0.0.0.0\\nnhsMHSIsAuthenticated: none\\nnhsMHSPartyKey: X26-823848\\nnhsMHsSN: urn:nhs:names:services:pdsquery\\nnhsMhsSvcIA: urn:nhs:names:services:pdsquery:QUPA_IN050000UK32\\nnhsMHSSyncReplyMode: None\\nnhsProductKey: 10894\\nnhsProductName: Compliance\\nnhsProductVersion: Initial\\nnhsRequestorURP: uniqueidentifier=555050304105,uniqueidentifier=555008548101,uid=555008545108,ou=people, o=nhs\\nuniqueIdentifier: f1c55263f1ee924f460f"
RAW_NHS_ORG_PERSON_ROLE = b'\\nobjectClass: nhsOrgPersonRole\\nobjectClass: top\\nnhsIDCode: A9A5A\\nnhsJobRole: "Clinical":"Clinical Support":"Medical Secretary Access Role"\\nnhsJobRoleCode: S8000:G8001:R8006\\nnhsOrgOpenDate: 20240419\\nuniqueIdentifier: 555306132104'
NHS_MHS_AS_CHANGE = """dn: o=nhs,ou=Services,uniqueIdentifier=f1c55263f1ee924f460f
changetype: add
objectClass: nhsMhs
objectClass: top
nhsApproverURP: uniqueidentifier=555050304105,uniqueidentifier=555008548101,uid=555008545108,ou=people, o=nhs
nhsContractPropertyTemplateKey: 14
nhsDateApproved: 20240417082830
nhsDateDNSApproved: 20240417082830
nhsDateRequested: 20240417082818
nhsDNSApprover: uniqueidentifier=555050304105,uniqueidentifier=555008548101,uid=555008545108,ou=people, o=nhs
nhsEPInteractionType: ebXML
nhsIDCode: X26
nhsMHSAckRequested: never
nhsMhsCPAId: f1c55263f1ee924f460f
nhsMHSDuplicateElimination: never
nhsMHSEndPoint: https://simple-sync.intspineservices.nhs.uk/
nhsMhsFQDN: simple-sync.intspineservices.nhs.uk
nhsMHsIN: QUPA_IN050000UK32
nhsMhsIPAddress: 0.0.0.0
nhsMHSIsAuthenticated: none
nhsMHSPartyKey: X26-823848
nhsMHsSN: urn:nhs:names:services:pdsquery
nhsMhsSvcIA: urn:nhs:names:services:pdsquery:QUPA_IN050000UK32
nhsMHSSyncReplyMode: None
nhsProductKey: 10894
nhsProductName: Compliance
nhsProductVersion: Initial
nhsRequestorURP: uniqueidentifier=555050304105,uniqueidentifier=555008548101,uid=555008545108,ou=people, o=nhs
uniqueIdentifier: f1c55263f1ee924f460f"""


def test__parse_and_join_changelog_changes_filters_out_people():
    changes = [
        RAW_NHS_MHS,
        RAW_NHS_MHS,
        RAW_NHS_ORG_PERSON_ROLE,
        RAW_NHS_MHS,
        RAW_NHS_ORG_PERSON_ROLE,
    ]

    changelog_entries = [
        (DISTINGUISHED_NAME, dict(**RECORD_WITHOUT_CHANGES, changes=[changes]))
        for changes in changes
    ]
    assert _parse_and_join_changelog_changes(
        data={_get_changelog_entries_from_ldap: changelog_entries}, cache=None
    ) == "\n\n".join([NHS_MHS_AS_CHANGE, NHS_MHS_AS_CHANGE, NHS_MHS_AS_CHANGE])
