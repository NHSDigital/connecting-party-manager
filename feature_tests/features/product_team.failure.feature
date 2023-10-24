Feature: Product Teams Failure Scenarios

  Scenario: Failure - invalid Product Team Name
    Given ODS Organisations:
      | ods_code | name    |
      | H8S7A    | BURENDO |
    And Users:
      | user_id          | name      |
      | test@example.org | Test User |
    When User "test@example.org" creates Product Team {00702d39-e65f-49f5-b9ef-6570245bfe17} called " " for supplier H8S7A
    Then the operation was not successful
    And the error is AssertionError

  Scenario: Failure - unknown supplier
    Given ODS Organisations:
      | ods_code | name |
    And Users:
      | user_id          | name      |
      | test@example.org | Test User |
    When User "test@example.org" creates Product Team {00702d39-e65f-49f5-b9ef-6570245bfe17} called "BURENDO" for supplier H8S7A
    Then the operation was not successful
    And the error is NotFoundError

  Scenario: Failure - unknown user
    Given ODS Organisations:
      | ods_code | name    |
      | H8S7A    | BURENDO |
    And Users:
      | user_id | name |
    When User "test@example.org" creates Product Team {00702d39-e65f-49f5-b9ef-6570245bfe17} called "BURENDO" for supplier H8S7A
    Then the operation was not successful
    And the error is NotFoundError
