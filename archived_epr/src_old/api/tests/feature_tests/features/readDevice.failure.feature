Feature: Read Device - failure scenarios
  These scenarios demonstrate failure reading Device

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Read a deleted Product's Device
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }/dev/Device" with body:
      | path | value     |
      | name | My Device |
    And I note the response field "$.id" as "device_id"
    And I have already made a "DELETE" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }"
    When I make a "GET" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }/dev/Device/${ note(device_id) }"
    Then I receive a status code "404" with body
      | path             | value                                                                                     |
      | errors.0.code    | RESOURCE_NOT_FOUND                                                                        |
      | errors.0.message | Could not find EprProduct for key ('${ note(product_team_id) }', '${ note(product_id) }') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 152              |

  Scenario: Read an unknown product teams Device
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }/dev/Device" with body:
      | path | value     |
      | name | My Device |
    And I note the response field "$.id" as "device_id"
    When I make a "GET" request with "default" headers to "ProductTeamEpr/F5H1R.f63ba1d2-99b3-4e7f-83b4-a98178f1e4fe/ProductEpr/${ note(product_id) }/dev/Device/${ note(device_id) }"
    Then I receive a status code "404" with body
      | path             | value                                                                             |
      | errors.0.code    | RESOURCE_NOT_FOUND                                                                |
      | errors.0.message | Could not find ProductTeam for key ('F5H1R.f63ba1d2-99b3-4e7f-83b4-a98178f1e4fe') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 140              |

  Scenario: Read an unknown Device
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }/dev/Device" with body:
      | path | value     |
      | name | My Device |
    And I note the response field "$.id" as "device_id"
    When I make a "GET" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }/dev/Device/not-a-device"
    Then I receive a status code "404" with body
      | path             | value                                                                                                        |
      | errors.0.code    | RESOURCE_NOT_FOUND                                                                                           |
      | errors.0.message | Could not find Device for key ('${ note(product_team_id) }', '${ note(product_id) }', 'DEV', 'not-a-device') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 171              |
