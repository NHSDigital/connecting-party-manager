Feature: Device Success Scenarios

  Scenario Outline: Successfully create a Device
    Given Product Teams
      | id                                   | name            | ods_code |
      | 00702d39-e65f-49f5-b9ef-6570245bfe17 | My Product Team | H8S7A    |
    When Product Team "00702d39-e65f-49f5-b9ef-6570245bfe17" creates a Device with:
      | property | value  |
      | name     | <name> |
      | type     | <type> |
    Then the operation is successful
    And the result is a Device with
      | property | value  |
      | name     | <name> |
      | type     | <type> |
      | status   | active |
      | ods_code | H8S7A  |
    And the following events were raised for the result
      | event              |
      | DeviceCreatedEvent |
    And event #1 of the result is DeviceCreatedEvent with
      | property | value  |
      | name     | <name> |
      | type     | <type> |
      | status   | active |
      | ods_code | H8S7A  |

    Examples:
      | name       | type    |
      | My Product | product |

  # | XXX-YYY | My API     | service |
  # | XXX-YYY | My Service | api     |
  Scenario: Successfully create a Device with keys
    Given Product Teams
      | id                                   | name            | ods_code |
      | 00702d39-e65f-49f5-b9ef-6570245bfe17 | My Product Team | H8S7A    |
    When Product Team "00702d39-e65f-49f5-b9ef-6570245bfe17" creates a Device with:
      | property    | value                |
      | name        | My Product           |
      | type        | product              |
      | keys.0.key  | P.AAA-CCC            |
      | keys.0.type | product_id           |
      | keys.1.key  | 12345                |
      | keys.1.type | accredited_system_id |
    Then the operation is successful
    And the result is a Device with
      | property              | value                |
      | name                  | My Product           |
      | type                  | product              |
      | status                | active               |
      | ods_code              | H8S7A                |
      | keys.P\\.AAA-CCC.key  | P.AAA-CCC            |
      | keys.P\\.AAA-CCC.type | product_id           |
      | keys.12345.key        | 12345                |
      | keys.12345.type       | accredited_system_id |
    And the following events were raised for the result
      | event                 |
      | DeviceCreatedEvent    |
      | DeviceKeyCreatedEvent |
      | DeviceKeyCreatedEvent |
    And event #1 of the result is DeviceCreatedEvent with
      | property | value      |
      | name     | My Product |
      | type     | product    |
      | status   | active     |
      | ods_code | H8S7A      |
    And event #2 of the result is DeviceKeyAddedEvent with
      | property | value      |
      | key      | P.AAA-CCC  |
      | type     | product_id |
    And event #3 of the result is DeviceKeyAddedEvent with
      | property | value                |
      | key      | 12345                |
      | type     | accredited_system_id |
