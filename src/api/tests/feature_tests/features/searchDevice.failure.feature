Feature: Search
  These scenarios demonstrate the expected behaviour of the device search endpoint

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Confirm Search rejects incorrect values for device_type filter
    When I make a "GET" request with "default" headers to "Device?device_type=foobar"
    Then I receive a status code "500" with body
      | path                             | value                                                                 |
      | resourceType                     | OperationOutcome                                                      |
      | id                               | << ignore >>                                                          |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome   |
      | issue.0.severity                 | error                                                                 |
      | issue.0.code                     | processing                                                            |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome   |
      | issue.0.details.coding.0.code    | SERVICE_ERROR                                                         |
      | issue.0.details.coding.0.display | Service error                                                         |
      | issue.0.diagnostics              | 'device_type' query parameter must be one of 'product' or 'endpoint'. |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 494              |

  Scenario: Confirm Search rejects more than 1 filter
    When I make a "GET" request with "default" headers to "Device?device_type=product&foo=bar"
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
      | issue.0.diagnostics              | Only 'device_type' query parameter is allowed.                      |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 471              |

  Scenario: Confirm Search rejects anything other than device_type
    When I make a "GET" request with "default" headers to "Device?foo=bar"
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
      | issue.0.diagnostics              | Only 'device_type' query parameter is allowed.                      |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 471              |
