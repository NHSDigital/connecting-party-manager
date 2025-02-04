Feature: Create CPM Product - failure scenarios
  These scenarios demonstrate failures to create a new CPM Product

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Cannot create a Cpm Product with a Cpm Product that is missing fields (no name) and has extra param
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path       | value            |
      | extra_name | My Great Product |
    Then I receive a status code "400" with body
      | path             | value                                                                 |
      | errors.0.code    | MISSING_VALUE                                                         |
      | errors.0.message | CreateCpmProductIncomingParams.name: field required                   |
      | errors.1.code    | VALIDATION_ERROR                                                      |
      | errors.1.message | CreateCpmProductIncomingParams.extra_name: extra fields not permitted |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 219              |

  Scenario: Cannot create a Cpm Product with a Cpm Product that is missing fields (no name)
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      """
      {}
      """
    Then I receive a status code "400" with body
      | path             | value                                               |
      | errors.0.code    | MISSING_VALUE                                       |
      | errors.0.message | CreateCpmProductIncomingParams.name: field required |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 105              |

  Scenario: Cannot create a Cpm Product with an invalid body (extra parameter is not allowed)
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value            |
      | name | My Great Product |
      | foo  | bar              |
    Then I receive a status code "400" with body
      | path             | value                                                          |
      | errors.0.code    | VALIDATION_ERROR                                               |
      | errors.0.message | CreateCpmProductIncomingParams.foo: extra fields not permitted |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 119              |

  Scenario: Cannot create a Cpm Product with corrupt body
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      """
      {"invalid_array": [}
      """
    Then I receive a status code "400" with body
      | path             | value                                                      |
      | errors.0.code    | VALIDATION_ERROR                                           |
      | errors.0.message | Invalid JSON body was provided: line 1 column 20 (char 19) |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 115              |

  Scenario: Cannot create a Cpm Product with a Product Team that does not exist
    When I make a "POST" request with "default" headers to "ProductTeam/f9518c12-6c83-4544-97db-d9dd1d64da97/Product" with body:
      | path | value            |
      | name | My Great Product |
    Then I receive a status code "404" with body
      | path             | value                                                                       |
      | errors.0.code    | RESOURCE_NOT_FOUND                                                          |
      | errors.0.message | Could not find ProductTeam for key ('f9518c12-6c83-4544-97db-d9dd1d64da97') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 134              |

  Scenario: Cannot create a Cpm Product with an empty name
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value |
      | name |       |
    Then I receive a status code "400" with body
      | path             | value                                                                            |
      | errors.0.code    | VALIDATION_ERROR                                                                 |
      | errors.0.message | CreateCpmProductIncomingParams.name: ensure this value has at least 1 characters |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 137              |
