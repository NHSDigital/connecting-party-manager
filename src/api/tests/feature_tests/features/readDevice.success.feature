Feature: Read Device - success scenarios
  These scenarios demonstrate successful reads from the GET Device endpoint

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Read an existing Device
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    Given I note the response field "$.id" as "product_team_id"

# And I have already made a "POST" request with "default" headers to "Device" with body:
# | path                         | value                                    |
# | resourceType                 | Device                                   |
# | deviceName.0.name            | My Device of type "product"              |
# | deviceName.0.type            | user-friendly-name                       |
# | definition.identifier.system | connecting-party-manager/device-type     |
# | definition.identifier.value  | product                                  |
# | owner.identifier.system      | connecting-party-manager/product-team-id |
# | owner.identifier.value       | ${ note(product_team_id) }               |
# When I make a "GET" request with "default" headers to the id in the location response header to the endpoint prefix "Device/<id>"
# Then I receive a status code "200" with body
# | path                         | value                                    |
# | resourceType                 | Device                                   |
# | id                           | << ignore >>                             |
# | deviceName.0.name            | My Device of type "product"              |
# | deviceName.0.type            | user-friendly-name                       |
# | definition.identifier.system | connecting-party-manager/device-type     |
# | definition.identifier.value  | product                                  |
# | identifier.0.system          | connecting-party-manager/product_id      |
# | identifier.0.value           | << ignore >>                             |
# | owner.identifier.system      | connecting-party-manager/product-team-id |
# | owner.identifier.value       | ${ note(product_team_id) }               |
# And the response headers contain:
# | name           | value            |
# | Content-Type   | application/json |
# | Content-Length | 436              |
