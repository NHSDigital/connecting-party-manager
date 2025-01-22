<<<<<<<< HEAD:src/api/tests/feature_tests/features/deleteEprProduct.success.feature
Feature: Delete EPR Product - success scenarios
  These scenarios demonstrate success in deleting an EPR Product
========
Feature: Delete CPM Product - success scenarios
  These scenarios demonstrate success in deleting an CPM Product
>>>>>>>> e9c92c3 (Create a new ProductTeam and rename the old one):src/api/tests/feature_tests/features/deleteCpmProduct.success.feature

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

<<<<<<<< HEAD:src/api/tests/feature_tests/features/deleteEprProduct.success.feature
  Scenario Outline: Successfully delete an EPR Product
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
========
  Scenario Outline: Successfully delete a CPM Product
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
>>>>>>>> e9c92c3 (Create a new ProductTeam and rename the old one):src/api/tests/feature_tests/features/deleteCpmProduct.success.feature
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
<<<<<<<< HEAD:src/api/tests/feature_tests/features/deleteEprProduct.success.feature
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "DELETE" request with "default" headers to "ProductTeamEpr/<product_team_id>/ProductEpr/${ note(product_id) }"
========
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "DELETE" request with "default" headers to "ProductTeam/<product_team_id>/Product/${ note(product_id) }"
>>>>>>>> e9c92c3 (Create a new ProductTeam and rename the old one):src/api/tests/feature_tests/features/deleteCpmProduct.success.feature
    Then I receive a status code "204"
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 0                |

    Examples:
      | product_team_id            |
      | ${ note(product_team_id) } |
      | FOOBAR                     |

<<<<<<<< HEAD:src/api/tests/feature_tests/features/deleteEprProduct.success.feature
  Scenario Outline: Successfully delete an EPR Product created for EPR
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
========
  Scenario Outline: Successfully delete a CPM Product and try to read it.
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
>>>>>>>> e9c92c3 (Create a new ProductTeam and rename the old one):src/api/tests/feature_tests/features/deleteCpmProduct.success.feature
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    And I note the response field "$.id" as "product_team_id"
<<<<<<<< HEAD:src/api/tests/feature_tests/features/deleteEprProduct.success.feature
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/<product_team_id>/ProductEpr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I note the response field "$.keys.0.key_value" as "party_key"
    When I make a "DELETE" request with "default" headers to "ProductTeamEpr/<product_team_id>/ProductEpr/<product_id>"
    Then I receive a status code "204"
========
    And I have already made a "POST" request with "default" headers to "ProductTeam/<product_team_id>/Product" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I have already made a "DELETE" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/<product_id>"
    When I make a "GET" request with "default" headers to "ProductTeam/<product_team_id>/Product/<product_id>"
    Then I receive a status code "404" with body
      | path             | value                                                                            |
      | errors.0.code    | RESOURCE_NOT_FOUND                                                               |
      | errors.0.message | Could not find CpmProduct for key ('${ note(product_team_id) }', '<product_id>') |
>>>>>>>> e9c92c3 (Create a new ProductTeam and rename the old one):src/api/tests/feature_tests/features/deleteCpmProduct.success.feature
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 146              |

    Examples:
      | product_team_id            | product_id            |
      | ${ note(product_team_id) } | ${ note(product_id) } |
      | FOOBAR                     | ${ note(product_id) } |
