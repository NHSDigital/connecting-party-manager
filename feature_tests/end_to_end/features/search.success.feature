Feature: Search
  These scenarios demonstrate the expected behaviour of the device search endpoint

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Confirm Search endpoint is active
    When I make a "GET" request with "default" headers to "Device?device_type=product"
    Then I receive a status code "200" with body
      | path                                  | value                 |
      | resourceType                          | Bundle                |
      | id                                    | << ignore >>          |
      | total                                 | 1                     |
      | entry.0.resourceType                  | Bundle                |
      | entry.0.total                         | 1                     |
      | entry.0.entry.0.resource.resourceType | Device                |
      | entry.0.entry.1.resourceType          | QuestionnaireResponse |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 12001            |
