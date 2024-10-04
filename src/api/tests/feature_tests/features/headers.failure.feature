Feature: Headers - failure scenarios
  These scenarios demonstrate invalid header values

  Scenario: Version is missing
    Given "bad" request headers:
      | name          | value   |
      | Authorization | letmein |
    When I make a "GET" request with "bad" headers to "ProductTeam/f9518c12-6c83-4544-97db-d9dd1d64da97"
    Then I receive a status code "400" with body
      | path             | value                                 |
      | errors.0.code    | MISSING_VALUE                         |
      | errors.0.message | Event.headers.version: field required |
    And the response headers contain:
      | name    | value |
      | Version | null  |

  Scenario Outline: Version is invalid
    Given "bad" request headers:
      | name          | value     |
      | version       | <version> |
      | Authorization | letmein   |
    When I make a "GET" request with "bad" headers to "ProductTeam/f9518c12-6c83-4544-97db-d9dd1d64da97"
    Then I receive a status code "400" with body
      | path             | value                                               |
      | errors.0.code    | VALIDATION_ERROR                                    |
      | errors.0.message | Event.headers.version: value is not a valid integer |
    And the response headers contain:
      | name    | value |
      | Version | null  |

    Examples:
      | version      |
      |              |
      | not_a_number |
      | 1.0          |

  Scenario Outline: Version does not exist
    Given "bad" request headers:
      | name          | value     |
      | version       | <version> |
      | Authorization | letmein   |
    When I make a "GET" request with "bad" headers to "ProductTeam/f9518c12-6c83-4544-97db-d9dd1d64da97"
    Then I receive a status code "403" with body
      | path             | value                            |
      | errors.0.code    | ACCESS_DENIED                    |
      | errors.0.message | Version not supported: <version> |
    And the response headers contain:
      | name    | value |
      | Version | null  |

    Examples:
      | version |
      | 0       |
      | -1      |
