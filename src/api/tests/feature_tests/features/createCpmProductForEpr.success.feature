Feature: Create CPM Product for EPR - success scenarios
  These scenarios demonstrate successful CPM product for EPR creation

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Successfully create a CPM Product for EPR
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path         | value            |
      | product_name | My Great Product |
    Then I receive a status code "201" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | << ignore >>                                                        |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | information                                                         |
      | issue.0.code                     | informational                                                       |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | RESOURCE_CREATED                                                    |
      | issue.0.details.coding.0.display | Resource created                                                    |
      | issue.0.diagnostics              | Resource created                                                    |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 466              |
    When I make a "GET" request with "default" headers to the id in the location response header to the endpoint prefix "ProductTeam/${ note(product_team_id) }/Product/<id>"
    Then I receive a status code "200" with body
      | path             | value                      |
      | id               | << ignore >>               |
      | name             | My Great Product           |
      | product_team_id  | ${ note(product_team_id) } |
      | ods_code         | F5H1R                      |
      | keys.0.key_value | F5H1R-850000               |
      | keys.0.key_type  | party_key                  |
      | status           | active                     |
      | created_on       | << ignore >>               |
      | updated_on       | << ignore >>               |
      | deleted_on       | << ignore >>               |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 339              |

  Scenario: Successfully create two CPM Products for EPR with the same ProductTeam
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path         | value            |
      | product_name | My Great Product |
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path         | value                  |
      | product_name | My Other Great Product |
    Then I receive a status code "201" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | << ignore >>                                                        |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | information                                                         |
      | issue.0.code                     | informational                                                       |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | RESOURCE_CREATED                                                    |
      | issue.0.details.coding.0.display | Resource created                                                    |
      | issue.0.diagnostics              | Resource created                                                    |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 466              |
    When I make a "GET" request with "default" headers to the id in the location response header to the endpoint prefix "ProductTeam/${ note(product_team_id) }/Product/<id>"
    Then I receive a status code "200" with body
      | path             | value                      |
      | id               | << ignore >>               |
      | name             | My Other Great Product     |
      | product_team_id  | ${ note(product_team_id) } |
      | ods_code         | F5H1R                      |
      | keys.0.key_value | F5H1R-850001               |
      | keys.0.key_type  | party_key                  |
      | status           | active                     |
      | created_on       | << ignore >>               |
      | updated_on       | << ignore >>               |
      | deleted_on       | << ignore >>               |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 345              |
