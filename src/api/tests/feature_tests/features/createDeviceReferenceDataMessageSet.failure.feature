Feature: Create "Message Set" Device Reference Data - failure scenarios
  These scenarios demonstrate failure to create "Message Set" Device Reference Data

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Fail to create an "MHS Message Set" Device Reference Data, because it has not answered fields requried for the system generated fields
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/MhsMessageSet" with body:
      | path                                                    | value                      |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS SN | urn:nhs:names:services:ers |
    Then I receive a status code "400" with body
      | path             | value                                                                                       |
      | errors.0.code    | VALIDATION_ERROR                                                                            |
      | errors.0.message | The following required fields are missing in the response to spine_mhs_message_sets: MHS IN |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 148              |

  Scenario: Fail to create an "MHS Message Set" Device Reference Data, with invalid questionnaire response (bad value)
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/MhsMessageSet" with body:
      | path                                                                               | value                          |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS SN                            | urn:nhs:names:services:ers     |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS IN                            | READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_mhs_message_sets.0.Reliability Configuration Retries | two                            |
    Then I receive a status code "400" with body
      | path             | value                                                                                      |
      | errors.0.code    | VALIDATION_ERROR                                                                           |
      | errors.0.message | Failed to validate data against 'spine_mhs_message_sets/1': 'two' is not of type 'integer' |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 147              |

  Scenario: Fail to create an "MHS Message Set" Device Reference Data, with invalid questionnaire response (unknown field)
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/MhsMessageSet" with body:
      | path                                                           | value                          |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS SN        | urn:nhs:names:services:ers     |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS IN        | READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_mhs_message_sets.0.unknown_field | 123                            |
    Then I receive a status code "400" with body
      | path             | value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
      | errors.0.code    | VALIDATION_ERROR                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
      | errors.0.message | Payload contains unexpected fields: {'unknown_field'}. Expected fields are: ['Contract Property Template Key', 'Interaction Type', 'MHS IN', 'MHS IP Address', 'MHS Is Authenticated', 'MHS SN', 'Product Key', 'Reliability Configuration Ack Requested', 'Reliability Configuration Actor', 'Reliability Configuration Duplication Elimination', 'Reliability Configuration Persist Duration', 'Reliability Configuration Reply Mode', 'Reliability Configuration Retries', 'Reliability Configuration Retry Interval']. |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 563              |

  Scenario: Fail to create an "MHS Message Set" Device Reference Data, with invalid questionnaire name
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/MhsMessageSet" with body:
      | path                                                        | value |
      | questionnaire_responses.bad_questionnaire_name.0.some_value | 123   |
    Then I receive a status code "400" with body
      | path             | value                                                                                                                                                                             |
      | errors.0.code    | VALIDATION_ERROR                                                                                                                                                                  |
      | errors.0.message | CreateDeviceReferenceMessageSetsDataParams.questionnaire_responses.__key__: unexpected value; permitted: <QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS: 'spine_mhs_message_sets'> |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 234              |

  Scenario: Fail to create a second "MHS Message Set" Device Reference Data in the same EPR Product
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
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/MhsMessageSet"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/MhsMessageSet"
    Then I receive a status code "400" with body
      | path             | value                                                                                                                             |
      | errors.0.code    | VALIDATION_ERROR                                                                                                                  |
      | errors.0.message | This product already has a 'Message Sets' DeviceReferenceData. Please update, or delete and recreate if you wish to make changes. |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 186              |

  Scenario: Fail to create an "MHS Message Set" Device Reference Data in non-EPR product
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/MhsMessageSet"
    Then I receive a status code "400" with body
      | path             | value                                                                                  |
      | errors.0.code    | VALIDATION_ERROR                                                                       |
      | errors.0.message | Not an EPR Product: Cannot create MHS Device for product without exactly one Party Key |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 143              |

  Scenario: Fail to create an "MHS Message Set" Device Reference Data, with questionnaire responses with duplicate interaction IDs
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
      | path                                                    | value                          |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS SN | urn:nhs:names:services:ers     |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS IN | READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_mhs_message_sets.1.MHS SN | urn:nhs:names:services:ers     |
      | questionnaire_responses.spine_mhs_message_sets.1.MHS IN | READ_PRACTITIONER_ROLE_R4_V001 |
    Then I receive a status code "400" with body
      | path             | value                                                                                                                                                |
      | errors.0.code    | VALIDATION_ERROR                                                                                                                                     |
      | errors.0.message | Duplicate 'Interaction ID' provided: value 'urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001' occurs 2 times in the questionnaire response. |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 205              |
