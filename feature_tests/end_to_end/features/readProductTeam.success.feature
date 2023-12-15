Feature: Read Product Team - success scenarios

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Read an existing ProductTeam
    Given I have already made a "POST" request with "default" headers to "Organization" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | f9518c12-6c83-4544-97db-d9dd1d64da97                           |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    When I make a "GET" request with "default" headers to "Organization/f9518c12-6c83-4544-97db-d9dd1d64da97"
    Then I receive a status code "200" with body
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | f9518c12-6c83-4544-97db-d9dd1d64da97                           |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 308              |
