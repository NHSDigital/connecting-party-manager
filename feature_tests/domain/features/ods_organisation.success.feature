Feature: ODS Organisation success scenarios

  Scenario Outline: Success - ODS Code exists
    When ODS Organisation <ods_code> called "BURENDO" is created
    Then the operation is successful
    And ODS Organisation <ods_code> exists

    Examples:
      | ods_code |
      | TAJ      |
      | TAH      |
      | TAG      |
