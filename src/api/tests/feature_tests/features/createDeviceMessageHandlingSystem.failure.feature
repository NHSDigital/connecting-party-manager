Feature: Create MHS Device - failure scenarios
  These scenarios demonstrate failures to create a new MHS Device

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Cannot create a MHS Device with a body that is missing fields (no questionnaire_responses) and has extra param
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/MessageHandlingSystem" with body:
      | path      | value        |
      | bad_field | Not required |
    Then I receive a status code "400" with body
      | path             | value                                                                 |
      | errors.0.code    | MISSING_VALUE                                                         |
      | errors.0.message | CreateMhsDeviceIncomingParams.questionnaire_responses: field required |
      | errors.1.code    | VALIDATION_ERROR                                                      |
      | errors.1.message | CreateMhsDeviceIncomingParams.bad_field: extra fields not permitted   |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 235              |

  Scenario: Cannot create a MHS Device with a corrupt Device body
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/MessageHandlingSystem" with body:
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

  Scenario: Cannot create a MHS Device with a Product Team that does not exist
    When I make a "POST" request with "default" headers to "ProductTeamEpr/not-a-product-team/Product/not-a-product/dev/Device/MessageHandlingSystem" with body:
      | path                                                              | value               |
      | questionnaire_responses.spine_mhs.0.MHS FQDN                      | mhs.example.com     |
      | questionnaire_responses.spine_mhs.0.MHS Service Description       | Example Description |
      | questionnaire_responses.spine_mhs.0.MHS Manufacturer Organisation | F5H1R               |
      | questionnaire_responses.spine_mhs.0.Product Name                  | Product Name        |
      | questionnaire_responses.spine_mhs.0.Product Version               | 1                   |
      | questionnaire_responses.spine_mhs.0.Approver URP                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.DNS Approver                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.Requestor URP                 | UI provided         |
    Then I receive a status code "404" with body
      | path             | value                                                     |
      | errors.0.code    | RESOURCE_NOT_FOUND                                        |
      | errors.0.message | Could not find ProductTeam for key ('not-a-product-team') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 116              |

  Scenario: Cannot create a MHS Device with a Product that does not exist
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/not-a-product/dev/Device/MessageHandlingSystem" with body:
      | path                                                              | value               |
      | questionnaire_responses.spine_mhs.0.MHS FQDN                      | mhs.example.com     |
      | questionnaire_responses.spine_mhs.0.MHS Service Description       | Example Description |
      | questionnaire_responses.spine_mhs.0.MHS Manufacturer Organisation | F5H1R               |
      | questionnaire_responses.spine_mhs.0.Product Name                  | Product Name        |
      | questionnaire_responses.spine_mhs.0.Product Version               | 1                   |
      | questionnaire_responses.spine_mhs.0.Approver URP                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.DNS Approver                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.Requestor URP                 | UI provided         |
    Then I receive a status code "404" with body
      | path             | value                                                                             |
      | errors.0.code    | RESOURCE_NOT_FOUND                                                                |
      | errors.0.message | Could not find CpmProduct for key ('${ note(product_team_id) }', 'not-a-product') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 156              |

  Scenario: Cannot create a MHS Device with a Product that does not have a party key
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/MessageHandlingSystem" with body:
      | path                                                              | value               |
      | questionnaire_responses.spine_mhs.0.MHS FQDN                      | mhs.example.com     |
      | questionnaire_responses.spine_mhs.0.MHS Service Description       | Example Description |
      | questionnaire_responses.spine_mhs.0.MHS Manufacturer Organisation | F5H1R               |
      | questionnaire_responses.spine_mhs.0.Product Name                  | Product Name        |
      | questionnaire_responses.spine_mhs.0.Product Version               | 1                   |
      | questionnaire_responses.spine_mhs.0.Approver URP                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.DNS Approver                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.Requestor URP                 | UI provided         |
    Then I receive a status code "400" with body
      | path             | value                                                                                  |
      | errors.0.code    | VALIDATION_ERROR                                                                       |
      | errors.0.message | Not an EPR Product: Cannot create MHS Device for product without exactly one Party Key |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 143              |

  Scenario: Cannot create a MHS Device for a Product that does not have a MessageSet Device Reference Data
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/MessageHandlingSystem" with body:
      | path                                                              | value               |
      | questionnaire_responses.spine_mhs.0.MHS FQDN                      | mhs.example.com     |
      | questionnaire_responses.spine_mhs.0.MHS Service Description       | Example Description |
      | questionnaire_responses.spine_mhs.0.MHS Manufacturer Organisation | F5H1R               |
      | questionnaire_responses.spine_mhs.0.Product Name                  | Product Name        |
      | questionnaire_responses.spine_mhs.0.Product Version               | 1                   |
      | questionnaire_responses.spine_mhs.0.Approver URP                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.DNS Approver                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.Requestor URP                 | UI provided         |
    Then I receive a status code "400" with body
      | path             | value                                                                                          |
      | errors.0.code    | VALIDATION_ERROR                                                                               |
      | errors.0.message | You must configure exactly one MessageSet Device Reference Data before creating an MHS Device. |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 151              |

  Scenario: Cannot create a MHS Device with a Device body that has answered a questionnaire that isn't 'spine_mhs'
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
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/MessageHandlingSystem" with body:
      | path                                             | value  |
      | questionnaire_responses.not_spine_mhs.0.Question | Answer |
    Then I receive a status code "400" with body
      | path             | value                                                                                                                                      |
      | errors.0.code    | VALIDATION_ERROR                                                                                                                           |
      | errors.0.message | CreateMhsDeviceIncomingParams.questionnaire_responses.__key__: unexpected value; permitted: <QuestionnaireInstance.SPINE_MHS: 'spine_mhs'> |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 195              |

  Scenario: Cannot create a MHS Device with a Device body that hasn't answered the questionnaire 'spine_mhs'
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
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/MessageHandlingSystem"
    Then I receive a status code "400" with body
      | path             | value                                                                 |
      | errors.0.code    | MISSING_VALUE                                                         |
      | errors.0.message | CreateMhsDeviceIncomingParams.questionnaire_responses: field required |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 123              |

  Scenario: Cannot create a MHS Device with a Device body that has multiple questionnaire responses for 'spine_mhs'
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
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/MessageHandlingSystem" with body:
      | path                                                              | value               |
      | questionnaire_responses.spine_mhs.0.MHS FQDN                      | mhs.example.com     |
      | questionnaire_responses.spine_mhs.0.MHS Service Description       | Example Description |
      | questionnaire_responses.spine_mhs.0.MHS Manufacturer Organisation | F5H1R               |
      | questionnaire_responses.spine_mhs.0.Product Name                  | Product Name        |
      | questionnaire_responses.spine_mhs.0.Product Version               | 1                   |
      | questionnaire_responses.spine_mhs.0.Approver URP                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.DNS Approver                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.Requestor URP                 | UI provided         |
      | questionnaire_responses.spine_mhs.1.MHS FQDN                      | mhs.example.com     |
      | questionnaire_responses.spine_mhs.1.MHS Service Description       | Example Description |
      | questionnaire_responses.spine_mhs.1.MHS Manufacturer Organisation | F5H1R               |
      | questionnaire_responses.spine_mhs.1.Product Name                  | Product Name        |
      | questionnaire_responses.spine_mhs.1.Product Version               | 1                   |
      | questionnaire_responses.spine_mhs.1.Approver URP                  | UI provided         |
      | questionnaire_responses.spine_mhs.1.DNS Approver                  | UI provided         |
      | questionnaire_responses.spine_mhs.1.Requestor URP                 | UI provided         |
    Then I receive a status code "400" with body
      | path             | value                                                                                  |
      | errors.0.code    | VALIDATION_ERROR                                                                       |
      | errors.0.message | You must provide exactly one spine_mhs questionnaire response to create an MHS Device. |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 143              |

  Scenario: Cannot create a MHS Device with a Device body that has an invalid questionnaire responses for the questionnaire 'spine_mhs'
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
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/MessageHandlingSystem" with body:
      | path                                         | value  |
      | questionnaire_responses.spine_mhs.0.MHS FQDN | 123456 |
    Then I receive a status code "400" with body
      | path             | value                                                                                                 |
      | errors.0.code    | MISSING_VALUE                                                                                         |
      | errors.0.message | Failed to validate data against 'spine_mhs/1': 'MHS Manufacturer Organisation' is a required property |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 155              |

  Scenario: Cannot create a MHS Device with a Device body that has answered system generated questions for the questionnaire 'spine_mhs'
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
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/MessageHandlingSystem" with body:
      | path                                                              | value               |
      | questionnaire_responses.spine_mhs.0.MHS FQDN                      | mhs.example.com     |
      | questionnaire_responses.spine_mhs.0.MHS Service Description       | Example Description |
      | questionnaire_responses.spine_mhs.0.MHS Manufacturer Organisation | F5H1R               |
      | questionnaire_responses.spine_mhs.0.Product Name                  | Product Name        |
      | questionnaire_responses.spine_mhs.0.Product Version               | 1                   |
      | questionnaire_responses.spine_mhs.0.Approver URP                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.DNS Approver                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.Requestor URP                 | UI provided         |
      | questionnaire_responses.spine_mhs.0.Address                       | http://example.com  |
    Then I receive a status code "400" with body
      | path             | value                                                                                                                                                                                                                               |
      | errors.0.code    | VALIDATION_ERROR                                                                                                                                                                                                                    |
      | errors.0.message | Payload contains unexpected fields: {'Address'}. Expected fields are: ['Approver URP', 'DNS Approver', 'MHS FQDN', 'MHS Manufacturer Organisation', 'MHS Service Description', 'Product Name', 'Product Version', 'Requestor URP']. |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 284              |

  Scenario: Cannot create a MHS Device with a Device body that has not answered fields requried for the system generated fields
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
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/MessageHandlingSystem" with body:
      | path                                                        | value               |
      | questionnaire_responses.spine_mhs.0.MHS Service Description | Example Description |
    Then I receive a status code "400" with body
      | path             | value                                                                            |
      | errors.0.code    | VALIDATION_ERROR                                                                 |
      | errors.0.message | The following required fields are missing in the response to spine_mhs: MHS FQDN |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 137              |

  Scenario: Cannot create a MHS Device with a Product that already has an MHS Device
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
      | path                                                                                        | value                          |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS SN                                     | urn:nhs:names:services:ers     |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS IN                                     | READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_mhs_message_sets.1.MHS SN                                     | urn:nhs:names:services:ebs     |
      | questionnaire_responses.spine_mhs_message_sets.1.MHS IN                                     | PRSC_IN080000UK07              |
      | questionnaire_responses.spine_mhs_message_sets.1.Reliability Configuration Retry Interval   | PT1M                           |
      | questionnaire_responses.spine_mhs_message_sets.1.Reliability Configuration Retries          | ${ integer(2) }                |
      | questionnaire_responses.spine_mhs_message_sets.1.Reliability Configuration Persist Duration | PT10M                          |
    And I note the response field "$.id" as "message_set_drd_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/MessageHandlingSystem" with body:
      | path                                                              | value               |
      | questionnaire_responses.spine_mhs.0.MHS FQDN                      | mhs.example.com     |
      | questionnaire_responses.spine_mhs.0.MHS Service Description       | Example Description |
      | questionnaire_responses.spine_mhs.0.MHS Manufacturer Organisation | F5H1R               |
      | questionnaire_responses.spine_mhs.0.Product Name                  | Product Name        |
      | questionnaire_responses.spine_mhs.0.Product Version               | 1                   |
      | questionnaire_responses.spine_mhs.0.Approver URP                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.DNS Approver                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.Requestor URP                 | UI provided         |
    And I note the response field "$.id" as "device_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/MessageHandlingSystem" with body:
      | path                                                              | value               |
      | questionnaire_responses.spine_mhs.0.MHS FQDN                      | mhs.example.com     |
      | questionnaire_responses.spine_mhs.0.MHS Service Description       | Example Description |
      | questionnaire_responses.spine_mhs.0.MHS Manufacturer Organisation | F5H1R               |
      | questionnaire_responses.spine_mhs.0.Product Name                  | Product Name        |
      | questionnaire_responses.spine_mhs.0.Product Version               | 1                   |
      | questionnaire_responses.spine_mhs.0.Approver URP                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.DNS Approver                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.Requestor URP                 | UI provided         |
    Then I receive a status code "400" with body
      | path             | value                                                    |
      | errors.0.code    | VALIDATION_ERROR                                         |
      | errors.0.message | There is already an existing MHS Device for this Product |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 113              |

  Scenario: Cannot create a MHS Device with a Product that already has an MHS Device with no Mhs Message Set questionnaire responses
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
    And I note the response field "$.id" as "message_set_drd_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/MessageHandlingSystem" with body:
      | path                                                              | value               |
      | questionnaire_responses.spine_mhs.0.MHS FQDN                      | mhs.example.com     |
      | questionnaire_responses.spine_mhs.0.MHS Service Description       | Example Description |
      | questionnaire_responses.spine_mhs.0.MHS Manufacturer Organisation | F5H1R               |
      | questionnaire_responses.spine_mhs.0.Product Name                  | Product Name        |
      | questionnaire_responses.spine_mhs.0.Product Version               | 1                   |
      | questionnaire_responses.spine_mhs.0.Approver URP                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.DNS Approver                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.Requestor URP                 | UI provided         |
    And I note the response field "$.id" as "device_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/MessageHandlingSystem" with body:
      | path                                                              | value               |
      | questionnaire_responses.spine_mhs.0.MHS FQDN                      | mhs.example.com     |
      | questionnaire_responses.spine_mhs.0.MHS Service Description       | Example Description |
      | questionnaire_responses.spine_mhs.0.MHS Manufacturer Organisation | F5H1R               |
      | questionnaire_responses.spine_mhs.0.Product Name                  | Product Name        |
      | questionnaire_responses.spine_mhs.0.Product Version               | 1                   |
      | questionnaire_responses.spine_mhs.0.Approver URP                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.DNS Approver                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.Requestor URP                 | UI provided         |
    Then I receive a status code "400" with body
      | path             | value                                                    |
      | errors.0.code    | VALIDATION_ERROR                                         |
      | errors.0.message | There is already an existing MHS Device for this Product |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 113              |
