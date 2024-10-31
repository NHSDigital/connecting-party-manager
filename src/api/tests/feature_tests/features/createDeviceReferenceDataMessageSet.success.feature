Feature: Create "Message Set" Device Reference Data - success scenarios
  These scenarios demonstrate successful "Message Set" Device Reference Data creation

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Successfully create an "MHS Message Set" Device Reference Data, with no questionnaire responses
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path         | value            |
      | product_name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I note the response field "$.keys.0.key_value" as "party_key"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/MhsMessageSet"
    Then I receive a status code "201" with body
      | path                    | value                          |
      | id                      | << ignore >>                   |
      | name                    | F5H1R-850000 - MHS Message Set |
      | product_id              | ${ note(product_id) }          |
      | product_team_id         | ${ note(product_team_id) }     |
      | ods_code                | F5H1R                          |
      | questionnaire_responses | {}                             |
      | created_on              | << ignore >>                   |
      | updated_on              | << ignore >>                   |
      | deleted_on              | << ignore >>                   |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 322              |
    And I note the response field "$.id" as "device_reference_data_id"
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/${ note(device_reference_data_id) }"
    Then I receive a status code "200" with body
      | path                    | value                               |
      | id                      | ${ note(device_reference_data_id) } |
      | name                    | F5H1R-850000 - MHS Message Set      |
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
      | Content-Length | 322              |

  Scenario: Successfully create an "MHS Message Set" Device Reference Data, with questionnaire responses
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path         | value            |
      | product_name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I note the response field "$.keys.0.key_value" as "party_key"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/MhsMessageSet" with body:
      | path                                                                                        | value                                                     |
      | questionnaire_responses.spine_mhs_message_sets.0.Interaction ID                             | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS SN                                     | urn:nhs:names:services:ers                                |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS IN                                     | READ_PRACTITIONER_ROLE_R4_V001                            |
      | questionnaire_responses.spine_mhs_message_sets.1.Interaction ID                             | urn:nhs:names:services:ebs:PRSC_IN080000UK07              |
      | questionnaire_responses.spine_mhs_message_sets.1.MHS SN                                     | urn:nhs:names:services:ebs                                |
      | questionnaire_responses.spine_mhs_message_sets.1.MHS IN                                     | PRSC_IN080000UK07                                         |
      | questionnaire_responses.spine_mhs_message_sets.1.Reliability Configuration Retry Interval   | PT1M                                                      |
      | questionnaire_responses.spine_mhs_message_sets.1.Reliability Configuration Retries          | ${ integer(2) }                                           |
      | questionnaire_responses.spine_mhs_message_sets.1.Reliability Configuration Persist Duration | PT10M                                                     |
    Then I receive a status code "201" with body
      | path                                                                                               | value                                                     |
      | id                                                                                                 | << ignore >>                                              |
      | name                                                                                               | F5H1R-850000 - MHS Message Set                            |
      | product_id                                                                                         | ${ note(product_id) }                                     |
      | product_team_id                                                                                    | ${ note(product_team_id) }                                |
      | ods_code                                                                                           | F5H1R                                                     |
      | created_on                                                                                         | << ignore >>                                              |
      | updated_on                                                                                         | << ignore >>                                              |
      | deleted_on                                                                                         | << ignore >>                                              |
      | questionnaire_responses.spine_mhs_message_sets/1.0.id                                              | << ignore >>                                              |
      | questionnaire_responses.spine_mhs_message_sets/1.0.questionnaire_name                              | spine_mhs_message_sets                                    |
      | questionnaire_responses.spine_mhs_message_sets/1.0.questionnaire_version                           | 1                                                         |
      | questionnaire_responses.spine_mhs_message_sets/1.0.created_on                                      | << ignore >>                                              |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.Interaction ID                             | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.MHS SN                                     | urn:nhs:names:services:ers                                |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.MHS IN                                     | READ_PRACTITIONER_ROLE_R4_V001                            |
      | questionnaire_responses.spine_mhs_message_sets/1.1.id                                              | << ignore >>                                              |
      | questionnaire_responses.spine_mhs_message_sets/1.1.questionnaire_name                              | spine_mhs_message_sets                                    |
      | questionnaire_responses.spine_mhs_message_sets/1.1.questionnaire_version                           | 1                                                         |
      | questionnaire_responses.spine_mhs_message_sets/1.1.created_on                                      | << ignore >>                                              |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Interaction ID                             | urn:nhs:names:services:ebs:PRSC_IN080000UK07              |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.MHS SN                                     | urn:nhs:names:services:ebs                                |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.MHS IN                                     | PRSC_IN080000UK07                                         |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Reliability Configuration Retry Interval   | PT1M                                                      |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Reliability Configuration Retries          | ${ integer(2) }                                           |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Reliability Configuration Persist Duration | PT10M                                                     |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 1199             |
    And I note the response field "$.id" as "device_reference_data_id"
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/${ note(device_reference_data_id) }"
    Then I receive a status code "200" with body
      | path                                                                                               | value                                                     |
      | id                                                                                                 | ${ note(device_reference_data_id) }                       |
      | name                                                                                               | F5H1R-850000 - MHS Message Set                            |
      | product_id                                                                                         | ${ note(product_id) }                                     |
      | product_team_id                                                                                    | ${ note(product_team_id) }                                |
      | ods_code                                                                                           | F5H1R                                                     |
      | created_on                                                                                         | << ignore >>                                              |
      | updated_on                                                                                         | << ignore >>                                              |
      | deleted_on                                                                                         | << ignore >>                                              |
      | questionnaire_responses.spine_mhs_message_sets/1.0.id                                              | << ignore >>                                              |
      | questionnaire_responses.spine_mhs_message_sets/1.0.questionnaire_name                              | spine_mhs_message_sets                                    |
      | questionnaire_responses.spine_mhs_message_sets/1.0.questionnaire_version                           | 1                                                         |
      | questionnaire_responses.spine_mhs_message_sets/1.0.created_on                                      | << ignore >>                                              |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.Interaction ID                             | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.MHS SN                                     | urn:nhs:names:services:ers                                |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.MHS IN                                     | READ_PRACTITIONER_ROLE_R4_V001                            |
      | questionnaire_responses.spine_mhs_message_sets/1.1.id                                              | << ignore >>                                              |
      | questionnaire_responses.spine_mhs_message_sets/1.1.questionnaire_name                              | spine_mhs_message_sets                                    |
      | questionnaire_responses.spine_mhs_message_sets/1.1.questionnaire_version                           | 1                                                         |
      | questionnaire_responses.spine_mhs_message_sets/1.1.created_on                                      | << ignore >>                                              |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Interaction ID                             | urn:nhs:names:services:ebs:PRSC_IN080000UK07              |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.MHS SN                                     | urn:nhs:names:services:ebs                                |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.MHS IN                                     | PRSC_IN080000UK07                                         |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Reliability Configuration Retry Interval   | PT1M                                                      |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Reliability Configuration Retries          | ${ integer(2) }                                           |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Reliability Configuration Persist Duration | PT10M                                                     |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 1199             |
