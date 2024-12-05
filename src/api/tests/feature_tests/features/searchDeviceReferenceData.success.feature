Feature: Search Device Reference Data - success scenarios
  These scenarios demonstrate successful Device Reference Data Search

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Successfully search Device Reference Data with no results
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData"
    Then I receive a status code "200" with body
      | path    | value |
      | results | []    |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 15               |

  Scenario: Successfully search one Device Reference Data
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    And I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value               |
      | name | My Great CpmProduct |
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData" with body:
      | path | value                    |
      | name | My Device Reference Data |
    And I note the response field "$.id" as "device_reference_data_id"
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData"
    Then I receive a status code "200" with body
      | path                              | value                               |
      | results.0.id                      | ${ note(device_reference_data_id) } |
      | results.0.product_id              | ${ note(product_id) }               |
      | results.0.product_team_id         | ${ note(product_team_id) }          |
      | results.0.name                    | My Device Reference Data            |
      | results.0.status                  | active                              |
      | results.0.env                     | dev                                 |
      | results.0.ods_code                | F5H1R                               |
      | results.0.created_on              | << ignore >>                        |
      | results.0.updated_on              | << ignore >>                        |
      | results.0.deleted_on              | << ignore >>                        |
      | results.0.questionnaire_responses | {}                                  |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 365              |

  Scenario: Successfully search more than one Device Reference Data
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
    And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData" with body:
      | path | value                      |
      | name | My Device Reference Data 1 |
    And I note the response field "$.id" as "device_reference_data_id_1"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData" with body:
      | path | value                      |
      | name | My Device Reference Data 2 |
    And I note the response field "$.id" as "device_reference_data_id_2"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData" with body:
      | path | value                      |
      | name | My Device Reference Data 3 |
    And I note the response field "$.id" as "device_reference_data_id_3"
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData"
    Then I receive a status code "200" with body where "results" has a length of "3"
      | path                              | value                                 |
      | results.0.id                      | ${ note(device_reference_data_id_1) } |
      | results.0.name                    | My Device Reference Data 1            |
      | results.0.status                  | active                                |
      | results.0.env                     | dev                                   |
      | results.0.product_id              | ${ note(product_id) }                 |
      | results.0.product_team_id         | ${ note(product_team_id) }            |
      | results.0.ods_code                | F5H1R                                 |
      | results.0.created_on              | << ignore >>                          |
      | results.0.updated_on              | << ignore >>                          |
      | results.0.deleted_on              | << ignore >>                          |
      | results.0.questionnaire_responses | {}                                    |
      | results.1.id                      | ${ note(device_reference_data_id_2) } |
      | results.1.name                    | My Device Reference Data 2            |
      | results.1.status                  | active                                |
      | results.1.env                     | dev                                   |
      | results.1.product_id              | ${ note(product_id) }                 |
      | results.1.product_team_id         | ${ note(product_team_id) }            |
      | results.1.ods_code                | F5H1R                                 |
      | results.1.created_on              | << ignore >>                          |
      | results.1.updated_on              | << ignore >>                          |
      | results.1.deleted_on              | << ignore >>                          |
      | results.1.questionnaire_responses | {}                                    |
      | results.2.id                      | ${ note(device_reference_data_id_3) } |
      | results.2.name                    | My Device Reference Data 3            |
      | results.2.status                  | active                                |
      | results.2.env                     | dev                                   |
      | results.2.product_id              | ${ note(product_id) }                 |
      | results.2.product_team_id         | ${ note(product_team_id) }            |
      | results.2.ods_code                | F5H1R                                 |
      | results.2.created_on              | << ignore >>                          |
      | results.2.updated_on              | << ignore >>                          |
      | results.2.deleted_on              | << ignore >>                          |
      | results.2.questionnaire_responses | {}                                    |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 1075             |
