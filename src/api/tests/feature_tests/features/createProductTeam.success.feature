Feature: Create Product Team - success scenarios
  These scenarios demonstrate successful Product Team creation

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Successfully create a ProductTeam
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Then I receive a status code "201" with body
      | path             | key_value             |
      | id               | << ignore >>          |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | status           | active                |
      | created_on       | << ignore >>          |
      | updated_on       | << ignore >>          |
      | deleted_on       | << ignore >>          |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 282              |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }"
    Then I receive a status code "200" with body
      | path             | value                      |
      | id               | ${ note(product_team_id) } |
      | name             | My Great Product Team      |
      | ods_code         | F5H1R                      |
      | status           | active                     |
      | created_on       | << ignore >>               |
      | updated_on       | << ignore >>               |
      | deleted_on       | << ignore >>               |
      | keys.0.key_type  | product_team_id_alias      |
      | keys.0.key_value | FOOBAR                     |

  Scenario: Successfully create a ProductTeam by removing the duplicated keys
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
      | keys.1.key_type  | product_team_id_alias |
      | keys.1.key_value | FOOBAR                |
      | keys.2.key_type  | product_team_id_alias |
      | keys.2.key_value | FOOBAR                |
    Then I receive a status code "201" with body where "keys" has a length of "1"
      | path             | key_value             |
      | id               | << ignore >>          |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | status           | active                |
      | created_on       | << ignore >>          |
      | updated_on       | << ignore >>          |
      | deleted_on       | << ignore >>          |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 282              |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }"
    Then I receive a status code "200" with body
      | path             | value                      |
      | id               | ${ note(product_team_id) } |
      | name             | My Great Product Team      |
      | ods_code         | F5H1R                      |
      | keys.0.key_type  | product_team_id_alias      |
      | keys.0.key_value | FOOBAR                     |
      | status           | active                     |
      | created_on       | << ignore >>               |
      | updated_on       | << ignore >>               |
      | deleted_on       | << ignore >>               |

  Scenario: Successfully create a ProductTeam and view by alias
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Then I receive a status code "201" with body
      | path             | key_value             |
      | id               | << ignore >>          |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | status           | active                |
      | created_on       | << ignore >>          |
      | updated_on       | << ignore >>          |
      | deleted_on       | << ignore >>          |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 282              |
    When I make a "GET" request with "default" headers to "ProductTeam/FOOBAR"
    Then I receive a status code "200" with body
      | path             | value                 |
      | id               | << ignore >>          |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | status           | active                |
      | created_on       | << ignore >>          |
      | updated_on       | << ignore >>          |
      | deleted_on       | << ignore >>          |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |

  Scenario: Successfully create multiple ProductTeams under an organization
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | Product Team-1        |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Then I receive a status code "201" with body
      | path             | key_value             |
      | id               | << ignore >>          |
      | name             | Product Team-1        |
      | ods_code         | F5H1R                 |
      | status           | active                |
      | created_on       | << ignore >>          |
      | updated_on       | << ignore >>          |
      | deleted_on       | << ignore >>          |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 275              |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }"
    Then I receive a status code "200" with body
      | path             | value                      |
      | id               | ${ note(product_team_id) } |
      | name             | Product Team-1             |
      | ods_code         | F5H1R                      |
      | status           | active                     |
      | created_on       | << ignore >>               |
      | updated_on       | << ignore >>               |
      | deleted_on       | << ignore >>               |
      | keys.0.key_type  | product_team_id_alias      |
      | keys.0.key_value | FOOBAR                     |
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | Product Team-2        |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | GARPLY                |
    Then I receive a status code "201" with body
      | path             | key_value             |
      | id               | << ignore >>          |
      | name             | Product Team-2        |
      | ods_code         | F5H1R                 |
      | status           | active                |
      | created_on       | << ignore >>          |
      | updated_on       | << ignore >>          |
      | deleted_on       | << ignore >>          |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | GARPLY                |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 275              |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }"
    Then I receive a status code "200" with body
      | path             | value                      |
      | id               | ${ note(product_team_id) } |
      | name             | Product Team-2             |
      | ods_code         | F5H1R                      |
      | status           | active                     |
      | created_on       | << ignore >>               |
      | updated_on       | << ignore >>               |
      | deleted_on       | << ignore >>               |
      | keys.0.key_type  | product_team_id_alias      |
      | keys.0.key_value | GARPLY                     |
