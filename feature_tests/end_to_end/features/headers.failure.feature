Feature: Headers - failure scenarios

  Scenario: Version is missing
    Given "bad" request headers:
      | name | value |
    When I make a "GET" request with "bad" headers to "Organization/f9518c12-6c83-4544-97db-d9dd1d64da97"
    Then I receive a status code "500" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | << ignore >>                                                        |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | error                                                               |
      | issue.0.code                     | processing                                                          |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | SERVICE_ERROR                                                       |
      | issue.0.details.coding.0.display | Service error                                                       |
      | issue.0.diagnostics              | field required                                                      |
      | issue.0.expression.0             | LambdaEventForVersioning.headers.version                            |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 502              |

  Scenario: Version does not exist
    Given "bad" request headers:
      | name    | value |
      | version | 0     |
    When I make a "GET" request with "bad" headers to "Organization/f9518c12-6c83-4544-97db-d9dd1d64da97"
    Then I receive a status code "500" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | << ignore >>                                                        |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | error                                                               |
      | issue.0.code                     | processing                                                          |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | ACCESS_DENIED                                                       |
      | issue.0.details.coding.0.display | Access has been denied to process this request                      |
      | issue.0.diagnostics              | Version not supported                                               |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 482              |
