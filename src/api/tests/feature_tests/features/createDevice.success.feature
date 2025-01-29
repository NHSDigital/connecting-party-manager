Feature: Create Device - success scenarios
  These scenarios demonstrate successful Device creation

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario Outline: Successfully create a Device
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/<product_team_id>/Product" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/<product_team_id>/Product/${ note(product_id) }/dev/Device" with body:
      | path | value     |
      | name | My Device |
    Then I receive a status code "201" with body
      | path                    | value                      |
      | id                      | << ignore >>               |
      | name                    | My Device                  |
      | status                  | active                     |
      | environment             | dev                        |
      | product_id              | ${ note(product_id) }      |
      | product_team_id         | ${ note(product_team_id) } |
      | ods_code                | F5H1R                      |
      | created_on              | << ignore >>               |
      | updated_on              | << ignore >>               |
      | deleted_on              | << ignore >>               |
      | keys                    | []                         |
      | tags                    | []                         |
      | questionnaire_responses | << ignore >>               |
      | device_reference_data   | << ignore >>               |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 396              |
    And I note the response field "$.id" as "device_id"
    When I make a "GET" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/${ note(device_id) }"
    Then I receive a status code "200" with body
      | path                    | value                      |
      | id                      | ${ note(device_id) }       |
      | name                    | My Device                  |
      | status                  | active                     |
      | environment             | dev                        |
      | product_id              | ${ note(product_id) }      |
      | product_team_id         | ${ note(product_team_id) } |
      | ods_code                | F5H1R                      |
      | created_on              | << ignore >>               |
      | updated_on              | << ignore >>               |
      | deleted_on              | << ignore >>               |
      | keys                    | []                         |
      | tags                    | []                         |
      | questionnaire_responses | << ignore >>               |
      | device_reference_data   | << ignore >>               |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 396              |

    Examples:
      | product_team_id            |
      | ${ note(product_team_id) } |
      | FOOBAR                     |

  Scenario Outline: Successfully create a Device with an EPR Product
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/<product_team_id>/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I note the response field "$.keys.0.key_value" as "party_key"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/<product_team_id>/Product/<product_id>/dev/Device" with body:
      | path | value     |
      | name | My Device |
    Then I receive a status code "201" with body
      | path                    | value                      |
      | id                      | << ignore >>               |
      | name                    | My Device                  |
      | status                  | active                     |
      | environment             | dev                        |
      | product_id              | ${ note(product_id) }      |
      | product_team_id         | ${ note(product_team_id) } |
      | ods_code                | F5H1R                      |
      | created_on              | << ignore >>               |
      | updated_on              | << ignore >>               |
      | deleted_on              | << ignore >>               |
      | keys                    | []                         |
      | tags                    | []                         |
      | questionnaire_responses | << ignore >>               |
      | device_reference_data   | << ignore >>               |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 396              |
    And I note the response field "$.id" as "device_id"
    When I make a "GET" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/${ note(device_id) }"
    Then I receive a status code "200" with body
      | path                    | value                      |
      | id                      | ${ note(device_id) }       |
      | name                    | My Device                  |
      | status                  | active                     |
      | environment             | dev                        |
      | product_id              | ${ note(product_id) }      |
      | product_team_id         | ${ note(product_team_id) } |
      | ods_code                | F5H1R                      |
      | created_on              | << ignore >>               |
      | updated_on              | << ignore >>               |
      | deleted_on              | << ignore >>               |
      | keys                    | []                         |
      | tags                    | []                         |
      | questionnaire_responses | << ignore >>               |
      | device_reference_data   | << ignore >>               |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 396              |

    Examples:
      | product_team_id            | product_id            |
      | ${ note(product_team_id) } | ${ note(product_id) } |
      | ${ note(product_team_id) } | ${ note(party_key) }  |
      | FOOBAR                     | ${ note(product_id) } |
      | FOOBAR                     | ${ note(party_key) }  |
