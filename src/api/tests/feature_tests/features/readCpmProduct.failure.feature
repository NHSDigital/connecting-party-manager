Feature: Read CPM Product - failure scenarios
  These scenarios demonstrate failures to read a new CPM Product

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Product Team doesn't exist
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path         | value               |
      | product_name | My Great CpmProduct |
    When I make a "GET" request with "default" headers to the id in the location response header to the endpoint prefix "ProductTeam/123/Product/<id>"
    Then I receive a status code "404" with body
      | path             | value                                      |
      | errors.0.code    | RESOURCE_NOT_FOUND                         |
      | errors.0.message | Could not find ProductTeam for key ('123') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 101              |

  Scenario: Unknown Product ID
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/P.XXX.YYY"
    Then I receive a status code "404" with body
      | path             | value                                                                         |
      | errors.0.code    | RESOURCE_NOT_FOUND                                                            |
      | errors.0.message | Could not find CpmProduct for key ('${ note(product_team_id) }', 'P.XXX.YYY') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 152              |
