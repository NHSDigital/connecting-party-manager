Feature: Delete EPR Product - failure scenarios
  These scenarios demonstrate failures to delete a new EPR Product

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

<<<<<<<< HEAD:src/api/tests/feature_tests/features/deleteEprProduct.failure.feature
  Scenario: EPR Product Team doesn't exist
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
========
  Scenario: CPM Product Team doesn't exist
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
>>>>>>>> e9c92c3 (Create a new ProductTeam and rename the old one):src/api/tests/feature_tests/features/deleteCpmProduct.failure.feature
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
<<<<<<<< HEAD:src/api/tests/feature_tests/features/deleteEprProduct.failure.feature
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr" with body:
      | path | value               |
      | name | My Great EprProduct |
    And I note the response field "$.id" as "product_id"
    When I make a "DELETE" request with "default" headers to "ProductTeamEpr/123/ProductEpr/${ note(product_id) }"
========
    Given I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value               |
      | name | My Great EprProduct |
    And I note the response field "$.id" as "product_id"
    When I make a "DELETE" request with "default" headers to "ProductTeam/123/Product/${ note(product_id) }"
>>>>>>>> e9c92c3 (Create a new ProductTeam and rename the old one):src/api/tests/feature_tests/features/deleteCpmProduct.failure.feature
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
<<<<<<<< HEAD:src/api/tests/feature_tests/features/deleteEprProduct.failure.feature
    When I make a "DELETE" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/P.XXX.YYY"
========
    When I make a "DELETE" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/P.XXX.YYY"
>>>>>>>> e9c92c3 (Create a new ProductTeam and rename the old one):src/api/tests/feature_tests/features/deleteCpmProduct.failure.feature
    Then I receive a status code "404" with body
      | path             | value                                                                         |
      | errors.0.code    | RESOURCE_NOT_FOUND                                                            |
      | errors.0.message | Could not find EprProduct for key ('${ note(product_team_id) }', 'P.XXX.YYY') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 146              |
