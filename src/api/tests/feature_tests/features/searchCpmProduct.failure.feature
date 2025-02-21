Feature: Search Products - failures scenarios
  These scenarios demonstrate unsuccessful Product Search

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Unsuccessfully search a Product without query params
    When I make a "GET" request with "default" headers to "Product"
    Then I receive a status code "400" with body
      | path             | value                                                                                                                          |
      | errors.0.code    | VALIDATION_ERROR                                                                                                               |
      | errors.0.message | SearchProductQueryParams.__root__: Please provide exactly one valid query parameter: ('product_team_id', 'organisation_code'). |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 183              |

  Scenario: Unsuccessfully search a Product with unknown query param
    When I make a "GET" request with "default" headers to "Product?product_team_id=123&foo=bar"
    Then I receive a status code "400" with body
      | path             | value                                                    |
      | errors.0.code    | VALIDATION_ERROR                                         |
      | errors.0.message | SearchProductQueryParams.foo: extra fields not permitted |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 113              |

  Scenario: Unsuccessfully search a Product with too many query param
    When I make a "GET" request with "default" headers to "Product?product_team_id=123&organisation_code=XYZ"
    Then I receive a status code "400" with body
      | path             | value                                                                                                                          |
      | errors.0.code    | VALIDATION_ERROR                                                                                                               |
      | errors.0.message | SearchProductQueryParams.__root__: Please provide exactly one valid query parameter: ('product_team_id', 'organisation_code'). |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 183              |
