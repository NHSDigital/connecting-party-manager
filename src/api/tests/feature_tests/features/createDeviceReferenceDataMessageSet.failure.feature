Feature: Create "Message Set" Device Reference Data - failure scenarios
  These scenarios demonstrate failure to create "Message Set" Device Reference Data

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Fail to create an "MHS Message Set" Device Reference Data, with incomplete questionnaire response
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path         | value            |
      | product_name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/MhsMessageSet" with body:
      | path                                                            | value                                                     |
      | questionnaire_responses.spine_mhs_message_sets.0.Interaction ID | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
    Then I receive a status code "400" with body
      | path             | value                                                                                       |
      | errors.0.code    | MISSING_VALUE                                                                               |
      | errors.0.message | Failed to validate data against 'spine_mhs_message_sets/1': 'MHS IN' is a required property |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 145              |

  Scenario: Fail to create an "MHS Message Set" Device Reference Data, with invalid questionnaire response (bad value)
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path         | value            |
      | product_name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/MhsMessageSet" with body:
      | path                                                                               | value                                                     |
      | questionnaire_responses.spine_mhs_message_sets.0.Interaction ID                    | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS SN                            | urn:nhs:names:services:ers                                |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS IN                            | READ_PRACTITIONER_ROLE_R4_V001                            |
      | questionnaire_responses.spine_mhs_message_sets.0.Reliability Configuration Retries | two                                                       |
    Then I receive a status code "400" with body
      | path             | value                                                                                      |
      | errors.0.code    | VALIDATION_ERROR                                                                           |
      | errors.0.message | Failed to validate data against 'spine_mhs_message_sets/1': 'two' is not of type 'integer' |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 147              |

  Scenario: Fail to create an "MHS Message Set" Device Reference Data, with invalid questionnaire response (unknown field)
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path         | value            |
      | product_name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/MhsMessageSet" with body:
      | path                                                            | value                                                     |
      | questionnaire_responses.spine_mhs_message_sets.0.Interaction ID | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS SN         | urn:nhs:names:services:ers                                |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS IN         | READ_PRACTITIONER_ROLE_R4_V001                            |
      | questionnaire_responses.spine_mhs_message_sets.0.unknown_field  | 123                                                       |
    Then I receive a status code "400" with body
      | path             | value                                                                                                                              |
      | errors.0.code    | VALIDATION_ERROR                                                                                                                   |
      | errors.0.message | Failed to validate data against 'spine_mhs_message_sets/1': Additional properties are not allowed ('unknown_field' was unexpected) |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 187              |

  Scenario: Fail to create an "MHS Message Set" Device Reference Data, with invalid questionnaire name
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path         | value            |
      | product_name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/MhsMessageSet" with body:
      | path                                                        | value |
      | questionnaire_responses.bad_questionnaire_name.0.some_value | 123   |
    Then I receive a status code "400" with body
      | path             | value                                                                                                                             |
      | errors.0.code    | VALIDATION_ERROR                                                                                                                  |
      | errors.0.message | CreateDeviceReferenceMessageSetsDataParams.questionnaire_responses.__key__: unexpected value; permitted: 'spine_mhs_message_sets' |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 186              |

  Scenario: Fail to create a second "MHS Message Set" Device Reference Data in the same EPR Product
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
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/MhsMessageSet"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/MhsMessageSet"
    Then I receive a status code "400" with body
      | path             | value                                                                                                                            |
      | errors.0.code    | VALIDATION_ERROR                                                                                                                 |
      | errors.0.message | This product already has a 'Message Set' DeviceReferenceData. Please update, or delete and recreate if you wish to make changes. |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 185              |

  Scenario: Fail to create an "MHS Message Set" Device Reference Data in non-EPR product
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path         | value            |
      | product_name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/MhsMessageSet"
    Then I receive a status code "400" with body
      | path             | value                                                              |
      | errors.0.code    | VALIDATION_ERROR                                                   |
      | errors.0.message | Cannot create Message Set in Product without exactly one Party Key |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 123              |