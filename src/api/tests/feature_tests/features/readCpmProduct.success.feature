Feature: Read CPM Product - success scenarios
  These scenarios demonstrate successful CPM Product reads

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario Outline: Read an existing CpmProduct
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "GET" request with "default" headers to "ProductTeamEpr/<product_team_id>/Product/${ note(product_id) }"
    Then I receive a status code "200" with body
      | path             | value                      |
      | id               | ${ note(product_id) }      |
      | name             | My Great Product           |
      | product_team_id  | ${ note(product_team_id) } |
      | ods_code         | F5H1R                      |
      | keys.0.key_value | F5H1R-850000               |
      | keys.0.key_type  | party_key                  |
      | status           | active                     |
      | created_on       | << ignore >>               |
      | updated_on       | << ignore >>               |
      | deleted_on       | << ignore >>               |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 339              |

  Scenario Outline: Read an existing CpmProduct created for EPR
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I note the response field "$.keys.0.key_value" as "party_key"
    When I make a "GET" request with "default" headers to "ProductTeamEpr/<product_team_id>/Product/<product_id>"
    Then I receive a status code "200" with body
      | path             | value                      |
      | id               | ${ note(product_id) }      |
      | name             | My Great Product           |
      | product_team_id  | ${ note(product_team_id) } |
      | ods_code         | F5H1R                      |
      | keys.0.key_value | F5H1R-850000               |
      | keys.0.key_type  | party_key                  |
      | status           | active                     |
      | created_on       | << ignore >>               |
      | updated_on       | << ignore >>               |
      | deleted_on       | << ignore >>               |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 339              |

    Examples:
      | product_team_id            | product_id            |
      | ${ note(product_team_id) } | ${ note(product_id) } |
      | ${ note(product_team_id) } | ${ note(party_key) }  |
      | FOOBAR                     | ${ note(product_id) } |
      | FOOBAR                     | ${ note(party_key) }  |
