Feature: Status

  Background:
    Given "default" request headers:
      | name | value |

  Scenario: Confirm Status endpoint is active
    When I make a "GET" request with "default" headers to "_status"
    Then I receive a status code "200" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | << ignore >>                                                        |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | information                                                         |
      | issue.0.code                     | informational                                                       |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | OK                                                                  |
      | issue.0.details.coding.0.display | Transaction successful                                              |
      | issue.0.diagnostics              | Transaction successful                                              |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 448              |
