Feature: Delete CPM Product - failure scenarios
  These scenarios demonstrate failures to delete a new CPM Product

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Product Team doesn't exist
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | ${ uuid(1) }                                                   |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    Given I have already made a "POST" request with "default" headers to "ProductTeam/${ uuid(1) }/Product" with body:
      | path         | value               |
      | product_name | My Great CpmProduct |
    When I make a "DELETE" request with "default" headers to the id in the location response header to the endpoint prefix "ProductTeam/123/Product/<id>"
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
      | issue.0.diagnostics              | Could not find ProductTeam for key ('123')                          |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 481              |

  Scenario: Unknown Product ID
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | ${ uuid(1) }                                                   |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    When I make a "DELETE" request with "default" headers to "ProductTeam/${ uuid(1) }/Product/P.XXX.YYY"
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
      | issue.0.diagnostics              | Could not find CpmProduct for key ('${ uuid(1) }', 'P.XXX.YYY')     |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 526              |