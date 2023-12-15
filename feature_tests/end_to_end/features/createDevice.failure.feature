Feature: Create Device - failure scenarios

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Cannot create a Device that already exists
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
      | identifier.0.value           | XXX-YYY                                  |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
      | owner.identifier.value       | ${ uuid(1) }                             |
    When I make a "POST" request with "default" headers to "Device" with body:
      | path                         | value                                    |
      | resourceType                 | Device                                   |
      | deviceName.0.name            | My Device of type "product"              |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | product                                  |
      | identifier.0.system          | connecting-party-manager/product_id      |
      | identifier.0.value           | XXX-YYY                                  |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
      | owner.identifier.value       | ${ uuid(1) }                             |
    Then I receive a status code "400" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | << ignore >>                                                        |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | error                                                               |
      | issue.0.code                     | processing                                                          |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | VALIDATION_ERROR                                                    |
      | issue.0.details.coding.0.display | Validation error                                                    |
      | issue.0.diagnostics              | Item already exists                                                 |

  Scenario: Cannot create a Device with an Device that is missing fields (no owner.identifier.value)
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
      | deviceName.0.name            | My Device of type "product"              |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | product                                  |
      | identifier.0.system          | connecting-party-manager/product_id      |
      | identifier.0.value           | XXX-YYY                                  |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
    Then I receive a status code "400" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | << ignore >>                                                        |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | error                                                               |
      | issue.0.code                     | processing                                                          |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | MISSING_VALUE                                                       |
      | issue.0.details.coding.0.display | Missing value                                                       |
      | issue.0.diagnostics              | field required                                                      |
      | issue.0.expression.0             | Device.owner.identifier.value                                       |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 488              |

  Scenario: Cannot create a Device with invalid FHIR
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
      | resourceType                 | invalid_type                             |
      | deviceName.0.name            | My Device of type "product"              |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | product                                  |
      | identifier.0.system          | connecting-party-manager/product_id      |
      | identifier.0.value           | XXX-YYY                                  |
      | owner.identifier             | connecting-party-manager/product-team-id |
    Then I receive a status code "400" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | << ignore >>                                                        |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | error                                                               |
      | issue.0.code                     | processing                                                          |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | VALIDATION_ERROR                                                    |
      | issue.0.details.coding.0.display | Validation error                                                    |
      | issue.0.diagnostics              | unexpected value; permitted: 'Device'                               |
      | issue.0.expression.0             | Device.resourceType                                                 |
      | issue.1.severity                 | error                                                               |
      | issue.1.code                     | processing                                                          |
      | issue.1.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.1.details.coding.0.code    | VALIDATION_ERROR                                                    |
      | issue.1.details.coding.0.display | Validation error                                                    |
      | issue.1.diagnostics              | value is not a valid dict                                           |
      | issue.1.expression.0             | Device.owner.identifier                                             |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 806              |

  Scenario: Cannot create a Device with an invalid ID
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
      | deviceName.0.name            | My Device of type "product"              |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | product                                  |
      | identifier.0.system          | connecting-party-manager/product_id      |
      | identifier.0.value           | not_a_valid_id                           |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
      | owner.identifier.value       | ${ uuid(1) }                             |
    Then I receive a status code "400" with body
      | path                             | value                                                                                                                                                                        |
      | resourceType                     | OperationOutcome                                                                                                                                                             |
      | id                               | << ignore >>                                                                                                                                                                 |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome                                                                                                          |
      | issue.0.severity                 | error                                                                                                                                                                        |
      | issue.0.code                     | processing                                                                                                                                                                   |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome                                                                                                          |
      | issue.0.details.coding.0.code    | VALIDATION_ERROR                                                                                                                                                             |
      | issue.0.details.coding.0.display | Validation error                                                                                                                                                             |
      | issue.0.diagnostics              | Key 'not_a_valid_id' does not match the expected pattern '^[ACDEFGHJKLMNPRTUVWXY34679]{3}-[ACDEFGHJKLMNPRTUVWXY34679]{3}${ dollar() }' associated with key type 'product_id' |
      | issue.0.expression.0             | Device.identifier.0                                                                                                                                                          |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 630              |

  Scenario: Cannot create a Device with an invalid name
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
      | deviceName.0.name            | My Device 🚀                             |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | product                                  |
      | identifier.0.system          | connecting-party-manager/product_id      |
      | identifier.0.value           | XXX-YYY                                  |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
      | owner.identifier.value       | ${ uuid(1) }                             |
    Then I receive a status code "400" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | << ignore >>                                                        |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | error                                                               |
      | issue.0.code                     | processing                                                          |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | VALIDATION_ERROR                                                    |
      | issue.0.details.coding.0.display | Validation error                                                    |
      | issue.0.diagnostics              | string does not match regex "^[a-zA-Z]{1}[ -~]+$"                   |
      | issue.0.expression.0             | Device.deviceName.0.name                                            |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 526              |

  Scenario: Cannot create a Device with an invalid name type
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
      | deviceName.0.name            | My Device                                |
      | deviceName.0.type            | not_a_type                               |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | product                                  |
      | identifier.0.system          | connecting-party-manager/product_id      |
      | identifier.0.value           | XXX-YYY                                  |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
      | owner.identifier.value       | ${ uuid(1) }                             |
    Then I receive a status code "400" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | << ignore >>                                                        |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | error                                                               |
      | issue.0.code                     | processing                                                          |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | VALIDATION_ERROR                                                    |
      | issue.0.details.coding.0.display | Validation error                                                    |
      | issue.0.diagnostics              | string does not match regex "^user-friendly-name$"                  |
      | issue.0.expression.0             | Device.deviceName.0.type                                            |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 527              |

  Scenario: Cannot create a Device with an invalid device type
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
      | deviceName.0.name            | My Device                                |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | not_a_type                               |
      | identifier.0.system          | connecting-party-manager/product_id      |
      | identifier.0.value           | XXX-YYY                                  |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
      | owner.identifier.value       | ${ uuid(1) }                             |
    Then I receive a status code "400" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | << ignore >>                                                        |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | error                                                               |
      | issue.0.code                     | processing                                                          |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | VALIDATION_ERROR                                                    |
      | issue.0.details.coding.0.display | Validation error                                                    |
      | issue.0.diagnostics              | string does not match regex "^product$"                             |
      | issue.0.expression.0             | Device.definition.identifier.value                                  |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 526              |

  Scenario: Cannot create a Device with an invalid key type
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
      | deviceName.0.name            | My Device                                |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | product                                  |
      | identifier.0.system          | not_a_key_type                           |
      | identifier.0.value           | XXX-YYY                                  |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
      | owner.identifier.value       | ${ uuid(1) }                             |
    Then I receive a status code "400" with body
      | path                             | value                                                                                                |
      | resourceType                     | OperationOutcome                                                                                     |
      | id                               | << ignore >>                                                                                         |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome                                  |
      | issue.0.severity                 | error                                                                                                |
      | issue.0.code                     | processing                                                                                           |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome                                  |
      | issue.0.details.coding.0.code    | VALIDATION_ERROR                                                                                     |
      | issue.0.details.coding.0.display | Validation error                                                                                     |
      | issue.0.diagnostics              | string does not match regex "^connecting-party-manager/(product_id${ pipe() }accredited_system_id)$" |
      | issue.0.expression.0             | Device.identifier.0.system                                                                           |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 569              |

  Scenario: Cannot create a Device with an invalid device id
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
      | deviceName.0.name            | My Device                                |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | product                                  |
      | identifier.0.system          | connecting-party-manager/product_id      |
      | identifier.0.value           | not_a_valid_product_id                   |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
      | owner.identifier.value       | ${ uuid(1) }                             |
    Then I receive a status code "400" with body
      | path                             | value                                                                                                                                                                                |
      | resourceType                     | OperationOutcome                                                                                                                                                                     |
      | id                               | << ignore >>                                                                                                                                                                         |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome                                                                                                                  |
      | issue.0.severity                 | error                                                                                                                                                                                |
      | issue.0.code                     | processing                                                                                                                                                                           |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome                                                                                                                  |
      | issue.0.details.coding.0.code    | VALIDATION_ERROR                                                                                                                                                                     |
      | issue.0.details.coding.0.display | Validation error                                                                                                                                                                     |
      | issue.0.diagnostics              | Key 'not_a_valid_product_id' does not match the expected pattern '^[ACDEFGHJKLMNPRTUVWXY34679]{3}-[ACDEFGHJKLMNPRTUVWXY34679]{3}${ dollar() }' associated with key type 'product_id' |
      | issue.0.expression.0             | Device.identifier.0                                                                                                                                                                  |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 638              |

  Scenario: Cannot create a Device with a repeated key
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
      | deviceName.0.name            | My Device of type "product"              |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | product                                  |
      | identifier.0.system          | connecting-party-manager/product_id      |
      | identifier.0.value           | XXX-YYY                                  |
      | identifier.1.system          | connecting-party-manager/product_id      |
      | identifier.1.value           | XXX-YYY                                  |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
      | owner.identifier.value       | ${ uuid(1) }                             |
    Then I receive a status code "400" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | << ignore >>                                                        |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | error                                                               |
      | issue.0.code                     | processing                                                          |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | VALIDATION_ERROR                                                    |
      | issue.0.details.coding.0.display | Validation error                                                    |
      | issue.0.diagnostics              | It is forbidden to supply the same key multiple times               |
      | issue.0.expression.0             | Device.identifier                                                   |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 521              |

  Scenario: Cannot create a Device with corrupt body
    Given I have already made a "POST" request with "default" headers to "Organization" with body:
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
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | << ignore >>                                                        |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | error                                                               |
      | issue.0.code                     | processing                                                          |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | VALIDATION_ERROR                                                    |
      | issue.0.details.coding.0.display | Validation error                                                    |
      | issue.0.diagnostics              | Invalid JSON body was provided: line 1 column 20 (char 19)          |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 489              |

  Scenario: Cannot create a Device with a Product Team that does not exist
    When I make a "POST" request with "default" headers to "Device" with body:
      | path                         | value                                    |
      | resourceType                 | Device                                   |
      | deviceName.0.name            | My Device of type "product"              |
      | deviceName.0.type            | user-friendly-name                       |
      | definition.identifier.system | connecting-party-manager/device-type     |
      | definition.identifier.value  | product                                  |
      | identifier.0.system          | connecting-party-manager/product_id      |
      | identifier.0.value           | XXX-YYY                                  |
      | owner.identifier.system      | connecting-party-manager/product-team-id |
      | owner.identifier.value       | ${ uuid(1) }                             |
    Then I receive a status code "404" with body
      | path                             | value                                                               |
      | resourceType                     | OperationOutcome                                                    |
      | id                               | << ignore >>                                                        |
      | meta.profile.0                   | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.severity                 | error                                                               |
      | issue.0.code                     | processing                                                          |
      | issue.0.details.coding.0.system  | https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome |
      | issue.0.details.coding.0.code    | RESOURCE_NOT_FOUND                                                  |
      | issue.0.details.coding.0.display | Resource not found                                                  |
      | issue.0.diagnostics              | Could not find object with key '${ uuid(1) }'                       |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 504              |
