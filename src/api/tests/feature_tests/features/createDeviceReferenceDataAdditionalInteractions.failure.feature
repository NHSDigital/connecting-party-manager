Feature: Create "Additional Interactions" Device Reference Data - failure scenarios
  These scenarios demonstrate unsuccessful "Additional Interactions" Device Reference Data creation

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Fail to create an "AS Additional Interactions" Device Reference Data, with incomplete questionnaire response
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/AccreditedSystemsAdditionalInteractions" with body:
      | path                                                       | value |
      | questionnaire_responses.spine_as_additional_interactions.0 | {}    |
    Then I receive a status code "400" with body
      | path             | value                                                                                                         |
      | errors.0.code    | MISSING_VALUE                                                                                                 |
      | errors.0.message | Failed to validate data against 'spine_as_additional_interactions/1': 'Interaction ID' is a required property |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 163              |

  Scenario: Fail to create an "AS Additional Interactions" Device Reference Data, with invalid questionnaire response (bad value)
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/AccreditedSystemsAdditionalInteractions" with body:
      | path                                                                      | value |
      | questionnaire_responses.spine_as_additional_interactions.0.Interaction ID | []    |
    Then I receive a status code "400" with body
      | path             | value                                                                                            |
      | errors.0.code    | VALIDATION_ERROR                                                                                 |
      | errors.0.message | Failed to validate data against 'spine_as_additional_interactions/1': [] is not of type 'string' |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 153              |

  Scenario: Fail to create an "AS Additional Interactions" Device Reference Data, with invalid questionnaire response (unknown field)
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/AccreditedSystemsAdditionalInteractions" with body:
      | path                                                                      | value                                                     |
      | questionnaire_responses.spine_as_additional_interactions.0.Interaction ID | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_as_additional_interactions.0.unknown_field  | 123                                                       |
    Then I receive a status code "400" with body
      | path             | value                                                                                                                                        |
      | errors.0.code    | VALIDATION_ERROR                                                                                                                             |
      | errors.0.message | Failed to validate data against 'spine_as_additional_interactions/1': Additional properties are not allowed ('unknown_field' was unexpected) |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 197              |

  Scenario: Fail to create an "AS Additional Interactions" Device Reference Data, with invalid questionnaire name
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/AccreditedSystemsAdditionalInteractions" with body:
      | path                                                        | value |
      | questionnaire_responses.bad_questionnaire_name.0.some_value | 123   |
    Then I receive a status code "400" with body
      | path             | value                                                                                                                                                                                                            |
      | errors.0.code    | VALIDATION_ERROR                                                                                                                                                                                                 |
      | errors.0.message | CreateDeviceReferenceAdditionalInteractionsDataParams.questionnaire_responses.__key__: unexpected value; permitted: <QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS: 'spine_as_additional_interactions'> |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 265              |

  Scenario: Fail to create a second "AS Additional Interactions" Device Reference Data in the same EPR Product
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I note the response field "$.keys.0.key_value" as "party_key"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/AccreditedSystemsAdditionalInteractions"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/AccreditedSystemsAdditionalInteractions"
    Then I receive a status code "400" with body
      | path             | value                                                                         |
      | errors.0.code    | VALIDATION_ERROR                                                              |
      | errors.0.message | Additional Interactions Device Reference Data already exists for this Product |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 134              |

  Scenario: Fail to create an "AS Additional Interactions" Device Reference Data in non-EPR product
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/AccreditedSystemsAdditionalInteractions"
    Then I receive a status code "400" with body
      | path             | value                                                                                              |
      | errors.0.code    | VALIDATION_ERROR                                                                                   |
      | errors.0.message | Not an EPR Product: Cannot create Additional Interactions in Product without exactly one Party Key |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 155              |

  Scenario: Failure to create an "AS Additional Interactions" Device Reference Data, with questionnaire responses with duplicate interaction IDs
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I note the response field "$.keys.0.key_value" as "party_key"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/AccreditedSystemsAdditionalInteractions" with body:
      | path                                                                      | value                                                     |
      | questionnaire_responses.spine_as_additional_interactions.0.Interaction ID | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_as_additional_interactions.1.Interaction ID | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
    Then I receive a status code "400" with body
      | path             | value                                                                                                                                                |
      | errors.0.code    | VALIDATION_ERROR                                                                                                                                     |
      | errors.0.message | Duplicate 'Interaction ID' provided: value 'urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001' occurs 2 times in the questionnaire response. |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 205              |
