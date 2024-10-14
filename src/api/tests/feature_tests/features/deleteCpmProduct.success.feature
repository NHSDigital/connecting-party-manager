Feature: Delete CPM Product - success scenarios
  These scenarios demonstrate success in deleting a CPM Product

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Successfully delete a CPM Product
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | ${ uuid(1) }                                                   |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ uuid(1) }/Product" with body:
      | path         | value            |
      | product_name | My Great Product |
    When I make a "DELETE" request with "default" headers to the id in the location response header to the endpoint prefix "ProductTeam/${ uuid(1) }/Product/<id>"
    Then I receive a status code "204"
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 0                |
