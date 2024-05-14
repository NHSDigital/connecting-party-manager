Feature: Search
  These scenarios demonstrate the expected behaviour of the device search endpoint

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Confirm Search rejects incorrect values for device_type filter
    When I make a "GET" request with "default" headers to "Device?device_type=foobar"
    Then I receive a status code "400" with body
      | path                             | value                                                                     |
      | resourceType                     | OperationOutcome                                                          |
      | id                               | << ignore >>                                                              |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome       |
      | issue.0.severity                 | error                                                                     |
      | issue.0.code                     | processing                                                                |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome       |
      | issue.0.details.coding.0.code    | VALIDATION_ERROR                                                          |
      | issue.0.details.coding.0.display | Validation error                                                          |
      | issue.0.diagnostics              | value is not a valid enumeration member; permitted: 'product', 'endpoint' |
      | issue.0.expression.0             | SearchQueryParams.device_type                                             |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 553              |

  Scenario: Confirm Search rejects more than 1 filter
    When I make a "GET" request with "default" headers to "Device?device_type=product&foo=bar"
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
      | issue.0.expression.0             | SearchQueryParams.foo                                               |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 498              |

  Scenario: Confirm Search rejects anything other than device_type
    When I make a "GET" request with "default" headers to "Device?foo=bar"
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
      | issue.0.expression.0             | SearchQueryParams.device_type                                       |
      | issue.1.severity                 | error                                                               |
      | issue.1.code                     | processing                                                          |
      | issue.1.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.1.details.coding.0.code    | VALIDATION_ERROR                                                    |
      | issue.1.details.coding.0.display | Validation error                                                    |
      | issue.1.diagnostics              | extra fields not permitted                                          |
      | issue.1.expression.0             | SearchQueryParams.foo                                               |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 786              |
