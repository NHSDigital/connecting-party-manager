devices = [
    {
        "id": "c7e3c61f-4613-402a-9028-dae4ee7ea6d0",
        "name": "My-device-Device",
        "type": "device",
        "product_team_id": "12345678-1234-5678-1234-567812345678",
        "ods_code": "ABC",
        "keys": [
            {"key_type": "product_id", "key_value": "P.WWW-XXX"},
            {
                "key_type": "message_handling_system_id",
                "key_value": "ABC:ABC-12345:abc123",
            },
        ],
        "tags": [
            {
                "components": [
                    ["ods_code", "ABC"],
                    ["party_key", "ABC-12345"],
                    ["interaction_id", "abc123"],
                ]
            }
        ],
        "questionnaire_responses": {
            "spine_endpoint/1/2014-01-01:01": [
                {
                    "questionnaire": ["spine_endpoint", "1"],
                    "status": "active",
                    "responses": [
                        {"object_class": ["nhsMhs"]},
                        {
                            "unique_identifier": [
                                "a83e020a3fe9c2988a36"  # pragma: allowlist secret
                            ]
                        },
                        {"nhs_approver_urp": ["System"]},
                        {"nhs_contract_property_template_key": ["17"]},
                        {"nhs_date_approved": ["20211118094930"]},
                        {"nhs_date_dns_approved": ["20211118094930"]},
                        {"nhs_date_requested": ["20191113101013"]},
                        {"nhs_dns_approver": ["System"]},
                        {"nhs_ep_interaction_type": ["fhir"]},
                        {"nhs_id_code": ["D81631"]},
                        {"nhs_mhs_ack_requested": ["never"]},
                        {"nhs_mhs_cpa_id": ["a83e020a3fe9c2988a36"]},
                        {"nhs_mhs_duplicate_elimination": ["never"]},
                        {
                            "nhs_mhs_end_point": [
                                "https://systmonespine1.tpp.nme.ncrs.nhs.uk/SystmOneMHS/NHSConnect/D81631/STU3/1"
                            ]
                        },
                        {"nhs_mhs_fqdn": ["systmonespine1.tpp.nme.ncrs.nhs.uk"]},
                        {"nhs_mhs_in": ["fhir:rest:read:location-1"]},
                        {"nhs_mhs_ip_address": ["20.146.248.152"]},
                        {"nhs_mhs_is_authenticated": ["none"]},
                        {"nhs_mhs_manufacturer_org": ["YGA"]},
                        {"nhs_mhs_party_key": ["D81631-827817"]},
                        {"nhs_mhs_sn": ["urn:nhs:names:services:gpconnect"]},
                        {
                            "nhs_mhs_svc_ia": [
                                "urn:nhs:names:services:gpconnect:fhir:rest:read:location-1"
                            ]
                        },
                        {"nhs_mhs_sync_reply_mode": ["none"]},
                        {"nhs_product_key": ["5952"]},
                        {"nhs_product_name": ["TPP"]},
                        {"nhs_product_version": ["GP Connect"]},
                        {
                            "nhs_requestor_urp": [
                                "uniqueidentifier=688491328565,uniqueidentifier=495227626043,uid=709580513048,ou=people, o=nhs"
                            ]
                        },
                    ],
                }
            ]
        },
        "status": "active",
        "created_on": "2024-06-14 09:31:14.740983",
        "updated_on": "2024-06-14 09:31:14.740983",
        "deleted_on": "2024-06-14 09:31:14.740983",
    }
]

endpoints = [
    {
        "id": "c7e3c61f-4613-402a-9028-dae4ee7ea6d0",
        "name": "My-device-Endpoint",
        "type": "endpoint",
        "product_team_id": "12345678-1234-5678-1234-567812345678",
        "ods_code": "ABC",
        "keys": [
            {"key_type": "product_id", "key_value": "P.WWW-XXX"},
            {
                "key_type": "message_handling_system_id",
                "key_value": "ABC:ABC-12345:abc123",
            },
        ],
        "tags": [
            {
                "components": [
                    ["ods_code", "ABC"],
                    ["party_key", "ABC-12345"],
                    ["interaction_id", "abc123"],
                ]
            }
        ],
        "questionnaire_responses": {
            "spine_endpoint/1/2014-01-01:01": [
                {
                    "questionnaire": ["spine_endpoint", "1"],
                    "status": "active",
                    "responses": [
                        {"object_class": ["nhsMhs"]},
                        {
                            "unique_identifier": [
                                "a83e020a3fe9c2988a36"  # pragma: allowlist secret
                            ]
                        },
                        {"nhs_approver_urp": ["System"]},
                        {"nhs_contract_property_template_key": ["17"]},
                        {"nhs_date_approved": ["20211118094930"]},
                        {"nhs_date_dns_approved": ["20211118094930"]},
                        {"nhs_date_requested": ["20191113101013"]},
                        {"nhs_dns_approver": ["System"]},
                        {"nhs_ep_interaction_type": ["fhir"]},
                        {"nhs_id_code": ["D81631"]},
                        {"nhs_mhs_ack_requested": ["never"]},
                        {"nhs_mhs_cpa_id": ["a83e020a3fe9c2988a36"]},
                        {"nhs_mhs_duplicate_elimination": ["never"]},
                        {
                            "nhs_mhs_end_point": [
                                "https://systmonespine1.tpp.nme.ncrs.nhs.uk/SystmOneMHS/NHSConnect/D81631/STU3/1"
                            ]
                        },
                        {"nhs_mhs_fqdn": ["systmonespine1.tpp.nme.ncrs.nhs.uk"]},
                        {"nhs_mhs_in": ["fhir:rest:read:location-1"]},
                        {"nhs_mhs_ip_address": ["20.146.248.152"]},
                        {"nhs_mhs_is_authenticated": ["none"]},
                        {"nhs_mhs_manufacturer_org": ["YGA"]},
                        {"nhs_mhs_party_key": ["D81631-827817"]},
                        {"nhs_mhs_sn": ["urn:nhs:names:services:gpconnect"]},
                        {
                            "nhs_mhs_svc_ia": [
                                "urn:nhs:names:services:gpconnect:fhir:rest:read:location-1"
                            ]
                        },
                        {"nhs_mhs_sync_reply_mode": ["none"]},
                        {"nhs_product_key": ["5952"]},
                        {"nhs_product_name": ["TPP"]},
                        {"nhs_product_version": ["GP Connect"]},
                        {
                            "nhs_requestor_urp": [
                                "uniqueidentifier=688491328565,uniqueidentifier=495227626043,uid=709580513048,ou=people, o=nhs"
                            ]
                        },
                    ],
                }
            ]
        },
        "status": "active",
        "created_on": "2024-06-14 09:31:14.740983",
        "updated_on": "2024-06-14 09:31:14.740983",
        "deleted_on": "2024-06-14 09:31:14.740983",
    }
]