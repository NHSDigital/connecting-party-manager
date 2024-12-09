Feature: Create MHS Device - failure scenarios
  These scenarios demonstrate failures to create a new MHS Device

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Cannot create a MHS Device with a body that is missing fields (no questionnaire_responses) and has extra param
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/Device/MessageHandlingSystem" with body:
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
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/Device/MessageHandlingSystem" with body:
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
    When I make a "POST" request with "default" headers to "ProductTeam/not-a-product-team/Product/not-a-product/Device/MessageHandlingSystem" with body:
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

  Scenario: Cannot create a MHS Device with a Product that does not exist
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/not-a-product/Device/MessageHandlingSystem" with body:
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

  Scenario: Cannot create a MHS Device with a Product that does not have a party key
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/Device/MessageHandlingSystem" with body:
      | path                    | value |
      | questionnaire_responses | {}    |
    Then I receive a status code "400" with body
      | path             | value                                                                                  |
      | errors.0.code    | VALIDATION_ERROR                                                                       |
      | errors.0.message | Not an EPR Product: Cannot create MHS Device for product without exactly one Party Key |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 143              |

  Scenario: Cannot create a MHS Device for a Product that does not have a MessageSet Device Reference Data
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/Device/MessageHandlingSystem" with body:
      | path                                                               | value              |
      | questionnaire_responses.spine_mhs.0.Address                        | http://example.com |
      | questionnaire_responses.spine_mhs.0.Unique Identifier              | 123456             |
      | questionnaire_responses.spine_mhs.0.Managing Organization          | Example Org        |
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
    Then I receive a status code "400" with body
      | path             | value                                                                                         |
      | errors.0.code    | VALIDATION_ERROR                                                                              |
      | errors.0.message | You must configure exactly one MessageSet Device Reference Data before creating an MHS Device |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 150              |

  Scenario: Cannot create a MHS Device with a Device body that has no questionnaire responses for 'spine_mhs'
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/MhsMessageSet"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/Device/MessageHandlingSystem" with body:
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

  Scenario: Cannot create a MHS Device with a Device body that has multiple questionnaire responses for 'spine_mhs'
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/MhsMessageSet"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/Device/MessageHandlingSystem" with body:
      | path                                                               | value              |
      | questionnaire_responses.spine_mhs.0.Address                        | http://example.com |
      | questionnaire_responses.spine_mhs.0.Unique Identifier              | 123456             |
      | questionnaire_responses.spine_mhs.0.Managing Organization          | Example Org        |
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
      | questionnaire_responses.spine_mhs.1.Address                        | http://example.com |
      | questionnaire_responses.spine_mhs.1.Unique Identifier              | 123456             |
      | questionnaire_responses.spine_mhs.1.Managing Organization          | Example Org        |
      | questionnaire_responses.spine_mhs.1.MHS Party key                  | party-key-001      |
      | questionnaire_responses.spine_mhs.1.MHS CPA ID                     | cpa-id-001         |
      | questionnaire_responses.spine_mhs.1.Approver URP                   | approver-123       |
      | questionnaire_responses.spine_mhs.1.Contract Property Template Key | contract-key-001   |
      | questionnaire_responses.spine_mhs.1.Date Approved                  | 2024-01-01         |
      | questionnaire_responses.spine_mhs.1.Date DNS Approved              | 2024-01-02         |
      | questionnaire_responses.spine_mhs.1.Date Requested                 | 2024-01-03         |
      | questionnaire_responses.spine_mhs.1.DNS Approver                   | dns-approver-456   |
      | questionnaire_responses.spine_mhs.1.Interaction Type               | FHIR               |
      | questionnaire_responses.spine_mhs.1.MHS FQDN                       | mhs.example.com    |
      | questionnaire_responses.spine_mhs.1.MHS Is Authenticated           | PERSISTENT         |
      | questionnaire_responses.spine_mhs.1.Product Key                    | product-key-001    |
      | questionnaire_responses.spine_mhs.1.Requestor URP                  | requestor-789      |
    Then I receive a status code "400" with body
      | path             | value                                                                                                           |
      | errors.0.code    | VALIDATION_ERROR                                                                                                |
      | errors.0.message | CreateMhsDeviceIncomingParams.questionnaire_responses.spine_mhs.__root__: ensure this value has at most 1 items |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 168              |

  Scenario: Cannot create a MHS Device with a Device body that has an invalid questionnaire responses for the questionnaire 'spine_mhs'
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/MhsMessageSet"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/Device/MessageHandlingSystem" with body:
      | path                                                  | value              |
      | questionnaire_responses.spine_mhs.0.Address           | http://example.com |
      | questionnaire_responses.spine_mhs.0.Unique Identifier | 123456             |
    Then I receive a status code "400" with body
      | path             | value                                                                                                 |
      | errors.0.code    | MISSING_VALUE                                                                                         |
      | errors.0.message | Failed to validate data against 'spine_mhs/1': 'MHS Manufacturer Organisation' is a required property |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 155              |

  Scenario: Cannot create a MHS Device with a Product that already has an MHS Device
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/MhsMessageSet" with body:
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
    And I note the response field "$.id" as "message_set_drd_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/Device/MessageHandlingSystem" with body:
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
    And I note the response field "$.id" as "device_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/Device/MessageHandlingSystem" with body:
      | path                                                               | value              |
      | questionnaire_responses.spine_mhs.0.Address                        | http://example.com |
      | questionnaire_responses.spine_mhs.0.Unique Identifier              | 123457             |
      | questionnaire_responses.spine_mhs.0.Managing Organization          | Example Org        |
      | questionnaire_responses.spine_mhs.0.MHS Manufacturer Organisation  | AAA                |
      | questionnaire_responses.spine_mhs.0.MHS Party key                  | party-key-003      |
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
    Then I receive a status code "400" with body
      | path             | value                                                    |
      | errors.0.code    | VALIDATION_ERROR                                         |
      | errors.0.message | There is already an existing MHS Device for this Product |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 113              |

  Scenario: Cannot create a MHS Device with a Product that already has an MHS Device with no questionnaire responses
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/DeviceReferenceData/MhsMessageSet"
    And I note the response field "$.id" as "message_set_drd_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/Device/MessageHandlingSystem" with body:
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
    And I note the response field "$.id" as "device_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/Device/MessageHandlingSystem" with body:
      | path                                                               | value              |
      | questionnaire_responses.spine_mhs.0.Address                        | http://example.com |
      | questionnaire_responses.spine_mhs.0.Unique Identifier              | 123457             |
      | questionnaire_responses.spine_mhs.0.Managing Organization          | Example Org        |
      | questionnaire_responses.spine_mhs.0.MHS Manufacturer Organisation  | AAA                |
      | questionnaire_responses.spine_mhs.0.MHS Party key                  | party-key-003      |
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
    Then I receive a status code "400" with body
      | path             | value                                                    |
      | errors.0.code    | VALIDATION_ERROR                                         |
      | errors.0.message | There is already an existing MHS Device for this Product |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 113              |
