Feature: Create Product Team - failure scenarios

  Background:
    Given "default" request headers:
      | name             | value      |
      | version          | 1          |
      | x-correlation-id | ${guid: 1} |
      | x-version-id     | ${guid: 1} |
      | Authorization    | letmein    |

  Scenario: Cannot create a ProductTeam that already exists
    Given I have already made a "POST" request with "default" headers to "Organization" with body:
      | path                    | value                                |
      | resourceType            | Organization                         |
      | id                      | f9518c12-6c83-4544-97db-d9dd1d64da97 |
      | name                    | My Great Product Team                |
      | partOf.identifier.id    | F5H1R                                |
      | partOf.identifier.value | ROYAL DERBY HOSPITAL UTC             |
      | contact.0.name.text     | My Company Name                      |
      | telecom.0.system        | email                                |
      | telecom.0.value         | admin@mycompanyname.com              |
    When I make a "POST" request with "default" headers to "Organization" with body:
      | path                    | value                                |
      | resourceType            | Organization                         |
      | id                      | f9518c12-6c83-4544-97db-d9dd1d64da97 |
      | name                    | My Great Product Team                |
      | partOf.identifier.id    | F5H1R                                |
      | partOf.identifier.value | ROYAL DERBY HOSPITAL UTC             |
      | contact.0.name.text     | My Company Name                      |
      | telecom.0.system        | email                                |
      | telecom.0.value         | admin@mycompanyname.com              |
    Then I receive a status code "500" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | ${guid: 2}                                                          |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | error                                                               |
      | issue.0.code                     | processing                                                          |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | SERVICE_ERROR                                                       |
      | issue.0.details.coding.0.display | Service Error                                                       |
      | issue.0.diagnostics              | Service Error                                                       |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 449              |

  Scenario: Cannot create a ProductTeam with an Organization that is missing fields (no contact.0.name)
    When I make a "POST" request with "default" headers to "Organization" with body:
      | path                    | value                                |
      | resourceType            | Organization                         |
      | id                      | f9518c12-6c83-4544-97db-d9dd1d64da97 |
      | name                    | My Great Product Team                |
      | partOf.identifier.id    | F5H1R                                |
      | partOf.identifier.value | ROYAL DERBY HOSPITAL UTC             |
      | telecom.0.system        | email                                |
      | telecom.0.value         | admin@mycompanyname.com              |
    Then I receive a status code "400" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | ${guid: 2}                                                          |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | error                                                               |
      | issue.0.code                     | processing                                                          |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | MISSING_VALUE                                                       |
      | issue.0.details.coding.0.display | Missing Value                                                       |
      | issue.0.diagnostics              | some pydantic error                                                 |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 449              |

  Scenario: Cannot create a ProductTeam with an Organization that fails to validate
    When I make a "POST" request with "default" headers to "Organization" with body:
      | path                    | value                    |
      | resourceType            | invalid_type             |
      | id                      | invalid_id               |
      | name                    | My Great Product Team    |
      | partOf.identifier.id    | invalid_ods_code         |
      | partOf.identifier.value | ROYAL DERBY HOSPITAL UTC |
      | telecom.0.system        | invalid_system           |
      | telecom.0.value         | invalid_email            |
    Then I receive a status code "400" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | ${guid: 2}                                                          |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | error                                                               |
      | issue.0.code                     | processing                                                          |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | VALIDATION_ERROR                                                    |
      | issue.0.details.coding.0.display | Validation Error                                                    |
      | issue.0.diagnostics              | some pydantic error                                                 |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 449              |

  Scenario: Cannot create a ProductTeam with an ODS code that is syntatically correct but doesn't exist
    When I make a "POST" request with "default" headers to "Organization" with body:
      | path                    | value                                |
      | resourceType            | Organization                         |
      | id                      | f9518c12-6c83-4544-97db-d9dd1d64da97 |
      | name                    | My Great Product Team                |
      | partOf.identifier.id    | F5H11                                |
      | partOf.identifier.value | ROYAL DERBY HOSPITAL UTC             |
      | telecom.0.system        | email                                |
      | telecom.0.value         | admin@mycompanyname.com              |
    Then I receive a status code "422" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | ${guid: 2}                                                          |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | error                                                               |
      | issue.0.code                     | processing                                                          |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | UNPROCESSABLE_ENTITY                                                |
      | issue.0.details.coding.0.display | Unprocessable Entity                                                |
      | issue.0.diagnostics              | Unprocessable Entity                                                |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 449              |
