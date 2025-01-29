Feature: Create "Message Set" Device Reference Data - success scenarios
  These scenarios demonstrate successful "Message Set" Device Reference Data creation

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario Outline: Successfully create an "MHS Message Set" Device Reference Data, with no questionnaire responses
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/<product_team_id>/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I note the response field "$.keys.0.key_value" as "party_key"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/<product_team_id>/Product/<product_id>/dev/DeviceReferenceData/MhsMessageSet"
    Then I receive a status code "201" with body
      | path                    | value                           |
      | id                      | << ignore >>                    |
      | name                    | F5H1R-850000 - MHS Message Sets |
      | status                  | active                          |
      | environment             | dev                             |
      | product_id              | ${ note(product_id) }           |
      | product_team_id         | ${ note(product_team_id) }      |
      | ods_code                | F5H1R                           |
      | questionnaire_responses | {}                              |
      | created_on              | << ignore >>                    |
      | updated_on              | << ignore >>                    |
      | deleted_on              | << ignore >>                    |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 365              |
    And I note the response field "$.id" as "device_reference_data_id"
    When I make a "GET" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/${ note(device_reference_data_id) }"
    Then I receive a status code "200" with body
      | path                    | value                               |
      | id                      | ${ note(device_reference_data_id) } |
      | name                    | F5H1R-850000 - MHS Message Sets     |
      | status                  | active                              |
      | environment             | dev                                 |
      | product_id              | ${ note(product_id) }               |
      | product_team_id         | ${ note(product_team_id) }          |
      | ods_code                | F5H1R                               |
      | questionnaire_responses | {}                                  |
      | created_on              | << ignore >>                        |
      | updated_on              | << ignore >>                        |
      | deleted_on              | << ignore >>                        |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 365              |

    Examples:
      | product_team_id            | product_id            |
      | ${ note(product_team_id) } | ${ note(product_id) } |
      | ${ note(product_team_id) } | ${ note(party_key) }  |
      | FOOBAR                     | ${ note(product_id) } |
      | FOOBAR                     | ${ note(party_key) }  |

  Scenario: Successfully create an "MHS Message Set" Device Reference Data, with questionnaire responses
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I note the response field "$.keys.0.key_value" as "party_key"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/MhsMessageSet" with body:
      | path                                                                                        | value                          |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS SN                                     | urn:nhs:names:services:ers     |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS IN                                     | READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_mhs_message_sets.1.MHS SN                                     | urn:nhs:names:services:ebs     |
      | questionnaire_responses.spine_mhs_message_sets.1.MHS IN                                     | PRSC_IN080000UK07              |
      | questionnaire_responses.spine_mhs_message_sets.1.Reliability Configuration Retry Interval   | PT1M                           |
      | questionnaire_responses.spine_mhs_message_sets.1.Reliability Configuration Retries          | ${ integer(2) }                |
      | questionnaire_responses.spine_mhs_message_sets.1.Reliability Configuration Persist Duration | PT10M                          |
    Then I receive a status code "201" with body
      | path                                                                                               | value                                                                          |
      | id                                                                                                 | << ignore >>                                                                   |
      | name                                                                                               | F5H1R-850000 - MHS Message Sets                                                |
      | status                                                                                             | active                                                                         |
      | environment                                                                                        | dev                                                                            |
      | product_id                                                                                         | ${ note(product_id) }                                                          |
      | product_team_id                                                                                    | ${ note(product_team_id) }                                                     |
      | ods_code                                                                                           | F5H1R                                                                          |
      | created_on                                                                                         | << ignore >>                                                                   |
      | updated_on                                                                                         | << ignore >>                                                                   |
      | deleted_on                                                                                         | << ignore >>                                                                   |
      | questionnaire_responses.spine_mhs_message_sets/1.0.id                                              | << ignore >>                                                                   |
      | questionnaire_responses.spine_mhs_message_sets/1.0.questionnaire_name                              | spine_mhs_message_sets                                                         |
      | questionnaire_responses.spine_mhs_message_sets/1.0.questionnaire_version                           | 1                                                                              |
      | questionnaire_responses.spine_mhs_message_sets/1.0.created_on                                      | << ignore >>                                                                   |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.MHS SN                                     | urn:nhs:names:services:ers                                                     |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.MHS IN                                     | READ_PRACTITIONER_ROLE_R4_V001                                                 |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.Interaction ID                             | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001                      |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.MHS CPA ID                                 | ${ note(party_key) }:urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.Unique Identifier                          | ${ note(party_key) }:urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_mhs_message_sets/1.1.id                                              | << ignore >>                                                                   |
      | questionnaire_responses.spine_mhs_message_sets/1.1.questionnaire_name                              | spine_mhs_message_sets                                                         |
      | questionnaire_responses.spine_mhs_message_sets/1.1.questionnaire_version                           | 1                                                                              |
      | questionnaire_responses.spine_mhs_message_sets/1.1.created_on                                      | << ignore >>                                                                   |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.MHS IN                                     | PRSC_IN080000UK07                                                              |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.MHS SN                                     | urn:nhs:names:services:ebs                                                     |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Interaction ID                             | urn:nhs:names:services:ebs:PRSC_IN080000UK07                                   |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.MHS CPA ID                                 | ${ note(party_key) }:urn:nhs:names:services:ebs:PRSC_IN080000UK07              |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Unique Identifier                          | ${ note(party_key) }:urn:nhs:names:services:ebs:PRSC_IN080000UK07              |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Reliability Configuration Retry Interval   | PT1M                                                                           |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Reliability Configuration Retries          | ${ integer(2) }                                                                |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Reliability Configuration Persist Duration | PT10M                                                                          |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 1582             |
    And I note the response field "$.id" as "device_reference_data_id"
    When I make a "GET" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/${ note(device_reference_data_id) }"
    Then I receive a status code "200" with body
      | path                                                                                               | value                                                                          |
      | id                                                                                                 | ${ note(device_reference_data_id) }                                            |
      | name                                                                                               | F5H1R-850000 - MHS Message Sets                                                |
      | status                                                                                             | active                                                                         |
      | environment                                                                                        | dev                                                                            |
      | product_id                                                                                         | ${ note(product_id) }                                                          |
      | product_team_id                                                                                    | ${ note(product_team_id) }                                                     |
      | ods_code                                                                                           | F5H1R                                                                          |
      | created_on                                                                                         | << ignore >>                                                                   |
      | updated_on                                                                                         | << ignore >>                                                                   |
      | deleted_on                                                                                         | << ignore >>                                                                   |
      | questionnaire_responses.spine_mhs_message_sets/1.0.id                                              | << ignore >>                                                                   |
      | questionnaire_responses.spine_mhs_message_sets/1.0.questionnaire_name                              | spine_mhs_message_sets                                                         |
      | questionnaire_responses.spine_mhs_message_sets/1.0.questionnaire_version                           | 1                                                                              |
      | questionnaire_responses.spine_mhs_message_sets/1.0.created_on                                      | << ignore >>                                                                   |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.MHS SN                                     | urn:nhs:names:services:ers                                                     |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.MHS IN                                     | READ_PRACTITIONER_ROLE_R4_V001                                                 |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.Interaction ID                             | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001                      |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.MHS CPA ID                                 | ${ note(party_key) }:urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.Unique Identifier                          | ${ note(party_key) }:urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_mhs_message_sets/1.1.id                                              | << ignore >>                                                                   |
      | questionnaire_responses.spine_mhs_message_sets/1.1.questionnaire_name                              | spine_mhs_message_sets                                                         |
      | questionnaire_responses.spine_mhs_message_sets/1.1.questionnaire_version                           | 1                                                                              |
      | questionnaire_responses.spine_mhs_message_sets/1.1.created_on                                      | << ignore >>                                                                   |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.MHS IN                                     | PRSC_IN080000UK07                                                              |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.MHS SN                                     | urn:nhs:names:services:ebs                                                     |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Interaction ID                             | urn:nhs:names:services:ebs:PRSC_IN080000UK07                                   |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.MHS CPA ID                                 | ${ note(party_key) }:urn:nhs:names:services:ebs:PRSC_IN080000UK07              |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Unique Identifier                          | ${ note(party_key) }:urn:nhs:names:services:ebs:PRSC_IN080000UK07              |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Reliability Configuration Retry Interval   | PT1M                                                                           |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Reliability Configuration Retries          | ${ integer(2) }                                                                |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Reliability Configuration Persist Duration | PT10M                                                                          |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 1582             |
