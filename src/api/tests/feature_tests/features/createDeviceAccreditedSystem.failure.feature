Feature: Create AS Device - failure scenarios
  These scenarios demonstrate failures to create a new AS Device

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Cannot create a AS Device with a Device body that is missing fields (no questionnaire_responses) and has extra param
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/AccreditedSystem" with body:
      | path      | value        |
      | bad_field | Not required |
    Then I receive a status code "400" with body
      | path             | value                                                                |
      | errors.0.code    | MISSING_VALUE                                                        |
      | errors.0.message | CreateAsDeviceIncomingParams.questionnaire_responses: field required |
      | errors.1.code    | VALIDATION_ERROR                                                     |
      | errors.1.message | CreateAsDeviceIncomingParams.bad_field: extra fields not permitted   |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 233              |

  Scenario: Cannot create a AS Device with a corrupt Device body
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/AccreditedSystem" with body:
      """
      {"invalid_array": [}
      """
    Then I receive a status code "400" with body
      | path             | value                                                      |
      | errors.0.code    | VALIDATION_ERROR                                           |
      | errors.0.message | Invalid JSON body was provided: line 1 column 20 (char 19) |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 115              |

  Scenario: Cannot create a AS Device with a Product Team that does not exist
    When I make a "POST" request with "default" headers to "ProductTeamEpr/not-a-product-team/Product/not-a-product/dev/Device/AccreditedSystem" with body:
      | path                    | value |
      | questionnaire_responses | {}    |
    Then I receive a status code "404" with body
      | path             | value                                                     |
      | errors.0.code    | RESOURCE_NOT_FOUND                                        |
      | errors.0.message | Could not find ProductTeam for key ('not-a-product-team') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 116              |

  Scenario: Cannot create a AS Device with a Product that does not exist
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/not-a-product/dev/Device/AccreditedSystem" with body:
      | path                    | value |
      | questionnaire_responses | {}    |
    Then I receive a status code "404" with body
      | path             | value                                                                             |
      | errors.0.code    | RESOURCE_NOT_FOUND                                                                |
      | errors.0.message | Could not find CpmProduct for key ('${ note(product_team_id) }', 'not-a-product') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 156              |

  Scenario: Cannot create a AS Device with a Product that does not have a party key
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/AccreditedSystem" with body:
      | path                    | value |
      | questionnaire_responses | {}    |
    Then I receive a status code "400" with body
      | path             | value                                                                                 |
      | errors.0.code    | VALIDATION_ERROR                                                                      |
      | errors.0.message | Not an EPR Product: Cannot create AS device for product without exactly one Party Key |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 142              |

  Scenario: Cannot create a AS Device for a Product that does not have a Any Device Reference Data
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/AccreditedSystem" with body:
      | path                                                  | value           |
      | questionnaire_responses.spine_as.0.ODS Code           | FH15R           |
      | questionnaire_responses.spine_as.0.Client ODS Codes.0 | FH15R           |
      | questionnaire_responses.spine_as.0.ASID               | Foobar          |
      | questionnaire_responses.spine_as.0.Party Key          | P.123-XXX       |
      | questionnaire_responses.spine_as.0.Approver URP       | approver-123    |
      | questionnaire_responses.spine_as.0.Date Approved      | 2024-01-01      |
      | questionnaire_responses.spine_as.0.Requestor URP      | requestor-789   |
      | questionnaire_responses.spine_as.0.Date Requested     | 2024-01-03      |
      | questionnaire_responses.spine_as.0.Product Key        | product-key-001 |
    Then I receive a status code "400" with body
      | path             | value                                                                                       |
      | errors.0.code    | VALIDATION_ERROR                                                                            |
      | errors.0.message | You must configure the AS and MessageSet Device Reference Data before creating an AS Device |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 148              |

  Scenario: Cannot create a AS Device for a Product that does not have a an AS Device Reference Data
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/MhsMessageSet" with body:
      | path                                                    | value                          |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS SN | urn:nhs:names:services:ers     |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS IN | READ_PRACTITIONER_ROLE_R4_V001 |
    And I note the response field "$.id" as "mhs_message_set_drd_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/AccreditedSystem" with body:
      | path                                                  | value           |
      | questionnaire_responses.spine_as.0.ODS Code           | FH15R           |
      | questionnaire_responses.spine_as.0.Client ODS Codes.0 | FH15R           |
      | questionnaire_responses.spine_as.0.ASID               | Foobar          |
      | questionnaire_responses.spine_as.0.Party Key          | P.123-XXX       |
      | questionnaire_responses.spine_as.0.Approver URP       | approver-123    |
      | questionnaire_responses.spine_as.0.Date Approved      | 2024-01-01      |
      | questionnaire_responses.spine_as.0.Requestor URP      | requestor-789   |
      | questionnaire_responses.spine_as.0.Date Requested     | 2024-01-03      |
      | questionnaire_responses.spine_as.0.Product Key        | product-key-001 |
    Then I receive a status code "400" with body
      | path             | value                                                                                       |
      | errors.0.code    | VALIDATION_ERROR                                                                            |
      | errors.0.message | You must configure the AS and MessageSet Device Reference Data before creating an AS Device |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 148              |

  Scenario: Cannot create a AS Device for a Product that does not have a an MHS Device Reference Data
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/AccreditedSystemsAdditionalInteractions" with body:
      | path                                                                      | value                                                     |
      | questionnaire_responses.spine_as_additional_interactions.0.Interaction ID | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V002 |
    And I note the response field "$.id" as "as_message_set_drd_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/AccreditedSystem" with body:
      | path                                                  | value           |
      | questionnaire_responses.spine_as.0.ODS Code           | FH15R           |
      | questionnaire_responses.spine_as.0.Client ODS Codes.0 | FH15R           |
      | questionnaire_responses.spine_as.0.ASID               | Foobar          |
      | questionnaire_responses.spine_as.0.Party Key          | P.123-XXX       |
      | questionnaire_responses.spine_as.0.Approver URP       | approver-123    |
      | questionnaire_responses.spine_as.0.Date Approved      | 2024-01-01      |
      | questionnaire_responses.spine_as.0.Requestor URP      | requestor-789   |
      | questionnaire_responses.spine_as.0.Date Requested     | 2024-01-03      |
      | questionnaire_responses.spine_as.0.Product Key        | product-key-001 |
    Then I receive a status code "400" with body
      | path             | value                                                                                       |
      | errors.0.code    | VALIDATION_ERROR                                                                            |
      | errors.0.message | You must configure the AS and MessageSet Device Reference Data before creating an AS Device |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 148              |

  Scenario: Cannot create a AS Device with a Device body that has no questionnaire responses for 'spine_as'
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/MhsMessageSet"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/AccreditedSystem" with body:
      | path                                            | value  |
      | questionnaire_responses.not_spine_as.0.Question | Answer |
    Then I receive a status code "400" with body
      | path             | value                                                                                                                                   |
      | errors.0.code    | VALIDATION_ERROR                                                                                                                        |
      | errors.0.message | CreateAsDeviceIncomingParams.questionnaire_responses.__key__: unexpected value; permitted: <QuestionnaireInstance.SPINE_AS: 'spine_as'> |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 192              |

  Scenario: Cannot create a AS Device with a Device body that has multiple questionnaire responses for 'spine_as'
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/MhsMessageSet" with body:
      | path                                                    | value                          |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS SN | urn:nhs:names:services:ers     |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS IN | READ_PRACTITIONER_ROLE_R4_V001 |
    And I note the response field "$.id" as "mhs_message_set_drd_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/AccreditedSystemsAdditionalInteractions" with body:
      | path                                                                      | value                                                     |
      | questionnaire_responses.spine_as_additional_interactions.0.Interaction ID | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V002 |
    And I note the response field "$.id" as "as_message_set_drd_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/AccreditedSystem" with body:
      | path                                                  | value           |
      | questionnaire_responses.spine_as.0.ODS Code           | FH15R           |
      | questionnaire_responses.spine_as.0.Client ODS Codes.0 | FH15R           |
      | questionnaire_responses.spine_as.0.ASID               | Foobar          |
      | questionnaire_responses.spine_as.0.Party Key          | P.123-XXX       |
      | questionnaire_responses.spine_as.0.Approver URP       | approver-123    |
      | questionnaire_responses.spine_as.0.Date Approved      | 2024-01-01      |
      | questionnaire_responses.spine_as.0.Requestor URP      | requestor-789   |
      | questionnaire_responses.spine_as.0.Date Requested     | 2024-01-03      |
      | questionnaire_responses.spine_as.0.Product Key        | product-key-001 |
      | questionnaire_responses.spine_as.1.ODS Code           | FH15R           |
      | questionnaire_responses.spine_as.1.Client ODS Codes.0 | FH15R           |
      | questionnaire_responses.spine_as.1.ASID               | Foobar          |
      | questionnaire_responses.spine_as.1.Party Key          | P.123-XXX       |
      | questionnaire_responses.spine_as.1.Approver URP       | approver-123    |
      | questionnaire_responses.spine_as.1.Date Approved      | 2024-01-01      |
      | questionnaire_responses.spine_as.1.Requestor URP      | requestor-789   |
      | questionnaire_responses.spine_as.1.Date Requested     | 2024-01-03      |
      | questionnaire_responses.spine_as.1.Product Key        | product-key-001 |
    Then I receive a status code "400" with body
      | path             | value                                                                                                         |
      | errors.0.code    | VALIDATION_ERROR                                                                                              |
      | errors.0.message | CreateAsDeviceIncomingParams.questionnaire_responses.spine_as.__root__: ensure this value has at most 1 items |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 166              |

  Scenario: Cannot create a AS Device with a Device body that has an invalid questionnaire responses for the questionnaire 'spine_as'
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/MhsMessageSet" with body:
      | path                                                    | value                          |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS SN | urn:nhs:names:services:ers     |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS IN | READ_PRACTITIONER_ROLE_R4_V001 |
    And I note the response field "$.id" as "mhs_message_set_drd_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/AccreditedSystemsAdditionalInteractions" with body:
      | path                                                                      | value                                                     |
      | questionnaire_responses.spine_as_additional_interactions.0.Interaction ID | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V002 |
    And I note the response field "$.id" as "as_message_set_drd_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/AccreditedSystem" with body:
      | path                                               | value             |
      | questionnaire_responses.spine_as.0.ODS Code        | F5H1R             |
      | questionnaire_responses.spine_as.0.Product Name    | My SPINE Product  |
      | questionnaire_responses.spine_as.0.Product Version | 2000.01           |
      | questionnaire_responses.spine_as.0.Requestor URP   | the-requestor-urp |
    Then I receive a status code "400" with body
      | path             | value                                                                               |
      | errors.0.code    | MISSING_VALUE                                                                       |
      | errors.0.message | Failed to validate data against 'spine_as/1': 'Approver URP' is a required property |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 137              |
