Feature: Create CPM Product - success scenarios
  These scenarios demonstrate successful CPM product creation

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario Outline: Successfully create a CPM Product
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeam/<product_team_id>/Product" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    Then I receive a status code "201" with body
      | path            | value                      |
      | id              | ${ note(product_id) }      |
      | name            | My Great Product           |
      | product_team_id | ${ note(product_team_id) } |
      | ods_code        | F5H1R                      |
      | status          | active                     |
      | keys            | []                         |
      | created_on      | << ignore >>               |
      | updated_on      | << ignore >>               |
      | deleted_on      | << ignore >>               |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 249              |
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }"
    Then I receive a status code "200" with body
      | path            | value                      |
      | id              | ${ note(product_id) }      |
      | name            | My Great Product           |
      | product_team_id | ${ note(product_team_id) } |
      | ods_code        | F5H1R                      |
      | status          | active                     |
      | keys            | []                         |
      | created_on      | << ignore >>               |
      | updated_on      | << ignore >>               |
      | deleted_on      | << ignore >>               |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 249              |

    Examples:
      | product_team_id            |
      | ${ note(product_team_id) } |
      | FOOBAR                     |
