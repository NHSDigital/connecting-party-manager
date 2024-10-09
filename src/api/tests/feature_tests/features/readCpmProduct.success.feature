Feature: Read CPM Product - success scenarios
  These scenarios demonstrate successful CPM Product reads

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Read an existing CpmProduct
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | f9518c12-6c83-4544-97db-d9dd1d64da97                           |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    Given I have already made a "POST" request with "default" headers to "ProductTeam/f9518c12-6c83-4544-97db-d9dd1d64da97/Product" with body:
      | path         | value               |
      | product_name | My Great CpmProduct |
    When I make a "GET" request with "default" headers to the id in the location response header to the endpoint prefix "ProductTeam/f9518c12-6c83-4544-97db-d9dd1d64da97/Product/<id>"
    Then I receive a status code "200" with body
      | path            | value                                |
      | id              | << ignore >>                         |
      | name            | My Great CpmProduct                  |
      | product_team_id | f9518c12-6c83-4544-97db-d9dd1d64da97 |
      | ods_code        | F5H1R                                |
      | keys            | []                                   |
      | created_on      | << ignore >>                         |
      | updated_on      | << ignore >>                         |
      | deleted_on      | << ignore >>                         |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 232              |
