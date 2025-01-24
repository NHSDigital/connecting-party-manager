Feature: Search Device Reference Data - failures scenarios
  These scenarios demonstrate unsuccessful Device Reference Data Search

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Search Device Reference Data per Product associated with a Product Team that does not exist
    When I make a "GET" request with "default" headers to "ProductTeamEpr/F5H1R.f9518c12-6c83-4544-97db-d9dd1d64da97/Product/P.XXX.YYY"
    Then I receive a status code "404" with body
      | path             | value                                                                             |
      | errors.0.code    | RESOURCE_NOT_FOUND                                                                |
      | errors.0.message | Could not find ProductTeam for key ('F5H1R.f9518c12-6c83-4544-97db-d9dd1d64da97') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 140              |

  Scenario: Search Device Reference Data per Product that does not exist associated with a Product Team
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "GET" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/P.XXX.YYY"
    Then I receive a status code "404" with body
      | path             | value                                                                         |
      | errors.0.code    | RESOURCE_NOT_FOUND                                                            |
      | errors.0.message | Could not find CpmProduct for key ('${ note(product_team_id) }', 'P.XXX.YYY') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 152              |
