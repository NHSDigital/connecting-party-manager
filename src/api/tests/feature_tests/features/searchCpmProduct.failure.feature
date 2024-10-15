Feature: Search CPM Products - failures scenarios
  These scenarios demonstrate unsuccessful CpmProduct Search

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Search CPM Products per Product Team that does not exist
    When I make a "GET" request with "default" headers to "ProductTeam/${ uuid(1) }/Product"
    Then I receive a status code "404" with body
      | path             | value                                               |
      | errors.0.code    | RESOURCE_NOT_FOUND                                  |
      | errors.0.message | Could not find ProductTeam for key ('${ uuid(1) }') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 134              |
