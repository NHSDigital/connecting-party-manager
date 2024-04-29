Feature: Search
  These scenarios demonstrate the expected behaviour of the device search endpoint

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Confirm Search endpoint is active with product as filter
    When I make a "GET" request with "default" headers to "Device?device_type=product"
    Then I receive a status code "200"
    And the response headers contain:
      | name         | value            |
      | Content-Type | application/json |

  Scenario: Confirm Search endpoint is active with endpoint as filter
    When I make a "GET" request with "default" headers to "Device?device_type=endpoint"
    Then I receive a status code "200"
    And the response headers contain:
      | name         | value            |
      | Content-Type | application/json |
