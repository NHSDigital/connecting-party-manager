Feature: Search CPM Products - success scenarios
  These scenarios demonstrate successful Device creation

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Successfully search one CPM Product
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | f9518c12-6c83-4544-97db-d9dd1d64da97                           |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    And I have already made a "POST" request with "default" headers to "ProductTeam/f9518c12-6c83-4544-97db-d9dd1d64da97/Product" with body:
      | path         | value               |
      | product_name | My Great CpmProduct |
    When I make a "GET" request with "default" headers to "ProductTeam/f9518c12-6c83-4544-97db-d9dd1d64da97/Product"
    Then I receive a status code "200" with body
      | path              | value                                |
      | 0.id              | << ignore >>                         |
      | 0.product_team_id | f9518c12-6c83-4544-97db-d9dd1d64da97 |
      | 0.name            | My Great CpmProduct                  |
      | 0.ods_code        | F5H1R                                |
      | 0.created_on      | << ignore >>                         |
      | 0.updated_on      | << ignore >>                         |
      | 0.deleted_on      | << ignore >>                         |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 222              |

  Scenario: Successfully search more than one CPM Product
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | f9518c12-6c83-4544-97db-d9dd1d64da97                           |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    And I have already made a "POST" request with "default" headers to "ProductTeam/f9518c12-6c83-4544-97db-d9dd1d64da97/Product" with body:
      | path         | value              |
      | product_name | My Great Product 1 |
    And I have already made a "POST" request with "default" headers to "ProductTeam/f9518c12-6c83-4544-97db-d9dd1d64da97/Product" with body:
      | path         | value              |
      | product_name | My Great Product 2 |
    And I have already made a "POST" request with "default" headers to "ProductTeam/f9518c12-6c83-4544-97db-d9dd1d64da97/Product" with body:
      | path         | value              |
      | product_name | My Great Product 3 |
    When I make a "GET" request with "default" headers to "ProductTeam/f9518c12-6c83-4544-97db-d9dd1d64da97/Product"
    Then I receive a status code "200" with a "product" search body reponse that contains
      | path              | value                                |
      | 0.id              | << ignore >>                         |
      | 0.product_team_id | f9518c12-6c83-4544-97db-d9dd1d64da97 |
      | 0.name            | My Great Product 1                   |
      | 0.ods_code        | F5H1R                                |
      | 0.created_on      | << ignore >>                         |
      | 0.updated_on      | << ignore >>                         |
      | 0.deleted_on      | << ignore >>                         |
      | 1.id              | << ignore >>                         |
      | 1.product_team_id | f9518c12-6c83-4544-97db-d9dd1d64da97 |
      | 1.name            | My Great Product 2                   |
      | 1.ods_code        | F5H1R                                |
      | 1.created_on      | << ignore >>                         |
      | 1.updated_on      | << ignore >>                         |
      | 1.deleted_on      | << ignore >>                         |
      | 2.id              | << ignore >>                         |
      | 2.product_team_id | f9518c12-6c83-4544-97db-d9dd1d64da97 |
      | 2.name            | My Great Product 3                   |
      | 2.ods_code        | F5H1R                                |
      | 2.created_on      | << ignore >>                         |
      | 2.updated_on      | << ignore >>                         |
      | 2.deleted_on      | << ignore >>                         |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 663              |
