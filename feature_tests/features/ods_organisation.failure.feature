Feature: ODS Organisation failure scenarios

  Scenario Outline: Failure - ODS Code does not exist
    When ODS Organisation <ods_code> called "BURENDO" is created
    Then the operation is not successful
    And the error is InvalidOdsCodeError

    Examples:
      | ods_code |
      | AAA111   |
      | BBB111   |
      | CCC111   |
