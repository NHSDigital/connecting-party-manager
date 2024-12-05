Feature: Create Device - failure scenarios
  These scenarios demonstrate failures to create a new Device

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Cannot create a Device with a Device that is missing fields (no name) and has extra param
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device" with body:
      | path      | value     |
      | bad_field | My Device |
    Then I receive a status code "400" with body
      | path             | value                                                            |
      | errors.0.code    | MISSING_VALUE                                                    |
      | errors.0.message | CreateDeviceIncomingParams.name: field required                  |
      | errors.1.code    | VALIDATION_ERROR                                                 |
      | errors.1.message | CreateDeviceIncomingParams.bad_field: extra fields not permitted |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 210              |

  Scenario: Cannot create a Device with a Device with a corrupt body
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device" with body:
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

  Scenario: Cannot create a Device with a Product Team that does not exist
    When I make a "POST" request with "default" headers to "ProductTeam/not-a-product-team/Product/not-a-product/dev/Device" with body:
      | path | value     |
      | name | My Device |
    Then I receive a status code "404" with body
      | path             | value                                                     |
      | errors.0.code    | RESOURCE_NOT_FOUND                                        |
      | errors.0.message | Could not find ProductTeam for key ('not-a-product-team') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 116              |

  Scenario: Cannot create a Device with a Product that does not exist
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/not-a-product/dev/Device" with body:
      | path | value     |
      | name | My Device |
    Then I receive a status code "404" with body
      | path             | value                                                                             |
      | errors.0.code    | RESOURCE_NOT_FOUND                                                                |
      | errors.0.message | Could not find CpmProduct for key ('${ note(product_team_id) }', 'not-a-product') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 156              |

  Scenario: Cannot create a Device with an environment that is not allowed
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/foo/Device" with body:
      | path | value     |
      | name | My Device |
    Then I receive a status code "400" with body
      | path             | value                                                                                                              |
      | errors.0.code    | VALIDATION_ERROR                                                                                                   |
      | errors.0.message | SubCpmProductPathParams.env: value is not a valid enumeration member; permitted: 'dev', 'qa', 'ref', 'int', 'prod' |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 171              |
