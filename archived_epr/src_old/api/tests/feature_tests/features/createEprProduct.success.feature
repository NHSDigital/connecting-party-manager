Feature: Create EPR Product - success scenarios
  These scenarios demonstrate successful EPR product creation

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario Outline: Successfully create an EPR Product
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/<product_team_id>/ProductEpr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    Then I receive a status code "201" with body
      | path             | value                      |
      | id               | ${ note(product_id) }      |
      | product_team_id  | ${ note(product_team_id) } |
      | name             | My Great Product           |
      | ods_code         | F5H1R                      |
      | status           | active                     |
      | keys.0.key_type  | party_key                  |
      | keys.0.key_value | F5H1R-850000               |
      | created_on       | << ignore >>               |
      | updated_on       | << ignore >>               |
      | deleted_on       | << ignore >>               |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 339              |
    When I make a "GET" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }"
    Then I receive a status code "200" with body
      | path             | value                      |
      | id               | ${ note(product_id) }      |
      | product_team_id  | ${ note(product_team_id) } |
      | name             | My Great Product           |
      | ods_code         | F5H1R                      |
      | status           | active                     |
      | keys.0.key_type  | party_key                  |
      | keys.0.key_value | F5H1R-850000               |
      | created_on       | << ignore >>               |
      | updated_on       | << ignore >>               |
      | deleted_on       | << ignore >>               |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 339              |

    Examples:
      | product_team_id            |
      | ${ note(product_team_id) } |
      | FOOBAR                     |

  Scenario: Successfully create two EPR Products with the same ProductTeam
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id_1"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr" with body:
      | path | value                  |
      | name | My Other Great Product |
    And I note the response field "$.id" as "product_id_2"
    When I make a "GET" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id_1) }"
    Then I receive a status code "200" with body
      | path             | value                      |
      | id               | ${ note(product_id_1) }    |
      | name             | My Great Product           |
      | product_team_id  | ${ note(product_team_id) } |
      | ods_code         | F5H1R                      |
      | keys.0.key_value | F5H1R-850000               |
      | keys.0.key_type  | party_key                  |
      | status           | active                     |
      | created_on       | << ignore >>               |
      | updated_on       | << ignore >>               |
      | deleted_on       | << ignore >>               |
    When I make a "GET" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id_2) }"
    Then I receive a status code "200" with body
      | path             | value                      |
      | id               | ${ note(product_id_2) }    |
      | name             | My Other Great Product     |
      | product_team_id  | ${ note(product_team_id) } |
      | ods_code         | F5H1R                      |
      | keys.0.key_value | F5H1R-850001               |
      | keys.0.key_type  | party_key                  |
      | status           | active                     |
      | created_on       | << ignore >>               |
      | updated_on       | << ignore >>               |
      | deleted_on       | << ignore >>               |
