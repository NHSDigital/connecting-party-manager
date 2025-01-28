Feature: Create Product Team - failure scenarios
  These scenarios demonstrate failures to create a new Product Team

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Cannot create a ProductTeam with a product_team_id_alias that already exists
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Then I receive a status code "400" with body
      | path             | value               |
      | errors.0.code    | VALIDATION_ERROR    |
      | errors.0.message | Item already exists |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 76               |

  Scenario: Cannot create a ProductTeam with invalid key_type
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | invalid_alias         |
      | keys.0.key_value | FOOBAR                |
    Then I receive a status code "400" with body
      | path             | value                                                                                                                                  |
      | errors.0.code    | VALIDATION_ERROR                                                                                                                       |
      | errors.0.message | CreateProductTeamIncomingParams.keys.0.key_type: value is not a valid enumeration member; permitted: 'product_team_id_alias', 'epr_id' |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 191              |

  Scenario: Cannot create a ProductTeam with an that is missing fields
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Then I receive a status code "400" with body
      | path             | value                                                    |
      | errors.0.code    | MISSING_VALUE                                            |
      | errors.0.message | CreateProductTeamIncomingParams.ods_code: field required |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 110              |

  Scenario: Cannot create a ProductTeam with a syntactically invalid ODS Code
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | invalid_ods_code      |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Then I receive a status code "422" with body
      | path             | value                                                                                                                 |
      | errors.0.code    | UNPROCESSABLE_ENTITY                                                                                                  |
      | errors.0.message | Invalid ODS Code: could not resolve 'https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/invalid_ods_code' |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 178              |

  Scenario: Cannot create a ProductTeam with an ODS code that is syntatically correct but doesnt exist
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H11                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Then I receive a status code "422" with body
      | path             | value                                                                                                      |
      | errors.0.code    | UNPROCESSABLE_ENTITY                                                                                       |
      | errors.0.message | Invalid ODS Code: could not resolve 'https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/F5H11' |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 167              |

  Scenario: Cannot create a ProductTeam with corrupt body
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
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
