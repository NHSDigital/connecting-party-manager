Feature: Search EPR Products - failures scenarios
  These scenarios demonstrate unsuccessful EprProduct Search

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Search EPR Products per Product Team that does not exist
    When I make a "GET" request with "default" headers to "ProductTeamEpr/F5H1R.f9518c12-6c83-4544-97db-d9dd1d64da97/ProductEpr"
    Then I receive a status code "404" with body
      | path             | value                                                                             |
      | errors.0.code    | RESOURCE_NOT_FOUND                                                                |
      | errors.0.message | Could not find ProductTeam for key ('F5H1R.f9518c12-6c83-4544-97db-d9dd1d64da97') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 140              |
