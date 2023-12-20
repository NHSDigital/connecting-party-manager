Feature: Headers - success scenarios

  Scenario Outline: Headers are case insensitive
    Given "default" request headers:
      | name          | value   |
      | authoRizatION | letmein |
      | VERsion       | 1       |
    When I make a "GET" request with "default" headers to "Organization/f9518c12-6c83-4544-97db-d9dd1d64da97"
    Then the response headers contain:
      | name    | value |
      | Version | 1     |

  Scenario Outline: Any available version can be specified explicitly
    Given "default" request headers:
      | name          | value     |
      | Authorization | letmein   |
      | Version       | <version> |
    When I make a "GET" request with "default" headers to "Organization/f9518c12-6c83-4544-97db-d9dd1d64da97"
    Then the response headers contain:
      | name    | value     |
      | Version | <version> |

    Examples:
      | version |
      | 1       |

  Scenario Outline: Any provided higher version number will round down to an available version
    Given "default" request headers:
      | name          | value     |
      | Authorization | letmein   |
      | Version       | <version> |
    When I make a "GET" request with "default" headers to "Organization/f9518c12-6c83-4544-97db-d9dd1d64da97"
    Then the response headers contain:
      | name    | value |
      | Version | 1     |

    Examples:
      | version |
      | 1000    |
      | 100     |
      | 10      |
      | 5       |
