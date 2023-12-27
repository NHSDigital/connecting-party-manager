Feature: Read Device - success scenarios
  These scenarios demonstrate successful reads from the GET Device endpoint

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Read an existing Device
    Given I have already made a "POST" request with "default" headers to "Organization" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | ${ uuid(1) }                                                   |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    And I have already made a "POST" request with "default" headers to "Device" with body:
      | path                         | value                                    |
      | resourceType                 | Device                                   |
      | deviceName.0.name            | My Device of type "product"              |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | product                                  |
      | identifier.0.system          | connecting-party-manager/product_id      |
      | identifier.0.value           | P.XXX-YYY                                |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
      | owner.identifier.value       | ${ uuid(1) }                             |
    When I make a "GET" request with "default" headers to "Device/P.XXX-YYY"
    Then I receive a status code "200" with body
      | path                         | value                                    |
      | resourceType                 | Device                                   |
      | deviceName.0.name            | My Device of type "product"              |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | product                                  |
      | identifier.0.system          | connecting-party-manager/product_id      |
      | identifier.0.value           | P.XXX-YYY                                |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
      | owner.identifier.value       | ${ uuid(1) }                             |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 434              |
