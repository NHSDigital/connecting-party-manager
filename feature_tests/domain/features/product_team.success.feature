Feature: Product Teams Success Scenarios

  Scenario Outline: Successfully create a Product Team
    Given ODS Organisations:
      | ods_code   |
      | <ods_code> |
    When User "<user_id>" creates Product Team <id> called "<name>" for supplier <ods_code>
    Then the operation is successful
    And the result is a ProductTeam with:
      | property | value      |
      | id       | <id>       |
      | name     | <name>     |
      | ods_code | <ods_code> |
    And the following events were raised for the result:
      | event                   |
      | ProductTeamCreatedEvent |
    And event #1 of the result is ProductTeamCreatedEvent with:
      | property | value      |
      | id       | <id>       |
      | name     | <name>     |
      | ods_code | <ods_code> |

    Examples:
      | id                                   | name            | ods_code | user_id          |
      | 00702d39-e65f-49f5-b9ef-6570245bfe17 | My organisation | H8S7A    | test@example.org |
      | d3424f20-e9bd-40d3-a7c1-5c401c5b9a1d | Another Org     | 8JK09    | test@example.org |
