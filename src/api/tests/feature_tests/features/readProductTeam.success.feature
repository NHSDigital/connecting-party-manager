Feature: Read Product Team - success scenarios
  These scenarios demonstrate successful reads from the GET Product Team endpoint

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario Outline: Read an existing ProductTeam
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                                |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 8babe222-5c78-42c6-8aa6-a3c69943030a |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "GET" request with "default" headers to "ProductTeam/<product_team_id>"
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
      | keys.0.key_value | 8babe222-5c78-42c6-8aa6-a3c69943030a |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 306              |

    Examples:
      | product_team_id                      |
      | ${ note(product_team_id) }           |
      | 8babe222-5c78-42c6-8aa6-a3c69943030a |
