Feature: Create Device - success scenarios

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario Outline: Successfully create a Device for each device type
    Given I have already made a "POST" request with "default" headers to "Organization" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | ${ uuid(1) }                                                   |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    When I make a "POST" request with "default" headers to "Device" with body:
      | path                         | value                                    |
      | resourceType                 | Device                                   |
      | deviceName.0.name            | My Device of type "<type>"               |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | <type>                                   |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
      | owner.identifier.value       | ${ uuid(1) }                             |
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
      | Content-Length | 456              |
    When I make a "GET" request with "default" headers to the id in the location response header to the Device endpoint
    Then I receive a status code "200" with body
      | path                         | value                                    |
      | resourceType                 | Device                                   |
      | id                           | << ignore >>                             |
      | deviceName.0.name            | My Device of type "<type>"               |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | <type>                                   |
      | identifier.0.system          | connecting-party-manager/product_id      |
      | identifier.0.value           | << ignore >>                             |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
      | owner.identifier.value       | ${ uuid(1) }                             |

    Examples:
      | type    |
      | product |
