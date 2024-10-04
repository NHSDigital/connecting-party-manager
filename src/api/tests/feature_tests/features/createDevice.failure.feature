Feature: Create Device - failure scenarios
  These scenarios demonstrate failures to create a new Device

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Cannot create a Device with an Device that is missing fields (no owner.identifier.value)
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
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
      | deviceName.0.name            | My Device of type "product"              |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | product                                  |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
    Then I receive a status code "400" with body
      | path             | value                                         |
      | errors.0.code    | MISSING_VALUE                                 |
      | errors.0.message | Device.owner.identifier.value: field required |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 99               |

  Scenario: Cannot create a Device with invalid FHIR
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | ${ uuid(1) }                                                   |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    When I make a "POST" request with "default" headers to "Device" with body:
      | path                         | value                                    |
      | resourceType                 | invalid_type                             |
      | deviceName.0.name            | My Device of type "product"              |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | product                                  |
      | owner.identifier             | connecting-party-manager/product-team-id |
    Then I receive a status code "400" with body
      | path             | value                                                      |
      | errors.0.code    | VALIDATION_ERROR                                           |
      | errors.0.message | Device.resourceType: unexpected value; permitted: 'Device' |
      | errors.1.code    | VALIDATION_ERROR                                           |
      | errors.1.message | Device.owner.identifier: value is not a valid dict         |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 210              |

  Scenario: Cannot create a Device with an invalid name
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
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
      | deviceName.0.name            | My Device 🚀                             |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | product                                  |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
      | owner.identifier.value       | ${ uuid(1) }                             |
    Then I receive a status code "400" with body
      | path             | value                                                            |
      | errors.0.code    | VALIDATION_ERROR                                                 |
      | errors.0.message | Device.deviceName.0.name: string does not match regex "^[ -~]+$" |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 123              |

  Scenario: Cannot create a Device with an invalid name type
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
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
      | deviceName.0.name            | My Device                                |
      | deviceName.0.type            | not_a_type                               |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | product                                  |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
      | owner.identifier.value       | ${ uuid(1) }                             |
    Then I receive a status code "400" with body
      | path             | value                                                                        |
      | errors.0.code    | VALIDATION_ERROR                                                             |
      | errors.0.message | Device.deviceName.0.type: string does not match regex "^user-friendly-name$" |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 135              |

  Scenario: Cannot create a Device with an invalid device type
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
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
      | deviceName.0.name            | My Device                                |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | not_a_type                               |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
      | owner.identifier.value       | ${ uuid(1) }                             |
    Then I receive a status code "400" with body
      | path             | value                                                                                 |
      | errors.0.code    | VALIDATION_ERROR                                                                      |
      | errors.0.message | Device.definition.identifier.value: string does not match regex "^product\|endpoint$" |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 143              |

  Scenario: Cannot create a Device with an invalid key type
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
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
      | deviceName.0.name            | My Device                                |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | product                                  |
      | identifier.0.system          | not_a_key_type                           |
      | identifier.0.value           | P.XXX-YYY                                |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
      | owner.identifier.value       | ${ uuid(1) }                             |
    Then I receive a status code "400" with body
      | path             | value                                                                                                                                                                 |
      | errors.0.code    | VALIDATION_ERROR                                                                                                                                                      |
      | errors.0.message | Device.identifier.0.system: string does not match regex "^connecting-party-manager/(product_id${ pipe() }accredited_system_id${ pipe() }message_handling_system_id)$" |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 204              |

  Scenario: Cannot create a Device with an invalid device id
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
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
      | deviceName.0.name            | My Device                                |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | product                                  |
      | identifier.0.system          | connecting-party-manager/product_id      |
      | identifier.0.value           | not_a_valid_product_id                   |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
      | owner.identifier.value       | ${ uuid(1) }                             |
    Then I receive a status code "400" with body
      | path             | value                                                                                                                                                                                                         |
      | errors.0.code    | VALIDATION_ERROR                                                                                                                                                                                              |
      | errors.0.message | Device.identifier.0: Key 'not_a_valid_product_id' does not match the expected pattern '^P\\.[ACDEFGHJKLMNPRTUVWXY34679]{3}-[ACDEFGHJKLMNPRTUVWXY34679]{3}${ dollar() }' associated with key type 'product_id' |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 250              |

  Scenario: Cannot create a Device with a repeated key
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | ${ uuid(1) }                                                   |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    When I make a "POST" request with "default" headers to "Device" with body:
      | path                         | value                                         |
      | resourceType                 | Device                                        |
      | deviceName.0.name            | My Device of type "product"                   |
      | deviceName.0.type            | user-friendly-name                            |
      | definition.identifier.system | connecting-party-manager/device-type          |
      | definition.identifier.value  | product                                       |
      | identifier.0.system          | connecting-party-manager/accredited_system_id |
      | identifier.0.value           | ABC:12345                                     |
      | identifier.1.system          | connecting-party-manager/accredited_system_id |
      | identifier.1.value           | ABC:12345                                     |
      | owner.identifier.system      | connecting-party-manager/product-team-id      |
      | owner.identifier.value       | ${ uuid(1) }                                  |
    Then I receive a status code "400" with body
      | path             | value                                                                    |
      | errors.0.code    | VALIDATION_ERROR                                                         |
      | errors.0.message | Device.identifier: It is forbidden to supply the same key multiple times |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 129              |

  Scenario: Cannot create a Device with a product_id
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
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
      | deviceName.0.name            | My Device of type "product"              |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | product                                  |
      | identifier.0.system          | connecting-party-manager/product_id      |
      | identifier.0.value           | P.XXX-YYY                                |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
      | owner.identifier.value       | ${ uuid(1) }                             |
    Then I receive a status code "400" with body
      | path             | value                                                     |
      | errors.0.code    | VALIDATION_ERROR                                          |
      | errors.0.message | Device.identifier: It is forbidden to supply a product_id |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 114              |

  Scenario: Cannot create a Device with corrupt body
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | ${ uuid(1) }                                                   |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    When I make a "POST" request with "default" headers to "Device" with body:
      """
      {"invalid_array": [}
      """
    Then I receive a status code "400" with body
      | path             | value                                                      |
      | errors.0.code    | VALIDATION_ERROR                                           |
      | errors.0.message | Invalid JSON body was provided: line 1 column 20 (char 19) |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 115              |

  Scenario: Cannot create a Device with a Product Team that does not exist
    When I make a "POST" request with "default" headers to "Device" with body:
      | path                         | value                                    |
      | resourceType                 | Device                                   |
      | deviceName.0.name            | My Device of type "product"              |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | product                                  |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
      | owner.identifier.value       | ${ uuid(1) }                             |
    Then I receive a status code "404" with body
      | path             | value                                         |
      | errors.0.code    | RESOURCE_NOT_FOUND                            |
      | errors.0.message | Could not find ProductTeam for key ('${ uuid(1) }') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 128              |
