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
      | path             | value                                                                                                    |
      | errors.0.code    | VALIDATION_ERROR                                                                                         |
      | errors.0.message | SearchQueryParams.device_type: value is not a valid enumeration member; permitted: 'product', 'endpoint' |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 161              |

  Scenario: Confirm Search rejects more than 1 filter
    When I make a "GET" request with "default" headers to "Device?device_type=product&foo=bar"
    Then I receive a status code "400" with body
      | path             | value                                             |
      | errors.0.code    | VALIDATION_ERROR                                  |
      | errors.0.message | SearchQueryParams.foo: extra fields not permitted |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 106              |

  Scenario: Confirm Search rejects anything other than device_type
    When I make a "GET" request with "default" headers to "Device?foo=bar"
    Then I receive a status code "400" with body
      | path             | value                                             |
      | errors.0.code    | MISSING_VALUE                                     |
      | errors.0.message | SearchQueryParams.device_type: field required     |
      | errors.1.code    | VALIDATION_ERROR                                  |
      | errors.1.message | SearchQueryParams.foo: extra fields not permitted |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 193              |
