devices = {
    "resourceType": "Bundle",
    "id": "11C55B9F-0D7A-41DB-8BE6-306DABA69698",
    "type": "searchset",
    "total": 1,
    "link": [{"relation": "self", "url": "https://cpm.co.uk/Device"}],
    "entry": [
        {
            "resourceType": "Bundle",
            "id": "11C55B9F-0D7A-41DB-8BE6-306DABA69698",
            "type": "collection",
            "total": 1,
            "link": [
                {
                    "relation": "self",
                    "url": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cae",
                }
            ],
            "entry": [
                {
                    "fullUrl": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cae",
                    "resource": {
                        "resourceType": "Device",
                        "deviceName": [
                            {"name": "CPM-Test-Device", "type": "user-friendly-name"}
                        ],
                        "definition": {
                            "identifier": {
                                "system": "connecting-party-manager/device-type",
                                "value": "instance",
                            }
                        },
                        "identifier": [
                            {
                                "system": "https://fhir.nhs.uk/Id/nhsSpineASID",
                                "value": "010057927542",
                            }
                        ],
                        "owner": {
                            "identifier": {
                                "system": "connecting-party-manager/product-team-id",
                                "value": "ae2ab026-0b53-7e7c-7a65-f0407a6e75f5",
                            }
                        },
                    },
                    "search": {"mode": "match"},
                },
                {
                    "resourceType": "QuestionnaireResponse",
                    "identifier": "010057927542",
                    "questionnaire": "https://cpm.co.uk/Questionnaire/spine_device|v1",
                    "status": "completed",
                    "subject": {
                        "reference": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cae"
                    },
                    "authored": "<dateTime>",
                    "author": {
                        "reference": "https://cpm.co.uk/Organization/ae2ab026-0b53-7e7c-7a65-f0407a6e75f5"
                    },
                    "item": [
                        {
                            "link_id": "object_class",
                            "text": "object_class",
                            "answer": [
                                {"valueString": "nhsAS"},
                                {"valueString": "top"},
                            ],
                        },
                        {
                            "link_id": "nhs_approver_urp",
                            "text": "nhs_approver_urp",
                            "answer": [
                                {
                                    "valueString": "uniqueIdentifier=562983788547,uniqueIdentifier=883298590547,uid=503560389549,ou=People,o=nhs"
                                }
                            ],
                        },
                        {
                            "link_id": "nhs_as_client",
                            "text": "nhs_as_client",
                            "answer": [{"valueString": "5NR"}],
                        },
                        {
                            "link_id": "nhs_as_svc_ia",
                            "text": "nhs_as_svc_ia",
                            "answer": [
                                {
                                    "valueString": "urn:oasis:names:tc:ebxml-msg:service:Acknowledgment"
                                },
                                {
                                    "valueString": "urn:oasis:names:tc:ebxml-msg:service:MessageError"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:REPC_IN020000UK01"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:REPC_IN050000UK01"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:REPC_IN040000UK01"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:REPC_IN030000UK01"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:QUPC_IN010000UK01"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:REPC_IN050000UK13"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:REPC_IN060000UK01"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:REPC_IN080000UK01"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:QUQI_IN010000UK14"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:QUPC_IN030000UK14"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:QUPC_IN010000UK15"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:QUPC_IN040000UK14"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:REPC_IN070000UK01"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:REPC_IN010000UK01"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:REPC_IN110000UK01"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:REPC_IN020000UK13"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:REPC_IN010000UK15"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:MCCI_IN010000UK13"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:REPC_IN040000UK15"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrsquery:QUPC_IN040000UK14"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrsquery:QUPC_IN030000UK14"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrsquery:QUQI_IN010000UK14"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrsquery:MCCI_IN010000UK13"
                                },
                            ],
                        },
                        {
                            "link_id": "nhs_date_approved",
                            "text": "nhs_date_approved",
                            "answer": [{"valueDateTime": "2008-04-01T13:18:34"}],
                        },
                        {
                            "link_id": "nhs_date_requested",
                            "text": "nhs_date_requested",
                            "answer": [{"valueDateTime": "2008-04-01T12:54:47"}],
                        },
                        {
                            "link_id": "nhs_id_code",
                            "text": "nhs_id_code",
                            "answer": [{"valueString": "5NR"}],
                        },
                        {
                            "link_id": "nhs_mhs_manufacturer_org",
                            "text": "nhs_mhs_manufacturer_org",
                            "answer": [{"valueString": "LSP02"}],
                        },
                        {
                            "link_id": "nhs_mhs_party_key",
                            "text": "nhs_mhs_party_key",
                            "answer": [{"valueString": "5NR-801831"}],
                        },
                        {
                            "link_id": "nhs_product_key",
                            "text": "nhs_product_key",
                            "answer": [{"valueInteger": 1113}],
                        },
                        {
                            "link_id": "nhs_requestor_urp",
                            "text": "nhs_requestor_urp",
                            "answer": [
                                {
                                    "valueString": "uniqueIdentifier=977624345541,uniqueIdentifier=883298590547,uid=503560389549,ou=People,o=nhs"
                                }
                            ],
                        },
                        {
                            "link_id": "nhs_temp_uid",
                            "text": "nhs_temp_uid",
                            "answer": [{"valueInteger": 1663}],
                        },
                        {
                            "link_id": "unique_identifier",
                            "text": "unique_identifier",
                            "answer": [{"valueString": "010057927542"}],
                        },
                    ],
                },
            ],
        },
        {
            "resourceType": "Bundle",
            "id": "11C55B9F-0D7A-41DB-8BE6-306DABA69699",
            "type": "collection",
            "total": 1,
            "link": [
                {
                    "relation": "self",
                    "url": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53caf",
                }
            ],
            "entry": [
                {
                    "fullUrl": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53caf",
                    "resource": {
                        "resourceType": "Device",
                        "deviceName": [
                            {"name": "CPM-Test-Device-2", "type": "user-friendly-name"}
                        ],
                        "definition": {
                            "identifier": {
                                "system": "connecting-party-manager/device-type",
                                "value": "instance",
                            }
                        },
                        "identifier": [
                            {
                                "system": "https://fhir.nhs.uk/Id/nhsSpineASID",
                                "value": "798706756516",
                            }
                        ],
                        "owner": {
                            "identifier": {
                                "system": "connecting-party-manager/product-team-id",
                                "value": "ae2ab026-0b53-7e7c-7a65-f0407a6e75f5",
                            }
                        },
                    },
                    "search": {"mode": "match"},
                },
                {
                    "resourceType": "QuestionnaireResponse",
                    "identifier": "798706756516",
                    "questionnaire": "https://cpm.co.uk/Questionnaire/spine_device|v1",
                    "status": "completed",
                    "subject": {
                        "reference": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53caf"
                    },
                    "authored": "<dateTime>",
                    "author": {
                        "reference": "https://cpm.co.uk/Organization/ae2ab026-0b53-7e7c-7a65-f0407a6e75f5"
                    },
                    "item": [
                        {
                            "link_id": "object_class",
                            "text": "object_class",
                            "answer": [
                                {"valueString": "nhsAS"},
                                {"valueString": "top"},
                            ],
                        },
                        {
                            "link_id": "nhs_approver_urp",
                            "text": "nhs_approver_urp",
                            "answer": [
                                {
                                    "valueString": "uniqueIdentifier=342242872543,uniqueIdentifier=883298590547,uid=503560389549,ou=People,o=nhs"
                                }
                            ],
                        },
                        {
                            "link_id": "nhs_as_acf",
                            "text": "nhs_as_acf",
                            "answer": [
                                {"valueString": "RBAC"},
                                {"valueString": "DOLR"},
                                {"valueString": "CNST"},
                            ],
                        },
                        {
                            "link_id": "nhs_as_client",
                            "text": "nhs_as_client",
                            "answer": [{"valueString": "RTX"}],
                        },
                        {
                            "link_id": "nhs_as_svc_ia",
                            "text": "nhs_as_svc_ia",
                            "answer": [
                                {
                                    "valueString": "urn:oasis:names:tc:ebxml-msg:service:Acknowledgment"
                                },
                                {
                                    "valueString": "urn:oasis:names:tc:ebxml-msg:service:MessageError"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:ebs:PRSC_IN040000UK08"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:ebs:PRSC_IN060000UK06"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:ebs:PRSC_IN140000UK06"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:ebs:PRSC_IN150000UK06"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:ebs:PRSC_IN070000UK08"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:ebs:PRSC_IN080000UK07"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:ebs:PRSC_IN050000UK06"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:ebs:PRSC_IN090000UK09"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:ebs:PRSC_IN130000UK07"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:ebs:PRSC_IN110000UK08"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:ebs:PRSC_IN100000UK06"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:ebs:MCCI_IN010000UK13"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:pds:MCCI_IN010000UK13"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:pds:PRPA_IN150000UK30"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:pds:PRPA_IN060000UK30"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:pds:PRPA_IN040000UK30"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:pds:PRPA_IN160000UK30"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:pdsquery:QUPA_IN060000UK30"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:pdsquery:QUPA_IN050000UK32"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:pdsquery:QUPA_IN010000UK32"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:pdsquery:QUPA_IN070000UK30"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:pdsquery:QUQI_IN010000UK14"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:pdsquery:QUPA_IN030000UK32"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:pdsquery:QUPA_IN020000UK31"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:pdsquery:QUPA_IN040000UK32"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:pdsquery:MCCI_IN010000UK13"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:psisquery:QUPC_IN160101UK05"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:psisquery:QUPC_IN160109UK05"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:psisquery:QUPC_IN160102UK05"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:psisquery:QUPC_IN160104UK05"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:psisquery:QUPC_IN160108UK05"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:psisquery:QUPC_IN160110UK05"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:psisquery:MCCI_IN010000UK13"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:psisquery:QUQI_IN010000UK14"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:psisquery:QUPC_IN160107UK05"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:psisquery:QUPC_IN160103UK05"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:REPC_IN040000UK15"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:REPC_IN050000UK13"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:MCCI_IN010000UK13"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:QUQI_IN010000UK14"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:REPC_IN010000UK15"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrs:REPC_IN020000UK13"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrsquery:QUPC_IN010000UK32"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrsquery:QUQI_IN010000UK14"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrsquery:QUPC_IN020000UK17"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrsquery:QUPC_IN250000UK02"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrsquery:QUPC_IN060000UK32"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrsquery:QUPC_IN070000UK32"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrsquery:MCCI_IN010000UK13"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrsquery:QUPC_IN090000UK03"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:lrsquery:QUPC_IN030000UK14"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:sds:REPC_IN130005UK01"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:sds:REPC_IN130003UK01"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:sds:REPC_IN130004UK01"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:sds:REPC_IN130002UK01"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:sds:MCCI_IN010000UK13"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:sdsquery:QUPC_IN041234UK01"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:sdsquery:REPC_IN130007UK01"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:sdsquery:MCCI_IN010000UK13"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:sdsquery:QUPC_IN010102UK01"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:sdsquery:QUPC_IN010103UK01"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:sdsquery:QUQI_IN010000UK14"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:sdsquery:AccreditedSystemSearchRequest_1_0"
                                },
                                {
                                    "valueString": "urn:nhs:names:services:sdsquery:AccreditedSystemSearchResponse_1_0"
                                },
                            ],
                        },
                        {
                            "link_id": "nhs_date_approved",
                            "text": "nhs_date_approved",
                            "answer": [{"valueDateTime": "2009-09-14T12:56:10"}],
                        },
                        {
                            "link_id": "nhs_date_requested",
                            "text": "nhs_date_requested",
                            "answer": [{"valueDateTime": "2009-09-14T12:53:32"}],
                        },
                        {
                            "link_id": "nhs_id_code",
                            "text": "nhs_id_code",
                            "answer": [{"valueString": "RTX"}],
                        },
                        {
                            "link_id": "nhs_mhs_manufacturer_org",
                            "text": "nhs_mhs_manufacturer_org",
                            "answer": [{"valueString": "LSP02"}],
                        },
                        {
                            "link_id": "nhs_mhs_party_key",
                            "text": "nhs_mhs_party_key",
                            "answer": [{"valueString": "RTX-806845"}],
                        },
                        {
                            "link_id": "nhs_product_key",
                            "text": "nhs_product_key",
                            "answer": [{"valueInteger": 4622}],
                        },
                        {
                            "link_id": "nhs_product_name",
                            "text": "nhs_product_name",
                            "answer": [{"valueString": "Lorenzo Regional Care"}],
                        },
                        {
                            "link_id": "nhs_product_version",
                            "text": "nhs_product_version",
                            "answer": [{"valueString": "R2"}],
                        },
                        {
                            "link_id": "nhs_requestor_urp",
                            "text": "nhs_requestor_urp",
                            "answer": [
                                {
                                    "valueString": "uniqueIdentifier=977624345541,uniqueIdentifier=883298590547,uid=503560389549,ou=People,o=nhs"
                                }
                            ],
                        },
                        {
                            "link_id": "nhs_temp_uid",
                            "text": "nhs_temp_uid",
                            "answer": [{"valueInteger": 10195}],
                        },
                        {
                            "link_id": "unique_identifier",
                            "text": "unique_identifier",
                            "answer": [{"valueString": "798706756516"}],
                        },
                    ],
                },
            ],
        },
    ],
}

endpoints = {
    "resourceType": "Bundle",
    "id": "11C55B9F-0D7A-41DB-8BE6-306DABA69698",
    "type": "searchset",
    "total": 1,
    "link": [{"relation": "self", "url": "https://cpm.co.uk/Device"}],
    "entry": [
        {
            "resourceType": "Bundle",
            "id": "11C55B9F-0D7A-41DB-8BE6-306DABA69700",
            "type": "collection",
            "total": 1,
            "link": [
                {
                    "relation": "self",
                    "url": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cag",
                }
            ],
            "entry": [
                {
                    "fullUrl": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cag",
                    "resource": {
                        "resourceType": "Device",
                        "deviceName": [
                            {
                                "name": "CPM-Test-Device-Endpoint",
                                "type": "user-friendly-name",
                            }
                        ],
                        "definition": {
                            "identifier": {
                                "system": "connecting-party-manager/device-type",
                                "value": "endpoint",
                            }
                        },
                        "identifier": [
                            {
                                "system": "https://fhir.nhs.uk/Id/nhsMhsPartyKey|Extension-SDS-NhsServiceInteractionId",
                                "value": "RTX-821088|urn:nhs:names:services:ebs:PRSC_IN070000UK08",
                            },
                            {
                                "system": "https://fhir.nhs.uk/Id/nhsMHSId",
                                "value": "69720694737ed98c0242",  # pragma: allowlist secret
                            },
                        ],
                        "owner": {
                            "identifier": {
                                "system": "connecting-party-manager/product-team-id",
                                "value": "ae2ab026-0b53-7e7c-7a65-f0407a6e75f5",
                            }
                        },
                    },
                    "search": {"mode": "match"},
                },
                {
                    "resourceType": "QuestionnaireResponse",
                    "identifier": "RTX-821088|urn:nhs:names:services:ebs:PRSC_IN070000UK08",
                    "questionnaire": "https://cpm.co.uk/Questionnaire/spine_endpoint|v1",
                    "status": "completed",
                    "subject": {
                        "reference": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cag"
                    },
                    "authored": "<dateTime>",
                    "author": {
                        "reference": "https://cpm.co.uk/Organization/ae2ab026-0b53-7e7c-7a65-f0407a6e75f5"
                    },
                    "item": [
                        {
                            "linkId": "object_class",
                            "text": "object_class",
                            "answer": [
                                {"valueString": "nhsMhs"},
                                {"valueString": "top"},
                            ],
                        },
                        {
                            "linkId": "nhs_approver_urp",
                            "text": "nhs_approver_urp",
                            "answer": [
                                {
                                    "valueString": "uniqueidentifier=555050305106,uniqueidentifier=555008548101,uid=555008545108,ou=people,o=nhs"
                                }
                            ],
                        },
                        {
                            "linkId": "nhs_contract_property_template_key",
                            "text": "nhs_contract_property_template_key",
                            "answer": [{"valueInteger": 45}],
                        },
                        {
                            "linkId": "nhs_date_approved",
                            "text": "nhs_date_approved",
                            "answer": [{"valueDateTime": "2016-09-29T11:43:37"}],
                        },
                        {
                            "linkId": "nhs_date_dns_approved",
                            "text": "nhs_date_dns_approved",
                            "answer": [{"valueDateTime": "2016-09-29T11:43:37"}],
                        },
                        {
                            "linkId": "nhs_date_requested",
                            "text": "nhs_date_requested",
                            "answer": [{"valueDateTime": "2016-09-29T10:20:51"}],
                        },
                        {
                            "linkId": "nhs_dns_approver",
                            "text": "nhs_dns_approver",
                            "answer": [
                                {
                                    "valueString": "uniqueidentifier=555050305106,uniqueidentifier=555008548101,uid=555008545108,ou=people,o=nhs"
                                }
                            ],
                        },
                        {
                            "linkId": "nhs_ep_interaction_type",
                            "text": "nhs_ep_interaction_type",
                            "answer": [{"valueString": "HL7"}],
                        },
                        {
                            "linkId": "nhs_id_code",
                            "text": "nhs_id_code",
                            "answer": [{"valueString": "RTX"}],
                        },
                        {
                            "linkId": "nhs_mhs_ack_requested",
                            "text": "nhs_mhs_ack_requested",
                            "answer": [{"valueString": "always"}],
                        },
                        {
                            "linkId": "nhs_mhs_actor",
                            "text": "nhs_mhs_actor",
                            "answer": [
                                {
                                    "valueString": "urn:oasis:names:tc:ebxml-msg:actor:nextMSH"
                                }
                            ],
                        },
                        {
                            "linkId": "nhs_mhs_cpa_id",
                            "text": "nhs_mhs_cpa_id",
                            "answer": [
                                {"valueString": "69720694737ed98c0242"}
                            ],  # pragma: allowlist secret
                        },
                        {
                            "linkId": "nhs_mhs_duplicate_elimination",
                            "text": "nhs_mhs_duplicate_elimination",
                            "answer": [{"valueString": "always"}],
                        },
                        {
                            "linkId": "nhs_mhs_end_point",
                            "text": "nhs_mhs_end_point",
                            "answer": [
                                {
                                    "valueString": "https://msg65-spine.msg.mpe.ncrs.nhs.uk/MHS/RTX/EBS3-5/messagehandler"
                                }
                            ],
                        },
                        {
                            "linkId": "nhs_mhs_fqdn",
                            "text": "nhs_mhs_fqdn",
                            "answer": [
                                {"valueString": "msg65-spine.msg.mpe.ncrs.nhs.uk"}
                            ],
                        },
                        {
                            "linkId": "nhs_mhs_in",
                            "text": "nhs_mhs_in",
                            "answer": [{"valueString": "PRSC_IN070000UK08"}],
                        },
                        {
                            "linkId": "nhs_mhs_ip_address",
                            "text": "nhs_mhs_ip_address",
                            "answer": [{"valueString": "20.146.66.17"}],
                        },
                        {
                            "linkId": "nhs_mhs_is_authenticated",
                            "text": "nhs_mhs_is_authenticated",
                            "answer": [{"valueString": "transient"}],
                        },
                        {
                            "linkId": "nhs_mhs_manufacturer_org",
                            "text": "nhs_mhs_manufacturer_org",
                            "answer": [{"valueString": "LSP02"}],
                        },
                        {
                            "linkId": "nhs_mhs_party_key",
                            "text": "nhs_mhs_party_key",
                            "answer": [{"valueString": "RTX-821088"}],
                        },
                        {
                            "linkId": "nhs_mhs_persist_duration",
                            "text": "nhs_mhs_persist_duration",
                            "answer": [{"valueString": "PT4M"}],
                        },
                        {
                            "linkId": "nhs_mhs_retries",
                            "text": "nhs_mhs_retries",
                            "answer": [{"valueInteger": 2}],
                        },
                        {
                            "linkId": "nhs_mhs_retry_interval",
                            "text": "nhs_mhs_retry_interval",
                            "answer": [{"valueString": "PT2S"}],
                        },
                        {
                            "linkId": "nhs_mhs_sn",
                            "text": "nhs_mhs_sn",
                            "answer": [{"valueString": "urn:nhs:names:services:ebs"}],
                        },
                        {
                            "linkId": "nhs_mhs_svc_ia",
                            "text": "nhs_mhs_svc_ia",
                            "answer": [
                                {
                                    "valueString": "urn:nhs:names:services:ebs:PRSC_IN070000UK08"
                                }
                            ],
                        },
                        {
                            "linkId": "nhs_mhs_sync_reply_mode",
                            "text": "nhs_mhs_sync_reply_mode",
                            "answer": [{"valueString": "None"}],
                        },
                        {
                            "linkId": "nhs_product_key",
                            "text": "nhs_product_key",
                            "answer": [{"valueInteger": 10927}],
                        },
                        {
                            "linkId": "nhs_product_name",
                            "text": "nhs_product_name",
                            "answer": [{"valueString": "Lorenzo Regional Care"}],
                        },
                        {
                            "linkId": "nhs_product_version",
                            "text": "nhs_product_version",
                            "answer": [{"valueString": "V3"}],
                        },
                        {
                            "linkId": "nhs_requestor_urp",
                            "text": "nhs_requestor_urp",
                            "answer": [
                                {
                                    "valueString": "uniqueidentifier=099108008519,uniqueidentifier=255496688516,uid=467956997515,ou=people,o=nhs"
                                }
                            ],
                        },
                        {
                            "linkId": "unique_identifier",  # pragma: allowlist secret
                            "text": "unique_identifier",
                            "answer": [{"valueString": "69720694737ed98c0242"}],
                        },
                    ],
                },
            ],
        },
        {
            "resourceType": "Bundle",
            "id": "11C55B9F-0D7A-41DB-8BE6-306DABA69701",
            "type": "collection",
            "total": 1,
            "link": [
                {
                    "relation": "self",
                    "url": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cah",
                }
            ],
            "entry": [
                {
                    "fullUrl": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cah",
                    "resource": {
                        "resourceType": "Device",
                        "deviceName": [
                            {
                                "name": "CPM-Test-Device-Endpoint-2",
                                "type": "user-friendly-name",
                            }
                        ],
                        "definition": {
                            "identifier": {
                                "system": "connecting-party-manager/device-type",
                                "value": "endpoint",
                            }
                        },
                        "identifier": [
                            {
                                "system": "https://fhir.nhs.uk/Id/nhsMhsPartyKey|Extension-SDS-NhsServiceInteractionId",
                                "value": "RTX-821088|urn:nhs:names:services:cpisquery:REPC_IN000007GB01",
                            },
                            {
                                "system": "https://fhir.nhs.uk/Id/nhsMHSId",
                                "value": "798bc45334bbb95b51de",  # pragma: allowlist secret
                            },
                        ],
                        "owner": {
                            "identifier": {
                                "system": "connecting-party-manager/product-team-id",
                                "value": "ae2ab026-0b53-7e7c-7a65-f0407a6e75f5",
                            }
                        },
                    },
                    "search": {"mode": "match"},
                },
                {
                    "resourceType": "QuestionnaireResponse",
                    "identifier": "RTX-821088|urn:nhs:names:services:cpisquery:REPC_IN000007GB01",
                    "questionnaire": "https://cpm.co.uk/Questionnaire/spine_endpoint|v1",
                    "status": "completed",
                    "subject": {
                        "reference": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cah"
                    },
                    "authored": "<dateTime>",
                    "author": {
                        "reference": "https://cpm.co.uk/Organization/ae2ab026-0b53-7e7c-7a65-f0407a6e75f5"
                    },
                    "item": [
                        {
                            "link_id": "object_class",
                            "text": "object_class",
                            "answer": [
                                {"valueString": "nhsMhs"},
                                {"valueString": "top"},
                            ],
                        },
                        {
                            "link_id": "nhs_approver_urp",
                            "text": "nhs_approver_urp",
                            "answer": [
                                {
                                    "valueString": "uniqueidentifier=555050305106,uniqueidentifier=555008548101,uid=555008545108,ou=people,o=nhs"
                                }
                            ],
                        },
                        {
                            "link_id": "nhs_contract_property_template_key",
                            "text": "nhs_contract_property_template_key",
                            "answer": [{"valueInteger": 46}],
                        },
                        {
                            "link_id": "nhs_date_approved",
                            "text": "nhs_date_approved",
                            "answer": [{"valueDateTime": "2016-09-29T11:43:37"}],
                        },
                        {
                            "link_id": "nhs_date_dns_approved",
                            "text": "nhs_date_dns_approved",
                            "answer": [{"valueDateTime": "2016-09-29T11:43:37"}],
                        },
                        {
                            "link_id": "nhs_date_requested",
                            "text": "nhs_date_requested",
                            "answer": [{"valueDateTime": "2016-09-29T10:20:51"}],
                        },
                        {
                            "link_id": "nhs_dns_approver",
                            "text": "nhs_dns_approver",
                            "answer": [
                                {
                                    "valueString": "uniqueidentifier=555050305106,uniqueidentifier=555008548101,uid=555008545108,ou=people,o=nhs"
                                }
                            ],
                        },
                        {
                            "link_id": "nhs_ep_interaction_type",
                            "text": "nhs_ep_interaction_type",
                            "answer": [{"valueString": "HL7"}],
                        },
                        {
                            "link_id": "nhs_id_code",
                            "text": "nhs_id_code",
                            "answer": [{"valueString": "RTX"}],
                        },
                        {
                            "link_id": "nhs_mhs_ack_requested",
                            "text": "nhs_mhs_ack_requested",
                            "answer": [{"valueString": "never"}],
                        },
                        {
                            "link_id": "nhs_mhs_cpa_id",
                            "text": "nhs_mhs_cpa_id",
                            "answer": [
                                {"valueString": "798bc45334bbb95b51de"}
                            ],  # pragma: allowlist secret
                        },
                        {
                            "link_id": "nhs_mhs_duplicate_elimination",
                            "text": "nhs_mhs_duplicate_elimination",
                            "answer": [{"valueString": "never"}],
                        },
                        {
                            "link_id": "nhs_mhs_end_point",
                            "text": "nhs_mhs_end_point",
                            "answer": [
                                {
                                    "valueString": "https://msg65-spine.msg.mpe.ncrs.nhs.uk/Tower6-2/RTX/CPIS-0/responsehandler"
                                }
                            ],
                        },
                        {
                            "link_id": "nhs_mhs_fqdn",
                            "text": "nhs_mhs_fqdn",
                            "answer": [
                                {"valueString": "msg65-spine.msg.mpe.ncrs.nhs.uk"}
                            ],
                        },
                        {
                            "link_id": "nhs_mhs_in",
                            "text": "nhs_mhs_in",
                            "answer": [{"valueString": "REPC_IN000007GB01"}],
                        },
                        {
                            "link_id": "nhs_mhs_ip_address",
                            "text": "nhs_mhs_ip_address",
                            "answer": [{"valueString": "20.146.66.17"}],
                        },
                        {
                            "link_id": "nhs_mhs_is_authenticated",
                            "text": "nhs_mhs_is_authenticated",
                            "answer": [{"valueString": "transient"}],
                        },
                        {
                            "link_id": "nhs_mhs_manufacturer_org",
                            "text": "nhs_mhs_manufacturer_org",
                            "answer": [{"valueString": "LSP02"}],
                        },
                        {
                            "link_id": "nhs_mhs_party_key",
                            "text": "nhs_mhs_party_key",
                            "answer": [{"valueString": "RTX-821088"}],
                        },
                        {
                            "link_id": "nhs_mhs_service_description",
                            "text": "nhs_mhs_service_description",
                            "answer": [
                                {"valueString": "urn:nhs:names:services:cpisquery"}
                            ],
                        },
                        {
                            "link_id": "nhs_mhs_sn",
                            "text": "nhs_mhs_sn",
                            "answer": [
                                {"valueString": "urn:nhs:names:services:cpisquery"}
                            ],
                        },
                        {
                            "link_id": "nhs_mhs_svc_ia",
                            "text": "nhs_mhs_svc_ia",
                            "answer": [
                                {
                                    "valueString": "urn:nhs:names:services:cpisquery:REPC_IN000007GB01"
                                }
                            ],
                        },
                        {
                            "link_id": "nhs_mhs_sync_reply_mode",
                            "text": "nhs_mhs_sync_reply_mode",
                            "answer": [{"valueString": "MSHSignalsOnly"}],
                        },
                        {
                            "link_id": "nhs_product_key",
                            "text": "nhs_product_key",
                            "answer": [{"valueInteger": 10927}],
                        },
                        {
                            "link_id": "nhs_product_name",
                            "text": "nhs_product_name",
                            "answer": [{"valueString": "Lorenzo Regional Care"}],
                        },
                        {
                            "link_id": "nhs_product_version",
                            "text": "nhs_product_version",
                            "answer": [{"valueString": "V3"}],
                        },
                        {
                            "link_id": "nhs_requestor_urp",
                            "text": "nhs_requestor_urp",
                            "answer": [
                                {
                                    "valueString": "uniqueidentifier=099108008519,uniqueidentifier=255496688516,uid=467956997515,ou=people,o=nhs"
                                }
                            ],
                        },
                        {
                            "link_id": "unique_identifier",  # pragma: allowlist secret
                            "text": "unique_identifier",
                            "answer": [
                                {"valueString": "798bc45334bbb95b51de"}
                            ],  # pragma: allowlist secret
                        },
                    ],
                },
            ],
        },
        {
            "resourceType": "Bundle",
            "id": "11C55B9F-0D7A-41DB-8BE6-306DABA69701",
            "type": "collection",
            "total": 1,
            "link": [
                {
                    "relation": "self",
                    "url": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cah",
                }
            ],
            "entry": [
                {
                    "fullUrl": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cah",
                    "resource": {
                        "resourceType": "Device",
                        "deviceName": [
                            {
                                "name": "ReliableIntermediary",
                                "type": "user-friendly-name",
                            }
                        ],
                        "definition": {
                            "identifier": {
                                "system": "connecting-party-manager/device-type",
                                "value": "endpoint",
                            }
                        },
                        "identifier": [
                            {
                                "system": "https://fhir.nhs.uk/Id/nhsMhsPartyKey|Extension-SDS-NhsServiceInteractionId",
                                "value": "YES-0000806|urn:nhs:names:services:tms:ReliableIntermediary",
                            },
                            {
                                "system": "https://fhir.nhs.uk/Id/nhsMHSId",
                                "value": "S20001A000192",  # pragma: allowlist secret
                            },
                        ],
                        "owner": {
                            "identifier": {
                                "system": "connecting-party-manager/product-team-id",
                                "value": "ae2ab026-0b53-7e7c-7a65-f0407a6e75f5",
                            }
                        },
                    },
                    "search": {"mode": "match"},
                },
                {
                    "resourceType": "QuestionnaireResponse",
                    "identifier": "YES-0000806|urn:nhs:names:services:tms:ReliableIntermediary",
                    "questionnaire": "https://cpm.co.uk/Questionnaire/spine_endpoint|v1",
                    "status": "completed",
                    "subject": {
                        "reference": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cah"
                    },
                    "authored": "<dateTime>",
                    "author": {
                        "reference": "https://cpm.co.uk/Organization/ae2ab026-0b53-7e7c-7a65-f0407a6e75f5"
                    },
                    "item": [
                        {
                            "link_id": "object_class",
                            "text": "object_class",
                            "answer": [
                                {"valueString": "nhsMhs"},
                                {"valueString": "top"},
                            ],
                        },
                        {
                            "linkId": "nhs_mhs_actor",
                            "text": "nhs_mhs_actor",
                            "answer": [],
                        },
                        {
                            "link_id": "nhs_id_code",
                            "text": "nhs_id_code",
                            "answer": [{"valueString": "YES"}],
                        },
                        {
                            "link_id": "nhs_mhs_ack_requested",
                            "text": "nhs_mhs_ack_requested",
                            "answer": [{"valueString": "never"}],
                        },
                        {
                            "link_id": "nhs_mhs_cpa_id",
                            "text": "nhs_mhs_cpa_id",
                            "answer": [
                                {"valueString": "S20001A000192"}
                            ],  # pragma: allowlist secret
                        },
                        {
                            "link_id": "nhs_mhs_duplicate_elimination",
                            "text": "nhs_mhs_duplicate_elimination",
                            "answer": [{"valueString": "never"}],
                        },
                        {
                            "link_id": "nhs_mhs_end_point",
                            "text": "nhs_mhs_end_point",
                            "answer": [
                                {
                                    "valueString": "https://msg.int.spine2.ncrs.nhs.uk/reliablemessaging/intermediary"
                                }
                            ],
                        },
                        {
                            "link_id": "nhs_mhs_fqdn",
                            "text": "nhs_mhs_fqdn",
                            "answer": [{"valueString": "msg.int.spine2.ncrs.nhs.uk"}],
                        },
                        {
                            "link_id": "nhs_mhs_in",
                            "text": "nhs_mhs_in",
                            "answer": [{"valueString": "ReliableIntermediary"}],
                        },
                        {
                            "link_id": "nhs_mhs_party_key",
                            "text": "nhs_mhs_party_key",
                            "answer": [{"valueString": "YES-0000806"}],
                        },
                        {
                            "link_id": "nhs_mhs_sn",
                            "text": "nhs_mhs_sn",
                            "answer": [{"valueString": "urn:nhs:names:services:tms"}],
                        },
                        {
                            "link_id": "nhs_mhs_svc_ia",
                            "text": "nhs_mhs_svc_ia",
                            "answer": [
                                {
                                    "valueString": "urn:nhs:names:services:tms:ReliableIntermediary"
                                }
                            ],
                        },
                        {
                            "link_id": "nhs_mhs_sync_reply_mode",
                            "text": "nhs_mhs_sync_reply_mode",
                            "answer": [{"valueString": "None"}],
                        },
                        {
                            "linkId": "nhs_mhs_persist_duration",
                            "text": "nhs_mhs_persist_duration",
                            "answer": [],
                        },
                        {
                            "linkId": "nhs_mhs_retries",
                            "text": "nhs_mhs_retries",
                            "answer": [],
                        },
                        {
                            "linkId": "nhs_mhs_retry_interval",
                            "text": "nhs_mhs_retry_interval",
                            "answer": [],
                        },
                        {
                            "link_id": "unique_identifier",  # pragma: allowlist secret
                            "text": "unique_identifier",
                            "answer": [
                                {"valueString": "S20001A000192"}
                            ],  # pragma: allowlist secret
                        },
                    ],
                },
            ],
        },
        {
            "resourceType": "Bundle",
            "id": "11C55B9F-0D7A-41DB-8BE6-306DABA69701",
            "type": "collection",
            "total": 1,
            "link": [
                {
                    "relation": "self",
                    "url": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cah",
                }
            ],
            "entry": [
                {
                    "fullUrl": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cah",
                    "resource": {
                        "resourceType": "Device",
                        "deviceName": [
                            {
                                "name": "ReliableIntermediary",
                                "type": "user-friendly-name",
                            }
                        ],
                        "definition": {
                            "identifier": {
                                "system": "connecting-party-manager/device-type",
                                "value": "endpoint",
                            }
                        },
                        "identifier": [
                            {
                                "system": "https://fhir.nhs.uk/Id/nhsMhsPartyKey|Extension-SDS-NhsServiceInteractionId",
                                "value": "YEA-801248|urn:nhs:names:services:tms:ReliableIntermediary",
                            },
                            {
                                "system": "https://fhir.nhs.uk/Id/nhsMHSId",
                                "value": "S2001930A2012103",  # pragma: allowlist secret
                            },
                        ],
                        "owner": {
                            "identifier": {
                                "system": "connecting-party-manager/product-team-id",
                                "value": "ae2ab026-0b53-7e7c-7a65-f0407a6e75f5",
                            }
                        },
                    },
                    "search": {"mode": "match"},
                },
                {
                    "resourceType": "QuestionnaireResponse",
                    "identifier": "YEA-801248|urn:nhs:names:services:tms:ReliableIntermediary",
                    "questionnaire": "https://cpm.co.uk/Questionnaire/spine_endpoint|v1",
                    "status": "completed",
                    "subject": {
                        "reference": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cah"
                    },
                    "authored": "<dateTime>",
                    "author": {
                        "reference": "https://cpm.co.uk/Organization/ae2ab026-0b53-7e7c-7a65-f0407a6e75f5"
                    },
                    "item": [
                        {
                            "link_id": "object_class",
                            "text": "object_class",
                            "answer": [
                                {"valueString": "nhsMhs"},
                                {"valueString": "top"},
                            ],
                        },
                        {
                            "linkId": "nhs_mhs_actor",
                            "text": "nhs_mhs_actor",
                            "answer": [],
                        },
                        {
                            "link_id": "nhs_id_code",
                            "text": "nhs_id_code",
                            "answer": [{"valueString": "YEA"}],
                        },
                        {
                            "link_id": "nhs_mhs_ack_requested",
                            "text": "nhs_mhs_ack_requested",
                            "answer": [{"valueString": "never"}],
                        },
                        {
                            "link_id": "nhs_mhs_cpa_id",
                            "text": "nhs_mhs_cpa_id",
                            "answer": [
                                {"valueString": "S2001930A2012103"}
                            ],  # pragma: allowlist secret
                        },
                        {
                            "link_id": "nhs_mhs_duplicate_elimination",
                            "text": "nhs_mhs_duplicate_elimination",
                            "answer": [{"valueString": "never"}],
                        },
                        {
                            "link_id": "nhs_mhs_end_point",
                            "text": "nhs_mhs_end_point",
                            "answer": [
                                {
                                    "valueString": "https://rmmid.nis1.national.ncrs.nhs.uk/reliablemessaging/forwardreliable"
                                }
                            ],
                        },
                        {
                            "link_id": "nhs_mhs_fqdn",
                            "text": "nhs_mhs_fqdn",
                            "answer": [{"valueString": "appliedendpoint.spine.nhs.uk"}],
                        },
                        {
                            "link_id": "nhs_mhs_in",
                            "text": "nhs_mhs_in",
                            "answer": [{"valueString": "ReliableIntermediary"}],
                        },
                        {
                            "link_id": "nhs_mhs_party_key",
                            "text": "nhs_mhs_party_key",
                            "answer": [{"valueString": "YEA-801248"}],
                        },
                        {
                            "link_id": "nhs_mhs_sn",
                            "text": "nhs_mhs_sn",
                            "answer": [{"valueString": "urn:nhs:names:services:tms"}],
                        },
                        {
                            "link_id": "nhs_mhs_svc_ia",
                            "text": "nhs_mhs_svc_ia",
                            "answer": [
                                {
                                    "valueString": "urn:nhs:names:services:tms:ReliableIntermediary"
                                }
                            ],
                        },
                        {
                            "link_id": "nhs_mhs_sync_reply_mode",
                            "text": "nhs_mhs_sync_reply_mode",
                            "answer": [{"valueString": "None"}],
                        },
                        {
                            "linkId": "nhs_mhs_persist_duration",
                            "text": "nhs_mhs_persist_duration",
                            "answer": [],
                        },
                        {
                            "linkId": "nhs_mhs_retries",
                            "text": "nhs_mhs_retries",
                            "answer": [],
                        },
                        {
                            "linkId": "nhs_mhs_retry_interval",
                            "text": "nhs_mhs_retry_interval",
                            "answer": [],
                        },
                        {
                            "link_id": "unique_identifier",  # pragma: allowlist secret
                            "text": "unique_identifier",
                            "answer": [
                                {"valueString": "S2001930A2012103"}
                            ],  # pragma: allowlist secret
                        },
                    ],
                },
            ],
        },
        {
            "resourceType": "Bundle",
            "id": "11C55B9F-0D7A-41DB-8BE6-306DABA69701",
            "type": "collection",
            "total": 1,
            "link": [
                {
                    "relation": "self",
                    "url": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cah",
                }
            ],
            "entry": [
                {
                    "fullUrl": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cah",
                    "resource": {
                        "resourceType": "Device",
                        "deviceName": [
                            {
                                "name": "ExpressIntermediary",
                                "type": "user-friendly-name",
                            }
                        ],
                        "definition": {
                            "identifier": {
                                "system": "connecting-party-manager/device-type",
                                "value": "endpoint",
                            }
                        },
                        "identifier": [
                            {
                                "system": "https://fhir.nhs.uk/Id/nhsMhsPartyKey|Extension-SDS-NhsServiceInteractionId",
                                "value": "YES-0000806|urn:nhs:names:services:tms:ExpressIntermediary",
                            },
                            {
                                "system": "https://fhir.nhs.uk/Id/nhsMHSId",
                                "value": "S20001A000190",  # pragma: allowlist secret
                            },
                        ],
                        "owner": {
                            "identifier": {
                                "system": "connecting-party-manager/product-team-id",
                                "value": "ae2ab026-0b53-7e7c-7a65-f0407a6e75f5",
                            }
                        },
                    },
                    "search": {"mode": "match"},
                },
                {
                    "resourceType": "QuestionnaireResponse",
                    "identifier": "YES-0000806|urn:nhs:names:services:tms:ExpressIntermediary",
                    "questionnaire": "https://cpm.co.uk/Questionnaire/spine_endpoint|v1",
                    "status": "completed",
                    "subject": {
                        "reference": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cah"
                    },
                    "authored": "<dateTime>",
                    "author": {
                        "reference": "https://cpm.co.uk/Organization/ae2ab026-0b53-7e7c-7a65-f0407a6e75f5"
                    },
                    "item": [
                        {
                            "link_id": "object_class",
                            "text": "object_class",
                            "answer": [
                                {"valueString": "nhsMhs"},
                                {"valueString": "top"},
                            ],
                        },
                        {
                            "linkId": "nhs_mhs_actor",
                            "text": "nhs_mhs_actor",
                            "answer": [],
                        },
                        {
                            "link_id": "nhs_id_code",
                            "text": "nhs_id_code",
                            "answer": [{"valueString": "YES"}],
                        },
                        {
                            "link_id": "nhs_mhs_ack_requested",
                            "text": "nhs_mhs_ack_requested",
                            "answer": [{"valueString": "never"}],
                        },
                        {
                            "link_id": "nhs_mhs_cpa_id",
                            "text": "nhs_mhs_cpa_id",
                            "answer": [
                                {"valueString": "S20001A000190"}
                            ],  # pragma: allowlist secret
                        },
                        {
                            "link_id": "nhs_mhs_duplicate_elimination",
                            "text": "nhs_mhs_duplicate_elimination",
                            "answer": [{"valueString": "never"}],
                        },
                        {
                            "link_id": "nhs_mhs_end_point",
                            "text": "nhs_mhs_end_point",
                            "answer": [
                                {
                                    "valueString": "https://msg.int.spine2.ncrs.nhs.uk/reliablemessaging/intermediary"
                                }
                            ],
                        },
                        {
                            "link_id": "nhs_mhs_fqdn",
                            "text": "nhs_mhs_fqdn",
                            "answer": [{"valueString": "msg.int.spine2.ncrs.nhs.uk"}],
                        },
                        {
                            "link_id": "nhs_mhs_in",
                            "text": "nhs_mhs_in",
                            "answer": [{"valueString": "ExpressIntermediary"}],
                        },
                        {
                            "link_id": "nhs_mhs_party_key",
                            "text": "nhs_mhs_party_key",
                            "answer": [{"valueString": "YES-0000806"}],
                        },
                        {
                            "link_id": "nhs_mhs_sn",
                            "text": "nhs_mhs_sn",
                            "answer": [{"valueString": "urn:nhs:names:services:tms"}],
                        },
                        {
                            "link_id": "nhs_mhs_svc_ia",
                            "text": "nhs_mhs_svc_ia",
                            "answer": [
                                {
                                    "valueString": "urn:nhs:names:services:tms:ExpressIntermediary"
                                }
                            ],
                        },
                        {
                            "link_id": "nhs_mhs_sync_reply_mode",
                            "text": "nhs_mhs_sync_reply_mode",
                            "answer": [{"valueString": "None"}],
                        },
                        {
                            "linkId": "nhs_mhs_persist_duration",
                            "text": "nhs_mhs_persist_duration",
                            "answer": [],
                        },
                        {
                            "linkId": "nhs_mhs_retries",
                            "text": "nhs_mhs_retries",
                            "answer": [],
                        },
                        {
                            "linkId": "nhs_mhs_retry_interval",
                            "text": "nhs_mhs_retry_interval",
                            "answer": [],
                        },
                        {
                            "link_id": "unique_identifier",  # pragma: allowlist secret
                            "text": "unique_identifier",
                            "answer": [
                                {"valueString": "S20001A000190"}
                            ],  # pragma: allowlist secret
                        },
                    ],
                },
            ],
        },
        {
            "resourceType": "Bundle",
            "id": "11C55B9F-0D7A-41DB-8BE6-306DABA69701",
            "type": "collection",
            "total": 1,
            "link": [
                {
                    "relation": "self",
                    "url": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cah",
                }
            ],
            "entry": [
                {
                    "fullUrl": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cah",
                    "resource": {
                        "resourceType": "Device",
                        "deviceName": [
                            {
                                "name": "ExpressIntermediary",
                                "type": "user-friendly-name",
                            }
                        ],
                        "definition": {
                            "identifier": {
                                "system": "connecting-party-manager/device-type",
                                "value": "endpoint",
                            }
                        },
                        "identifier": [
                            {
                                "system": "https://fhir.nhs.uk/Id/nhsMhsPartyKey|Extension-SDS-NhsServiceInteractionId",
                                "value": "YEA-801248|urn:nhs:names:services:tms:ExpressIntermediary",
                            },
                            {
                                "system": "https://fhir.nhs.uk/Id/nhsMHSId",
                                "value": "S2001930A2012104",  # pragma: allowlist secret
                            },
                        ],
                        "owner": {
                            "identifier": {
                                "system": "connecting-party-manager/product-team-id",
                                "value": "ae2ab026-0b53-7e7c-7a65-f0407a6e75f5",
                            }
                        },
                    },
                    "search": {"mode": "match"},
                },
                {
                    "resourceType": "QuestionnaireResponse",
                    "identifier": "YEA-801248|urn:nhs:names:services:tms:ExpressIntermediary",
                    "questionnaire": "https://cpm.co.uk/Questionnaire/spine_endpoint|v1",
                    "status": "completed",
                    "subject": {
                        "reference": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cah"
                    },
                    "authored": "<dateTime>",
                    "author": {
                        "reference": "https://cpm.co.uk/Organization/ae2ab026-0b53-7e7c-7a65-f0407a6e75f5"
                    },
                    "item": [
                        {
                            "link_id": "object_class",
                            "text": "object_class",
                            "answer": [
                                {"valueString": "nhsMhs"},
                                {"valueString": "top"},
                            ],
                        },
                        {
                            "linkId": "nhs_mhs_actor",
                            "text": "nhs_mhs_actor",
                            "answer": [],
                        },
                        {
                            "link_id": "nhs_id_code",
                            "text": "nhs_id_code",
                            "answer": [{"valueString": "YEA"}],
                        },
                        {
                            "link_id": "nhs_mhs_ack_requested",
                            "text": "nhs_mhs_ack_requested",
                            "answer": [{"valueString": "never"}],
                        },
                        {
                            "link_id": "nhs_mhs_cpa_id",
                            "text": "nhs_mhs_cpa_id",
                            "answer": [
                                {"valueString": "S2001930A2012104"}
                            ],  # pragma: allowlist secret
                        },
                        {
                            "link_id": "nhs_mhs_duplicate_elimination",
                            "text": "nhs_mhs_duplicate_elimination",
                            "answer": [{"valueString": "never"}],
                        },
                        {
                            "link_id": "nhs_mhs_end_point",
                            "text": "nhs_mhs_end_point",
                            "answer": [
                                {
                                    "valueString": "https://ummid.nis1.national.ncrs.nhs.uk/reliablemessaging/intermediary"
                                }
                            ],
                        },
                        {
                            "link_id": "nhs_mhs_fqdn",
                            "text": "nhs_mhs_fqdn",
                            "answer": [{"valueString": "appliedendpoint.spine.nhs.uk"}],
                        },
                        {
                            "link_id": "nhs_mhs_in",
                            "text": "nhs_mhs_in",
                            "answer": [{"valueString": "ExpressIntermediary"}],
                        },
                        {
                            "link_id": "nhs_mhs_party_key",
                            "text": "nhs_mhs_party_key",
                            "answer": [{"valueString": "YEA-801248"}],
                        },
                        {
                            "link_id": "nhs_mhs_sn",
                            "text": "nhs_mhs_sn",
                            "answer": [{"valueString": "urn:nhs:names:services:tms"}],
                        },
                        {
                            "link_id": "nhs_mhs_svc_ia",
                            "text": "nhs_mhs_svc_ia",
                            "answer": [
                                {
                                    "valueString": "urn:nhs:names:services:tms:ExpressIntermediary"
                                }
                            ],
                        },
                        {
                            "link_id": "nhs_mhs_sync_reply_mode",
                            "text": "nhs_mhs_sync_reply_mode",
                            "answer": [{"valueString": "None"}],
                        },
                        {
                            "linkId": "nhs_mhs_persist_duration",
                            "text": "nhs_mhs_persist_duration",
                            "answer": [],
                        },
                        {
                            "linkId": "nhs_mhs_retries",
                            "text": "nhs_mhs_retries",
                            "answer": [],
                        },
                        {
                            "linkId": "nhs_mhs_retry_interval",
                            "text": "nhs_mhs_retry_interval",
                            "answer": [],
                        },
                        {
                            "link_id": "unique_identifier",  # pragma: allowlist secret
                            "text": "unique_identifier",
                            "answer": [
                                {"valueString": "S2001930A2012104"}
                            ],  # pragma: allowlist secret
                        },
                    ],
                },
            ],
        },
    ],
}
