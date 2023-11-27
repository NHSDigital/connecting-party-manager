Feature: Product Teams Failure Scenarios

  Scenario: Failure - invalid Product Team Name
    Given ODS Organisations:
      | ods_code | name    |
      | H8S7A    | BURENDO |
    When User "test@example.org" creates Product Team {00702d39-e65f-49f5-b9ef-6570245bfe17} called " " for supplier H8S7A
    Then the operation is not successful
    And the error is ValidationError
