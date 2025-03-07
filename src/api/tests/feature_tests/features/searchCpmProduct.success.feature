Feature: Search Products - success scenarios
  These scenarios demonstrate successful Product Search

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Successfully search Products with no results
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                                |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 808a36db-a52a-4130-b71e-d9cbcbaed15b |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "GET" request with "default" headers to "Product?product_team_id=${ note(product_team_id) }"
    Then I receive a status code "200" with body
      | path    | value |
      | results | []    |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 15               |

  Scenario Outline: Successfully search one Product with product team id or alias
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                                |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 808a36db-a52a-4130-b71e-d9cbcbaed15b |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "GET" request with "default" headers to "Product?product_team_id=<product_team_id>"
    Then I receive a status code "200" with body
      | path                                                     | value                                |
      | results.0.org_code                                       | F5H1R                                |
      | results.0.product_teams.0.product_team_id                | 808a36db-a52a-4130-b71e-d9cbcbaed15b |
      | results.0.product_teams.0.cpm_product_team_id            | ${ note(product_team_id) }           |
      | results.0.product_teams.0.products.0.id                  | ${ note(product_id) }                |
      | results.0.product_teams.0.products.0.cpm_product_team_id | ${ note(product_team_id) }           |
      | results.0.product_teams.0.products.0.product_team_id     | 808a36db-a52a-4130-b71e-d9cbcbaed15b |
      | results.0.product_teams.0.products.0.name                | My Great Product                     |
      | results.0.product_teams.0.products.0.ods_code            | F5H1R                                |
      | results.0.product_teams.0.products.0.status              | active                               |
      | results.0.product_teams.0.products.0.created_on          | << ignore >>                         |
      | results.0.product_teams.0.products.0.updated_on          | null                                 |
      | results.0.product_teams.0.products.0.deleted_on          | null                                 |
      | results.0.product_teams.0.products.0.keys                | []                                   |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 507              |

    Examples:
      | product_team_id                      |
      | ${ note(product_team_id) }           |
      | 808a36db-a52a-4130-b71e-d9cbcbaed15b |

  Scenario: Successfully search one Product with oragnisation code
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                                |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 808a36db-a52a-4130-b71e-d9cbcbaed15b |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "GET" request with "default" headers to "Product?organisation_code=F5H1R"
    Then I receive a status code "200" with body
      | path                                                     | value                                |
      | results.0.org_code                                       | F5H1R                                |
      | results.0.product_teams.0.product_team_id                | 808a36db-a52a-4130-b71e-d9cbcbaed15b |
      | results.0.product_teams.0.cpm_product_team_id            | ${ note(product_team_id) }           |
      | results.0.product_teams.0.products.0.id                  | ${ note(product_id) }                |
      | results.0.product_teams.0.products.0.cpm_product_team_id | ${ note(product_team_id) }           |
      | results.0.product_teams.0.products.0.product_team_id     | 808a36db-a52a-4130-b71e-d9cbcbaed15b |
      | results.0.product_teams.0.products.0.name                | My Great Product                     |
      | results.0.product_teams.0.products.0.ods_code            | F5H1R                                |
      | results.0.product_teams.0.products.0.status              | active                               |
      | results.0.product_teams.0.products.0.created_on          | << ignore >>                         |
      | results.0.product_teams.0.products.0.updated_on          | null                                 |
      | results.0.product_teams.0.products.0.deleted_on          | null                                 |
      | results.0.product_teams.0.products.0.keys                | []                                   |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 507              |

  Scenario Outline: Successfully search more than one Product with product team id or alias
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                                |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 808a36db-a52a-4130-b71e-d9cbcbaed15b |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value              |
      | name | My Great Product 1 |
    And I note the response field "$.id" as "product_id_1"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value              |
      | name | My Great Product 2 |
    And I note the response field "$.id" as "product_id_2"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value              |
      | name | My Great Product 3 |
    And I note the response field "$.id" as "product_id_3"
    When I make a "GET" request with "default" headers to "Product?product_team_id=${ note(product_team_id) }"
    Then I receive a status code "200" with body where ProductTeams has a length of "1" with "3" Products each
      | path                                                     | value                                |
      | results.0.org_code                                       | F5H1R                                |
      | results.0.product_teams.0.product_team_id                | 808a36db-a52a-4130-b71e-d9cbcbaed15b |
      | results.0.product_teams.0.cpm_product_team_id            | ${ note(product_team_id) }           |
      | results.0.product_teams.0.products.0.id                  | ${ note(product_id_1) }              |
      | results.0.product_teams.0.products.0.cpm_product_team_id | ${ note(product_team_id) }           |
      | results.0.product_teams.0.products.0.product_team_id     | 808a36db-a52a-4130-b71e-d9cbcbaed15b |
      | results.0.product_teams.0.products.0.name                | My Great Product 1                   |
      | results.0.product_teams.0.products.0.ods_code            | F5H1R                                |
      | results.0.product_teams.0.products.0.status              | active                               |
      | results.0.product_teams.0.products.0.created_on          | << ignore >>                         |
      | results.0.product_teams.0.products.0.updated_on          | null                                 |
      | results.0.product_teams.0.products.0.deleted_on          | null                                 |
      | results.0.product_teams.0.products.0.keys                | []                                   |
      | results.0.product_teams.0.products.1.id                  | ${ note(product_id_2) }              |
      | results.0.product_teams.0.products.1.cpm_product_team_id | ${ note(product_team_id) }           |
      | results.0.product_teams.0.products.1.product_team_id     | 808a36db-a52a-4130-b71e-d9cbcbaed15b |
      | results.0.product_teams.0.products.1.name                | My Great Product 2                   |
      | results.0.product_teams.0.products.1.ods_code            | F5H1R                                |
      | results.0.product_teams.0.products.1.status              | active                               |
      | results.0.product_teams.0.products.1.created_on          | << ignore >>                         |
      | results.0.product_teams.0.products.1.updated_on          | null                                 |
      | results.0.product_teams.0.products.1.deleted_on          | null                                 |
      | results.0.product_teams.0.products.1.keys                | []                                   |
      | results.0.product_teams.0.products.2.id                  | ${ note(product_id_3) }              |
      | results.0.product_teams.0.products.2.cpm_product_team_id | ${ note(product_team_id) }           |
      | results.0.product_teams.0.products.2.product_team_id     | 808a36db-a52a-4130-b71e-d9cbcbaed15b |
      | results.0.product_teams.0.products.2.name                | My Great Product 3                   |
      | results.0.product_teams.0.products.2.ods_code            | F5H1R                                |
      | results.0.product_teams.0.products.2.status              | active                               |
      | results.0.product_teams.0.products.2.created_on          | << ignore >>                         |
      | results.0.product_teams.0.products.2.updated_on          | null                                 |
      | results.0.product_teams.0.products.2.deleted_on          | null                                 |
      | results.0.product_teams.0.products.2.keys                | []                                   |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 1141             |

    Examples:
      | product_team_id                      |
      | ${ note(product_team_id) }           |
      | 808a36db-a52a-4130-b71e-d9cbcbaed15b |

  Scenario: Successfully search Products under multiple product teams
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                   |
      | name     | My Great Product Team 1 |
      | ods_code | F5H1R                   |
    Given I note the response field "$.id" as "product_team_id_1"
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                   |
      | name     | My Great Product Team 2 |
      | ods_code | F5H1R                   |
    Given I note the response field "$.id" as "product_team_id_2"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id_1) }/Product" with body:
      | path | value              |
      | name | My Great Product 1 |
    And I note the response field "$.id" as "product_id_1"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id_2) }/Product" with body:
      | path | value              |
      | name | My Great Product 2 |
    And I note the response field "$.id" as "product_id_2"
    When I make a "GET" request with "default" headers to "Product?organisation_code=F5H1R"
    Then I receive a status code "200" with body where ProductTeams has a length of "2" with "2" Products each
      | path                                                     | value                        |
      | results.0.org_code                                       | F5H1R                        |
      | results.0.product_teams.0.product_team_id                | null                         |
      | results.0.product_teams.0.cpm_product_team_id            | ${ note(product_team_id_1) } |
      | results.0.product_teams.0.products.0.id                  | ${ note(product_id_1) }      |
      | results.0.product_teams.0.products.0.cpm_product_team_id | ${ note(product_team_id_1) } |
      | results.0.product_teams.0.products.0.product_team_id     | null                         |
      | results.0.product_teams.0.products.0.name                | My Great Product 1           |
      | results.0.product_teams.0.products.0.ods_code            | F5H1R                        |
      | results.0.product_teams.0.products.0.status              | active                       |
      | results.0.product_teams.0.products.0.created_on          | << ignore >>                 |
      | results.0.product_teams.0.products.0.updated_on          | null                         |
      | results.0.product_teams.0.products.0.deleted_on          | null                         |
      | results.0.product_teams.0.products.0.keys                | []                           |
      | results.0.product_teams.1.product_team_id                | null                         |
      | results.0.product_teams.1.cpm_product_team_id            | ${ note(product_team_id_2) } |
      | results.0.product_teams.1.products.0.id                  | ${ note(product_id_2) }      |
      | results.0.product_teams.1.products.0.cpm_product_team_id | ${ note(product_team_id_2) } |
      | results.0.product_teams.1.products.0.product_team_id     | null                         |
      | results.0.product_teams.1.products.0.name                | My Great Product 2           |
      | results.0.product_teams.1.products.0.ods_code            | F5H1R                        |
      | results.0.product_teams.1.products.0.status              | active                       |
      | results.0.product_teams.1.products.0.created_on          | << ignore >>                 |
      | results.0.product_teams.1.products.0.updated_on          | null                         |
      | results.0.product_teams.1.products.0.deleted_on          | null                         |
      | results.0.product_teams.1.products.0.keys                | []                           |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 827              |

  Scenario: Deleted Products not returned in search
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                                |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 808a36db-a52a-4130-b71e-d9cbcbaed15b |
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
    When I make a "GET" request with "default" headers to "Product?product_team_id=${ note(product_team_id) }"
    Then I receive a status code "200" with body where ProductTeams has a length of "1" with "2" Products each
      | path                                                     | value                                |
      | results.0.org_code                                       | F5H1R                                |
      | results.0.product_teams.0.product_team_id                | 808a36db-a52a-4130-b71e-d9cbcbaed15b |
      | results.0.product_teams.0.cpm_product_team_id            | ${ note(product_team_id) }           |
      | results.0.product_teams.0.products.0.id                  | ${ note(product_id_1) }              |
      | results.0.product_teams.0.products.0.cpm_product_team_id | ${ note(product_team_id) }           |
      | results.0.product_teams.0.products.0.product_team_id     | 808a36db-a52a-4130-b71e-d9cbcbaed15b |
      | results.0.product_teams.0.products.0.name                | My Great Product 1                   |
      | results.0.product_teams.0.products.0.ods_code            | F5H1R                                |
      | results.0.product_teams.0.products.0.status              | active                               |
      | results.0.product_teams.0.products.0.created_on          | << ignore >>                         |
      | results.0.product_teams.0.products.0.updated_on          | null                                 |
      | results.0.product_teams.0.products.0.deleted_on          | null                                 |
      | results.0.product_teams.0.products.0.keys                | []                                   |
      | results.0.product_teams.0.products.1.id                  | ${ note(product_id_3) }              |
      | results.0.product_teams.0.products.1.cpm_product_team_id | ${ note(product_team_id) }           |
      | results.0.product_teams.0.products.1.product_team_id     | 808a36db-a52a-4130-b71e-d9cbcbaed15b |
      | results.0.product_teams.0.products.1.name                | My Great Product 3                   |
      | results.0.product_teams.0.products.1.ods_code            | F5H1R                                |
      | results.0.product_teams.0.products.1.status              | active                               |
      | results.0.product_teams.0.products.1.created_on          | << ignore >>                         |
      | results.0.product_teams.0.products.1.updated_on          | null                                 |
      | results.0.product_teams.0.products.1.deleted_on          | null                                 |
      | results.0.product_teams.0.products.1.keys                | []                                   |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 825              |
