Feature: Delete CPM Product - success scenarios
  These scenarios demonstrate success in deleting a CPM Product

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Successfully delete a CPM Product
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "DELETE" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }"
    Then I receive a status code "204"
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 0                |
