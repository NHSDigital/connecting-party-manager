Feature: Read Product Team - failure scenarios
  These scenarios demonstrate failures from the GET Organization (i.e. Product Team) endpoint

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Unknown Product Team
    When I make a "GET" request with "default" headers to "ProductTeam/f9518c12-6c83-4544-97db-d9dd1d64da97"
    Then I receive a status code "404" with body
      | path             | value                                                                 |
      | errors.0.code    | RESOURCE_NOT_FOUND                                                    |
      | errors.0.message | Could not find ProductTeam for key ('f9518c12-6c83-4544-97db-d9dd1d64da97') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 128              |
