Feature: Create Product Team - success scenarios

  Background:
    Given "default" request headers:
      | name    | value |
      | version | 1     |

  Scenario: Successfully create a ProductTeam
    When I make a "POST" request with "default" headers to "Organization" with body:
      | path                    | value                                |
      | resourceType            | Organization                         |
      | id                      | f9518c12-6c83-4544-97db-d9dd1d64da97 |
      | name                    | My Great Product Team                |
      | partOf.identifier.id    | F5H1R                                |
      | partOf.identifier.value | ROYAL DERBY HOSPITAL UTC             |
    Then I receive a status code "201" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | << ignore >>                                                        |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | information                                                         |
      | issue.0.code                     | informational                                                       |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | RESOURCE_CREATED                                                    |
      | issue.0.details.coding.0.display | Resource created                                                    |
      | issue.0.diagnostics              | Resource created                                                    |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 461              |
    When I make a "GET" request with "default" headers to "Organization/f9518c12-6c83-4544-97db-d9dd1d64da97"
    Then I receive a status code "200" with body
      | path                    | value                                |
      | resourceType            | Organization                         |
      | id                      | f9518c12-6c83-4544-97db-d9dd1d64da97 |
      | name                    | My Great Product Team                |
      | partOf.identifier.id    | F5H1R                                |
      | partOf.identifier.value | ROYAL DERBY HOSPITAL UTC             |
