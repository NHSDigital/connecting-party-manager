Feature: Create CPM Product - failure scenarios
  These scenarios demonstrate failures to create a new CPM Product

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Cannot create a Cpm Product with a Cpm Product that is missing fields (no product_name)
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | f9518c12-6c83-4544-97db-d9dd1d64da97                           |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    When I make a "POST" request with "default" headers to "ProductTeam/f9518c12-6c83-4544-97db-d9dd1d64da97/Product" with body:
      | path | value |
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
      | issue.0.expression.0             | CpmProductIncomingParams.product_name                               |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 500              |

  # Scenario: Cannot create a Cpm Product with a Cpm Product that is missing fields (no product_team_id)
  # Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
  # | path                     | value                                                          |
  # | resourceType             | Organization                                                   |
  # | identifier.0.system      | connecting-party-manager/product-team-id                       |
  # | identifier.0.value       | f9518c12-6c83-4544-97db-d9dd1d64da97                           |
  # | name                     | My Great Product Team                                          |
  # | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
  # | partOf.identifier.value  | F5H1R                                                          |
  # When I make a "POST" request with "default" headers to "CpmProduct" with body:
  # | path         | value            |
  # | product_name | My Great Product |
  # Then I receive a status code "400" with body
  # | path                             | value                                                               |
  # | resourceType                     | OperationOutcome                                                    |
  # | id                               | << ignore >>                                                        |
  # | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
  # | issue.0.severity                 | error                                                               |
  # | issue.0.code                     | processing                                                          |
  # | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
  # | issue.0.details.coding.0.code    | MISSING_VALUE                                                       |
  # | issue.0.details.coding.0.display | Missing value                                                       |
  # | issue.0.diagnostics              | field required                                                      |
  # | issue.0.expression.0             | CpmProductIncomingParams.product_team_id                            |
  # And the response headers contain:
  # | name           | value            |
  # | Content-Type   | application/json |
  # | Content-Length | 503              |
  # Scenario: Cannot create a Cpm Product with a Cpm Product with an invalid product team id
  # Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
  # | path                     | value                                                          |
  # | resourceType             | Organization                                                   |
  # | identifier.0.system      | connecting-party-manager/product-team-id                       |
  # | identifier.0.value       | ${ uuid(1) }                                                   |
  # | name                     | My Great Product Team                                          |
  # | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
  # | partOf.identifier.value  | F5H1R                                                          |
  # When I make a "POST" request with "default" headers to "CpmProduct" with body:
  # | path            | value            |
  # | product_name    | My Great Product |
  # | product_team_id | 1234567890       |
  # Then I receive a status code "400" with body
  # | path                             | value                                                               |
  # | resourceType                     | OperationOutcome                                                    |
  # | id                               | << ignore >>                                                        |
  # | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
  # | issue.0.severity                 | error                                                               |
  # | issue.0.code                     | processing                                                          |
  # | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
  # | issue.0.details.coding.0.code    | VALIDATION_ERROR                                                    |
  # | issue.0.details.coding.0.display | Validation error                                                    |
  # | issue.0.diagnostics              | value is not a valid uuid                                           |
  # | issue.0.expression.0             | CpmProductIncomingParams.product_team_id                            |
  # And the response headers contain:
  # | name           | value            |
  # | Content-Type   | application/json |
  # | Content-Length | 520              |
  Scenario: Cannot create a Cpm Product with a Cpm Product with an invalid body extra parameter is not allowed
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | f9518c12-6c83-4544-97db-d9dd1d64da97                           |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    When I make a "POST" request with "default" headers to "ProductTeam/f9518c12-6c83-4544-97db-d9dd1d64da97/Product" with body:
      | path         | value            |
      | product_name | My Great Product |
      | foo          | bar              |
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
      | issue.0.diagnostics              | extra fields not permitted                                          |
      | issue.0.expression.0             | CpmProductIncomingParams.foo                                        |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 509              |

  Scenario: Cannot create a Cpm Product with corrupt body
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | f9518c12-6c83-4544-97db-d9dd1d64da97                           |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    When I make a "POST" request with "default" headers to "ProductTeam/f9518c12-6c83-4544-97db-d9dd1d64da97/Product" with body:
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
      | Content-Length | 493              |

  Scenario: Cannot create a Cpm Product with a Product Team that does not exist
    When I make a "POST" request with "default" headers to "ProductTeam/f9518c12-6c83-4544-97db-d9dd1d64da97/Product" with body:
      | path         | value            |
      | product_name | My Great Product |
    Then I receive a status code "404" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | << ignore >>                                                        |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | error                                                               |
      | issue.0.code                     | processing                                                          |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | RESOURCE_NOT_FOUND                                                  |
      | issue.0.details.coding.0.display | Resource not found                                                  |
      | issue.0.diagnostics              | Could not find object with key '${ uuid(1) }'                       |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 508              |
