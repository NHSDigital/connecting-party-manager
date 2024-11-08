Feature: Search CPM Products - success scenarios
  These scenarios demonstrate successful Product Search

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Successfully search CPM Products with no results
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product"
    Then I receive a status code "200" with body
      | path    | value |
      | results | []    |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 15               |

  Scenario: Successfully search one CPM Product
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value               |
      | name | My Great CpmProduct |
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product"
    Then I receive a status code "200" with body
      | path                      | value                      |
      | results.0.id              | << ignore >>               |
      | results.0.product_team_id | ${ note(product_team_id) } |
      | results.0.name            | My Great CpmProduct        |
      | results.0.ods_code        | F5H1R                      |
      | results.0.status          | active                     |
      | results.0.keys            | []                         |
      | results.0.created_on      | << ignore >>               |
      | results.0.updated_on      | << ignore >>               |
      | results.0.deleted_on      | << ignore >>               |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 273              |

  Scenario: Successfully search more than one CPM Product
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value              |
      | name | My Great Product 1 |
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value              |
      | name | My Great Product 2 |
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value              |
      | name | My Great Product 3 |
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product"
    Then I receive a status code "200" with body where "results" has a length of "3"
      | path                      | value                      |
      | results.0.id              | << ignore >>               |
      | results.0.product_team_id | ${ note(product_team_id) } |
      | results.0.name            | My Great Product 1         |
      | results.0.ods_code        | F5H1R                      |
      | results.0.status          | active                     |
      | results.0.keys            | []                         |
      | results.0.created_on      | << ignore >>               |
      | results.0.updated_on      | << ignore >>               |
      | results.0.deleted_on      | << ignore >>               |
      | results.1.id              | << ignore >>               |
      | results.1.product_team_id | ${ note(product_team_id) } |
      | results.1.name            | My Great Product 2         |
      | results.1.ods_code        | F5H1R                      |
      | results.1.status          | active                     |
      | results.1.keys            | []                         |
      | results.1.created_on      | << ignore >>               |
      | results.1.updated_on      | << ignore >>               |
      | results.1.deleted_on      | << ignore >>               |
      | results.2.id              | << ignore >>               |
      | results.2.product_team_id | ${ note(product_team_id) } |
      | results.2.name            | My Great Product 3         |
      | results.2.ods_code        | F5H1R                      |
      | results.2.status          | active                     |
      | results.2.keys            | []                         |
      | results.2.created_on      | << ignore >>               |
      | results.2.updated_on      | << ignore >>               |
      | results.2.deleted_on      | << ignore >>               |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 790              |

  Scenario: Deleted Products not returned in search
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value              |
      | name | My Great Product 1 |
    And I note the response field "$.id" as "product_id_1"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value              |
      | name | My Great Product 2 |
    And I note the response field "$.id" as "product_id_2"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value              |
      | name | My Great Product 3 |
    And I note the response field "$.id" as "product_id_3"
    And I have already made a "DELETE" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id_2) }"
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product"
    Then I receive a status code "200" with body where "results" has a length of "2"
      | path                      | value                      |
      | results.0.id              | ${ note(product_id_1) }    |
      | results.0.product_team_id | ${ note(product_team_id) } |
      | results.0.name            | My Great Product 1         |
      | results.0.ods_code        | F5H1R                      |
      | results.0.status          | active                     |
      | results.0.keys            | []                         |
      | results.0.created_on      | << ignore >>               |
      | results.0.updated_on      | << ignore >>               |
      | results.0.deleted_on      | << ignore >>               |
      | results.1.id              | ${ note(product_id_3) }    |
      | results.1.product_team_id | ${ note(product_team_id) } |
      | results.1.name            | My Great Product 3         |
      | results.1.ods_code        | F5H1R                      |
      | results.1.status          | active                     |
      | results.1.keys            | []                         |
      | results.1.created_on      | << ignore >>               |
      | results.1.updated_on      | << ignore >>               |
      | results.1.deleted_on      | << ignore >>               |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 531              |
