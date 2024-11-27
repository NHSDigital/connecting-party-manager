Feature: Create MHS Device - success scenarios
  These scenarios demonstrate successful MHS Device creation

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario Outline: Successfully create a MHS Device
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/<product_team_id>/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I note the response field "$.keys.0.key_type" as "party_key_tag"
    And I note the response field "$.keys.0.key_value" as "party_key_tag_value"
    And I have already made a "POST" request with "default" headers to "ProductTeam/<product_team_id>/Product/${ note(product_id) }/DeviceReferenceData/MhsMessageSet" with body:
      | path                                                            | value                                                     |
      | questionnaire_responses.spine_mhs_message_sets.0.Interaction ID | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS SN         | urn:nhs:names:services:ers                                |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS IN         | READ_PRACTITIONER_ROLE_R4_V001                            |
    And I note the response field "$.id" as "message_set_drd_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/Device/MessageHandlingSystem" with body:
      | path                                                               | value              |
      | questionnaire_responses.spine_mhs.0.Address                        | http://example.com |
      | questionnaire_responses.spine_mhs.0.Unique Identifier              | 123456             |
      | questionnaire_responses.spine_mhs.0.Managing Organization          | Example Org        |
      | questionnaire_responses.spine_mhs.0.MHS Manufacturer Organisation  | AAA                |
      | questionnaire_responses.spine_mhs.0.MHS Party key                  | party-key-001      |
      | questionnaire_responses.spine_mhs.0.MHS CPA ID                     | cpa-id-001         |
      | questionnaire_responses.spine_mhs.0.Approver URP                   | approver-123       |
      | questionnaire_responses.spine_mhs.0.Contract Property Template Key | contract-key-001   |
      | questionnaire_responses.spine_mhs.0.Date Approved                  | 2024-01-01         |
      | questionnaire_responses.spine_mhs.0.Date DNS Approved              | 2024-01-02         |
      | questionnaire_responses.spine_mhs.0.Date Requested                 | 2024-01-03         |
      | questionnaire_responses.spine_mhs.0.DNS Approver                   | dns-approver-456   |
      | questionnaire_responses.spine_mhs.0.Interaction Type               | FHIR               |
      | questionnaire_responses.spine_mhs.0.MHS FQDN                       | mhs.example.com    |
      | questionnaire_responses.spine_mhs.0.MHS Is Authenticated           | PERSISTENT         |
      | questionnaire_responses.spine_mhs.0.Product Key                    | product-key-001    |
      | questionnaire_responses.spine_mhs.0.Requestor URP                  | requestor-789      |
    Then I receive a status code "201" with body
      | path                    | value                                                                  |
      | id                      | << ignore >>                                                           |
      | name                    | F5H1R-850000 - Message Handling System                                 |
      | status                  | active                                                                 |
      | product_id              | ${ note(product_id) }                                                  |
      | product_team_id         | ${ note(product_team_id) }                                             |
      | ods_code                | F5H1R                                                                  |
      | created_on              | << ignore >>                                                           |
      | updated_on              | << ignore >>                                                           |
      | deleted_on              | << ignore >>                                                           |
      | keys.0.key_type         | cpa_id                                                                 |
      | keys.0.key_value        | F5H1R-850000:urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses | << ignore >>                                                           |
      | device_reference_data   | << ignore >>                                                           |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 1354             |
    And I note the response field "$.id" as "device_id"
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/Device/${ note(device_id) }"
    Then I receive a status code "200" with body
      | path                                                                      | value                                                                  |
      | id                                                                        | ${ note(device_id) }                                                   |
      | name                                                                      | Product-MHS                                                            |
      | status                                                                    | active                                                                 |
      | product_id                                                                | ${ note(product_id) }                                                  |
      | product_team_id                                                           | ${ note(product_team_id) }                                             |
      | ods_code                                                                  | F5H1R                                                                  |
      | created_on                                                                | << ignore >>                                                           |
      | updated_on                                                                | << ignore >>                                                           |
      | deleted_on                                                                | << ignore >>                                                           |
      | keys.0.key_type                                                           | interaction_id                                                         |
      | keys.0.key_value                                                          | F5H1R-850000:urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
      | tags.0.0.0                                                                | ${ note(party_key_tag) }                                               |
      | tags.0.0.1                                                                | ${ note(party_key_tag_value) }                                         |
      | questionnaire_responses.spine_mhs/1.0.id                                  | << ignore >>                                                           |
      | questionnaire_responses.spine_mhs/1.0.questionnaire_name                  | spine_mhs                                                              |
      | questionnaire_responses.spine_mhs/1.0.questionnaire_version               | 1                                                                      |
      | questionnaire_responses.spine_mhs/1.0.created_on                          | << ignore >>                                                           |
      | questionnaire_responses.spine_mhs/1.0.data.Address                        | http://example.com                                                     |
      | questionnaire_responses.spine_mhs/1.0.data.Unique Identifier              | 123456                                                                 |
      | questionnaire_responses.spine_mhs/1.0.data.Managing Organization          | Example Org                                                            |
      | questionnaire_responses.spine_mhs/1.0.data.MHS Party key                  | party-key-001                                                          |
      | questionnaire_responses.spine_mhs/1.0.data.MHS CPA ID                     | cpa-id-001                                                             |
      | questionnaire_responses.spine_mhs/1.0.data.Approver URP                   | approver-123                                                           |
      | questionnaire_responses.spine_mhs/1.0.data.Contract Property Template Key | contract-key-001                                                       |
      | questionnaire_responses.spine_mhs/1.0.data.Date Approved                  | 2024-01-01                                                             |
      | questionnaire_responses.spine_mhs/1.0.data.Date DNS Approved              | 2024-01-02                                                             |
      | questionnaire_responses.spine_mhs/1.0.data.Date Requested                 | 2024-01-03                                                             |
      | questionnaire_responses.spine_mhs/1.0.data.DNS Approver                   | dns-approver-456                                                       |
      | questionnaire_responses.spine_mhs/1.0.data.Interaction Type               | FHIR                                                                   |
      | questionnaire_responses.spine_mhs/1.0.data.MHS FQDN                       | mhs.example.com                                                        |
      | questionnaire_responses.spine_mhs/1.0.data.MHS Is Authenticated           | PERSISTENT                                                             |
      | questionnaire_responses.spine_mhs/1.0.data.Product Key                    | product-key-001                                                        |
      | questionnaire_responses.spine_mhs/1.0.data.Requestor URP                  | requestor-789                                                          |
      | questionnaire_responses.spine_mhs_message_sets/1.0.id                     | << ignore >>                                                           |
      | questionnaire_responses.spine_mhs_message_sets/1.0.questionnaire_name     | spine_mhs_message_sets                                                 |
      | questionnaire_responses.spine_mhs_message_sets/1.0.questionnaire_version  | 1                                                                      |
      | questionnaire_responses.spine_mhs_message_sets/1.0.created_on             | << ignore >>                                                           |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.Interaction ID    | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001              |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.MHS SN            | urn:nhs:names:services:ers                                             |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.MHS IN            | READ_PRACTITIONER_ROLE_R4_V001                                         |
      | device_reference_data                                                     | << ignore >>                                                           |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 1736             |

    Examples:
      | product_team_id            | product_id            |
      | ${ note(product_team_id) } | ${ note(product_id) } |
      | ${ note(product_team_id) } | ${ note(party_key) }  |
      | FOOBAR                     | ${ note(product_id) } |
      | FOOBAR                     | ${ note(party_key) }  |
