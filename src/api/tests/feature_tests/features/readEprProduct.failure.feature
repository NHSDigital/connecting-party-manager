Feature: Read EPR Product - failure scenarios
  These scenarios demonstrate failures to read a new EPR Product

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: EPR Product Team doesn't exist
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr" with body:
      | path | value               |
      | name | My Great EprProduct |
    And I note the response field "$.id" as "product_id"
    When I make a "GET" request with "default" headers to "ProductTeamEpr/123/ProductEpr/${ note(product_id) }"
    Then I receive a status code "404" with body
      | path             | value                                      |
      | errors.0.code    | RESOURCE_NOT_FOUND                         |
      | errors.0.message | Could not find ProductTeam for key ('123') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 101              |

  Scenario: Unknown Product ID
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "GET" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/P.XXX.YYY"
    Then I receive a status code "404" with body
      | path             | value                                                                         |
      | errors.0.code    | RESOURCE_NOT_FOUND                                                            |
      | errors.0.message | Could not find EprProduct for key ('${ note(product_team_id) }', 'P.XXX.YYY') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 152              |

  Scenario: Can't read a deleted Product
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I have already made a "DELETE" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }"
    When I make a "GET" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }"
    Then I receive a status code "404" with body
      | path             | value                                                                                     |
      | errors.0.code    | RESOURCE_NOT_FOUND                                                                        |
      | errors.0.message | Could not find EprProduct for key ('${ note(product_team_id) }', '${ note(product_id) }') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 152              |
