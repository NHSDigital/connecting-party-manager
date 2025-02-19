Feature: Read Device Reference Data - failure scenarios
  These scenarios demonstrate failure reading Device Reference Data

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Read a deleted Product's DeviceReferenceData
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }/dev/DeviceReferenceData" with body:
      | path | value                    |
      | name | My Device Reference Data |
    And I note the response field "$.id" as "device_reference_data_id"
    And I have already made a "DELETE" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }"
    When I make a "GET" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }/dev/DeviceReferenceData/${ note(device_reference_data_id) }"
    Then I receive a status code "404" with body
      | path             | value                                                                                     |
      | errors.0.code    | RESOURCE_NOT_FOUND                                                                        |
      | errors.0.message | Could not find EprProduct for key ('${ note(product_team_id) }', '${ note(product_id) }') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 152              |

  Scenario: Read an unknown product teams DeviceReferenceData
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }/dev/DeviceReferenceData" with body:
      | path | value                    |
      | name | My Device Reference Data |
    And I note the response field "$.id" as "device_reference_data_id"
    When I make a "GET" request with "default" headers to "ProductTeamEpr/F5H1R.f63ba1d2-99b3-4e7f-83b4-a98178f1e4fe/ProductEpr/${ note(product_id) }/dev/DeviceReferenceData/${ note(device_reference_data_id) }"
    Then I receive a status code "404" with body
      | path             | value                                                                             |
      | errors.0.code    | RESOURCE_NOT_FOUND                                                                |
      | errors.0.message | Could not find ProductTeam for key ('F5H1R.f63ba1d2-99b3-4e7f-83b4-a98178f1e4fe') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 140              |

  Scenario: Read an unknown DeviceReferenceData
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }/dev/DeviceReferenceData" with body:
      | path | value                    |
      | name | My Device Reference Data |
    And I note the response field "$.id" as "device_reference_data_id"
    When I make a "GET" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }/dev/DeviceReferenceData/not-a-device-reference-data"
    Then I receive a status code "404" with body
      | path             | value                                                                                                                                    |
      | errors.0.code    | RESOURCE_NOT_FOUND                                                                                                                       |
      | errors.0.message | Could not find DeviceReferenceData for key ('${ note(product_team_id) }', '${ note(product_id) }', 'DEV', 'not-a-device-reference-data') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 199              |
