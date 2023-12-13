Feature: Create Product Team - failure scenarios

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Cannot create a ProductTeam that already exists
    Given I have already made a "POST" request with "default" headers to "Organization" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | ${ uuid(1) }                                                   |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    When I make a "POST" request with "default" headers to "Organization" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | ${ uuid(1) }                                                   |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    Then I receive a status code "500" with body
      | path                             | value                                                                                                                                                                                                  |
      | resourceType                     | OperationOutcome                                                                                                                                                                                       |
      | id                               | << ignore >>                                                                                                                                                                                           |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome                                                                                                                                    |
      | issue.0.severity                 | error                                                                                                                                                                                                  |
      | issue.0.code                     | processing                                                                                                                                                                                             |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome                                                                                                                                    |
      | issue.0.details.coding.0.code    | SERVICE_ERROR                                                                                                                                                                                          |
      | issue.0.details.coding.0.display | Service error                                                                                                                                                                                          |
      | issue.0.diagnostics              | An error occurred (TransactionCanceledException) when calling the TransactWriteItems operation: Transaction cancelled, please refer cancellation reasons for specific reasons [ConditionalCheckFailed] |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 628              |

  Scenario: Cannot create a ProductTeam with an Organization that is missing fields (no partOf.identifier.value)
    When I make a "POST" request with "default" headers to "Organization" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | ${ uuid(1) }                                                   |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
    Then I receive a status code "400" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | << ignore >>                                                        |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | error                                                               |
      | issue.0.code                     | processing                                                          |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | MISSING_VALUE                                                       |
      | issue.0.details.coding.0.display | Missing value                                                       |
      | issue.0.diagnostics              | field required                                                      |
      | issue.0.expression.0             | Organization.partOf.identifier.value                                |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 500              |

  Scenario: Cannot create a ProductTeam with invalid FHIR
    When I make a "POST" request with "default" headers to "Organization" with body:
      | path                | value                                    |
      | resourceType        | invalid_type                             |
      | identifier.0.system | connecting-party-manager/product-team-id |
      | identifier.0.value  | ${ uuid(1) }                             |
      | name                | My Great Product Team                    |
      | partOf.identifier   | invalid_identifier                       |
    Then I receive a status code "400" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | << ignore >>                                                        |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | error                                                               |
      | issue.0.code                     | processing                                                          |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | VALIDATION_ERROR                                                    |
      | issue.0.details.coding.0.display | Validation error                                                    |
      | issue.0.diagnostics              | unexpected value; permitted: 'Organization'                         |
      | issue.0.expression.0             | Organization.resourceType                                           |
      | issue.1.severity                 | error                                                               |
      | issue.1.code                     | processing                                                          |
      | issue.1.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.1.details.coding.0.code    | VALIDATION_ERROR                                                    |
      | issue.1.details.coding.0.display | Validation error                                                    |
      | issue.1.diagnostics              | value is not a valid dict                                           |
      | issue.1.expression.0             | Organization.partOf.identifier                                      |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 830              |

  Scenario: Cannot create a ProductTeam with an invalid ID
    When I make a "POST" request with "default" headers to "Organization" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | invalid_id                                                     |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    Then I receive a status code "400" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | << ignore >>                                                        |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | error                                                               |
      | issue.0.code                     | processing                                                          |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | VALIDATION_ERROR                                                    |
      | issue.0.details.coding.0.display | Validation error                                                    |
      | issue.0.diagnostics              | value is not a valid uuid                                           |
      | issue.0.expression.0             | Organization.identifier.0.value                                     |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 512              |

  Scenario: Cannot create a ProductTeam with a syntactically invalid ODS Code
    When I make a "POST" request with "default" headers to "Organization" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | ${ uuid(1) }                                                   |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | invalid_ods_code                                               |
    Then I receive a status code "400" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | << ignore >>                                                        |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | error                                                               |
      | issue.0.code                     | processing                                                          |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | VALIDATION_ERROR                                                    |
      | issue.0.details.coding.0.display | Validation error                                                    |
      | issue.0.diagnostics              | string does not match regex "^[a-zA-Z0-9]{1,5}$"                    |
      | issue.0.expression.0             | Organization.partOf.identifier.value                                |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 542              |

  Scenario: Cannot create a ProductTeam with an ODS code that is syntatically correct but doesn't exist
    When I make a "POST" request with "default" headers to "Organization" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | ${ uuid(1) }                                                   |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H11                                                          |
    Then I receive a status code "422" with body
      | path                             | value                                                                                                      |
      | resourceType                     | OperationOutcome                                                                                           |
      | id                               | << ignore >>                                                                                               |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome                                        |
      | issue.0.severity                 | error                                                                                                      |
      | issue.0.code                     | processing                                                                                                 |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome                                        |
      | issue.0.details.coding.0.code    | UNPROCESSABLE_ENTITY                                                                                       |
      | issue.0.details.coding.0.display | A required resource was not available                                                                      |
      | issue.0.diagnostics              | Invalid ODS Code: could not resolve 'https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/F5H11' |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 567              |

  Scenario: Cannot create a ProductTeam with corrupt body
    When I make a "POST" request with "default" headers to "Organization" with body:
      """
      {"invalid_array": [}
      """
    Then I receive a status code "400" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | << ignore >>                                                        |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | error                                                               |
      | issue.0.code                     | processing                                                          |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | VALIDATION_ERROR                                                    |
      | issue.0.details.coding.0.display | Validation error                                                    |
      | issue.0.diagnostics              | Invalid JSON body was provided: line 1 column 20 (char 19)          |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 494              |
