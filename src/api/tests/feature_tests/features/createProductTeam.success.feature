Feature: Create Product Team - success scenarios
  These scenarios demonstrate successful Product Team creation

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Successfully create a ProductTeam
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                                |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |
    Then I receive a status code "201" with body
      | path             | key_value                            |
      | id               | << ignore >>                         |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | status           | active                               |
      | created_on       | << ignore >>                         |
      | updated_on       | << ignore >>                         |
      | deleted_on       | << ignore >>                         |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 306              |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }"
    Then I receive a status code "200" with body
      | path             | value                                |
      | id               | ${ note(product_team_id) }           |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | status           | active                               |
      | created_on       | << ignore >>                         |
      | updated_on       | << ignore >>                         |
      | deleted_on       | << ignore >>                         |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |

  Scenario: Successfully create a ProductTeam by removing the duplicated keys
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                                |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |
      | keys.1.key_type  | product_team_id                      |
      | keys.1.key_value | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |
      | keys.2.key_type  | product_team_id                      |
      | keys.2.key_value | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |
    Then I receive a status code "201" with body where "keys" has a length of "1"
      | path             | key_value                            |
      | id               | << ignore >>                         |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | status           | active                               |
      | created_on       | << ignore >>                         |
      | updated_on       | << ignore >>                         |
      | deleted_on       | << ignore >>                         |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 306              |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }"
    Then I receive a status code "200" with body
      | path             | value                                |
      | id               | ${ note(product_team_id) }           |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |
      | status           | active                               |
      | created_on       | << ignore >>                         |
      | updated_on       | << ignore >>                         |
      | deleted_on       | << ignore >>                         |

  Scenario: Successfully create a ProductTeam and view by alias
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                                |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |
    Then I receive a status code "201" with body
      | path             | key_value                            |
      | id               | << ignore >>                         |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | status           | active                               |
      | created_on       | << ignore >>                         |
      | updated_on       | << ignore >>                         |
      | deleted_on       | << ignore >>                         |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 306              |
    When I make a "GET" request with "default" headers to "ProductTeam/0a78ee8f-5bcf-4db1-9341-ef1d67248715"
    Then I receive a status code "200" with body
      | path             | value                                |
      | id               | << ignore >>                         |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | status           | active                               |
      | created_on       | << ignore >>                         |
      | updated_on       | << ignore >>                         |
      | deleted_on       | << ignore >>                         |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |

  Scenario: Successfully create multiple ProductTeams under an organization
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                                |
      | name             | Product Team-1                       |
      | ods_code         | F5H1R                                |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |
    Then I receive a status code "201" with body
      | path             | key_value                            |
      | id               | << ignore >>                         |
      | name             | Product Team-1                       |
      | ods_code         | F5H1R                                |
      | status           | active                               |
      | created_on       | << ignore >>                         |
      | updated_on       | << ignore >>                         |
      | deleted_on       | << ignore >>                         |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 299              |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }"
    Then I receive a status code "200" with body
      | path             | value                                |
      | id               | ${ note(product_team_id) }           |
      | name             | Product Team-1                       |
      | ods_code         | F5H1R                                |
      | status           | active                               |
      | created_on       | << ignore >>                         |
      | updated_on       | << ignore >>                         |
      | deleted_on       | << ignore >>                         |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                                |
      | name             | Product Team-2                       |
      | ods_code         | F5H1R                                |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 62afc7bb-77ad-4596-ab8e-a6dede3fe30b |
    Then I receive a status code "201" with body
      | path             | key_value                            |
      | id               | << ignore >>                         |
      | name             | Product Team-2                       |
      | ods_code         | F5H1R                                |
      | status           | active                               |
      | created_on       | << ignore >>                         |
      | updated_on       | << ignore >>                         |
      | deleted_on       | << ignore >>                         |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 62afc7bb-77ad-4596-ab8e-a6dede3fe30b |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 299              |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }"
    Then I receive a status code "200" with body
      | path             | value                                |
      | id               | ${ note(product_team_id) }           |
      | name             | Product Team-2                       |
      | ods_code         | F5H1R                                |
      | status           | active                               |
      | created_on       | << ignore >>                         |
      | updated_on       | << ignore >>                         |
      | deleted_on       | << ignore >>                         |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 62afc7bb-77ad-4596-ab8e-a6dede3fe30b |
