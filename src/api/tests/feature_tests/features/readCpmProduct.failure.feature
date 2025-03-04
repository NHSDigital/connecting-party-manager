Feature: Read CPM Product - failure scenarios
  These scenarios demonstrate failures to read a new CPM Product

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Unknown Product ID
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                                |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 8babe222-5c78-42c6-8aa6-a3c69943030a |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "GET" request with "default" headers to "Product/P.XXX.YYY"
    Then I receive a status code "404" with body
      | path             | value                                           |
      | errors.0.code    | RESOURCE_NOT_FOUND                              |
      | errors.0.message | Could not find CpmProduct for key ('P.XXX.YYY') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 106              |

# Scenario: Can't read a deleted Product
# Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
# | path             | value                 |
# | name             | My Great Product Team |
# | ods_code         | F5H1R                 |
# | keys.0.key_type  | product_team_id_alias |
# | keys.0.key_value | FOOBAR                |
# Given I note the response field "$.id" as "product_team_id"
# And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
# | path | value            |
# | name | My Great Product |
# And I note the response field "$.id" as "product_id"
# And I have already made a "DELETE" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }"
# When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }"
# Then I receive a status code "404" with body
# | path             | value                                                                                     |
# | errors.0.code    | RESOURCE_NOT_FOUND                                                                        |
# | errors.0.message | Could not find CpmProduct for key ('${ note(product_team_id) }', '${ note(product_id) }') |
# And the response headers contain:
# | name           | value            |
# | Content-Type   | application/json |
# | Content-Length | 146              |
