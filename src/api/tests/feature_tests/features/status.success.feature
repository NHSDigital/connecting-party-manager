Feature: Status
  These scenarios demonstrate the expected behaviour of the status endpoint

  Background:
    Given "default" request headers:
      | name          | value   |
      | Authorization | letmein |

  Scenario: Confirm Status endpoint is active
    When I make a "GET" request with "default" headers to "_status"
    Then I receive a status code "200"
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 3                |
