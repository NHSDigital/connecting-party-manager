Feature: Create CPM Product - failure scenarios
  These scenarios demonstrate failures to create a new CPM Product

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Cannot create a Cpm Product with a Cpm Product that is missing fields (no product_name) and has extra param
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | f9518c12-6c83-4544-97db-d9dd1d64da97                           |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    When I make a "POST" request with "default" headers to "ProductTeam/f9518c12-6c83-4544-97db-d9dd1d64da97/Product" with body:
      | path | value            |
      | name | My Great Product |
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
      | issue.0.expression.0             | CreateCpmProductIncomingParams.product_name                         |
      | issue.1.severity                 | error                                                               |
      | issue.1.code                     | processing                                                          |
      | issue.1.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.1.details.coding.0.code    | VALIDATION_ERROR                                                    |
      | issue.1.details.coding.0.display | Validation error                                                    |
      | issue.1.diagnostics              | extra fields not permitted                                          |
      | issue.1.expression.0             | CreateCpmProductIncomingParams.name                                 |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 818              |

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
      """
      {}
      """
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
      | issue.0.expression.0             | CreateCpmProductIncomingParams.product_name                         |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 506              |

  Scenario: Cannot create a Cpm Product with an invalid body (extra parameter is not allowed)
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
      | issue.0.expression.0             | CreateCpmProductIncomingParams.foo                                  |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 515              |

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
      | path                             | value                                                                 |
      | resourceType                     | OperationOutcome                                                      |
      | id                               | << ignore >>                                                          |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome   |
      | issue.0.severity                 | error                                                                 |
      | issue.0.code                     | processing                                                            |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome   |
      | issue.0.details.coding.0.code    | RESOURCE_NOT_FOUND                                                    |
      | issue.0.details.coding.0.display | Resource not found                                                    |
      | issue.0.diagnostics              | Could not find object with key 'f9518c12-6c83-4544-97db-d9dd1d64da97' |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 508              |
