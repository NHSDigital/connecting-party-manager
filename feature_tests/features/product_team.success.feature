Feature: Product Teams Success Scenarios

  Scenario Outline: Successfully create a Product Team
    Given ODS Organisations:
      | ods_code   | name       |
      | <ods_code> | <ods_name> |
    And Users:
      | user_id   | name      |
      | <user_id> | Test User |
    When User "<user_id>" creates Product Team <id> called "<name>" for supplier <ods_code>
    Then the operation is successful
    And the result is a ProductTeam with:
      | property | value  |
      | id       | <id>   |
      | name     | <name> |
    And the result organisation is an OdsOrganisation with:
      | property | value      |
      | id       | <ods_code> |
    And the result owner is a User with:
      | property | value     |
      | id       | <user_id> |
    And the following events were raised:
      | event                   |
      | ProductTeamCreatedEvent |
    And event #1 is ProductTeamCreatedEvent with:
      | property                     | value      |
      | product_team.id              | <id>       |
      | product_team.name            | <name>     |
      | product_team.organisation.id | <ods_code> |
      | product_team.owner.id        | <user_id>  |

    Examples:
      | id                                     | name            | ods_code | ods_name           | user_id          |
      | {00702d39-e65f-49f5-b9ef-6570245bfe17} | My organisation | H8S7A    | BURENDO            | test@example.org |
      | {d3424f20-e9bd-40d3-a7c1-5c401c5b9a1d} | Another Org     | 8JK09    | AIRE LOGIC LIMITED | test@example.org |
