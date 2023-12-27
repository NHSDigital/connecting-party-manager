Feature: Device Failure Scenarios

  # Scenario: Device ID is not valid
  # Given Product Teams
  # | id                                   | name            | ods_code |
  # | 00702d39-e65f-49f5-b9ef-6570245bfe17 | My Product Team | H8S7A    |
  # When Product Team "00702d39-e65f-49f5-b9ef-6570245bfe17" creates a Device with
  # | property | value          |
  # | id       | not_a_valid_id |
  # | name     | My Device      |
  # | type     | product        |
  # Then the operation is not successful
  # And the error is ValidationError on fields
  # | Device.id |
  Scenario: Device name is not valid
    Given Product Teams
      | id                                   | name            | ods_code |
      | 00702d39-e65f-49f5-b9ef-6570245bfe17 | My Product Team | H8S7A    |
    When Product Team "00702d39-e65f-49f5-b9ef-6570245bfe17" creates a Device with
      | property | value        |
      | name     | My Device 🚀 |
      | type     | product      |
    Then the operation is not successful
    And the error is ValidationError on fields
      | Device.name |

  Scenario: Device type is not valid
    Given Product Teams
      | id                                   | name            | ods_code |
      | 00702d39-e65f-49f5-b9ef-6570245bfe17 | My Product Team | H8S7A    |
    When Product Team "00702d39-e65f-49f5-b9ef-6570245bfe17" creates a Device with
      | property | value      |
      | name     | My Device  |
      | type     | not_a_type |
    Then the operation is not successful
    And the error is ValidationError on fields
      | Device.type |

  Scenario: Multiple bad fields (id, name, type)
    Given Product Teams
      | id                                   | name            | ods_code |
      | 00702d39-e65f-49f5-b9ef-6570245bfe17 | My Product Team | H8S7A    |
    When Product Team "00702d39-e65f-49f5-b9ef-6570245bfe17" creates a Device with
      | property | value        |
      | name     | My Device 🚀 |
      | type     | not_a_type   |
    Then the operation is not successful
    And the error is ValidationError on fields
      | Device.name | Device.type |

  Scenario: Invalid product key types
    Given Product Teams
      | id                                   | name            | ods_code |
      | 00702d39-e65f-49f5-b9ef-6570245bfe17 | My Product Team | H8S7A    |
    When Product Team "00702d39-e65f-49f5-b9ef-6570245bfe17" creates a Device with
      | property    | value          |
      | name        | My Product     |
      | type        | product        |
      | keys.0.key  | AAA-CCC-DDD    |
      | keys.0.type | not_a_key_type |
    Then the operation is not successful
    And the error is ValidationError on fields
      | DeviceKey.type |

  Scenario: Invalid product key for the given types
    Given Product Teams
      | id                                   | name            | ods_code |
      | 00702d39-e65f-49f5-b9ef-6570245bfe17 | My Product Team | H8S7A    |
    When Product Team "00702d39-e65f-49f5-b9ef-6570245bfe17" creates a Device with
      | property    | value                  |
      | name        | My Product             |
      | type        | product                |
      | keys.0.key  | not_a_valid_product_id |
      | keys.0.type | product_id             |
    Then the operation is not successful
    And the error is ValidationError on fields
      | DeviceKey.key |

  Scenario: Cannot add the same valid key twice
    Given Product Teams
      | id                                   | name            | ods_code |
      | 00702d39-e65f-49f5-b9ef-6570245bfe17 | My Product Team | H8S7A    |
    When Product Team "00702d39-e65f-49f5-b9ef-6570245bfe17" creates a Device with
      | property    | value      |
      | name        | My Product |
      | type        | product    |
      | keys.0.key  | P.AAA-CCC  |
      | keys.0.type | product_id |
      | keys.1.key  | P.AAA-CCC  |
      | keys.1.type | product_id |
    Then the operation is not successful
    And the error is DuplicateError
