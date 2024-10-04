Feature: Read Device - failure scenarios
  These scenarios demonstrate failures from the GET Device endpoint

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Unknown Device
    When I make a "GET" request with "default" headers to "Device/f9518c12-6c83-4544-97db-d9dd1d64da97"
    Then I receive a status code "404" with body
      | path                             | value                                                                  |
      | resourceType                     | OperationOutcome                                                       |
      | id                               | << ignore >>                                                           |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome    |
      | issue.0.severity                 | error                                                                  |
      | issue.0.code                     | processing                                                             |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome    |
      | issue.0.details.coding.0.code    | RESOURCE_NOT_FOUND                                                     |
      | issue.0.details.coding.0.display | Resource not found                                                     |
      | issue.0.diagnostics              | Could not find Device for key ('f9518c12-6c83-4544-97db-d9dd1d64da97') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 503              |
