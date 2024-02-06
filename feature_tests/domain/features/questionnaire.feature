Feature: Questionnaires

  Scenario: Add questions to a questionnaire
    Given Questionnaire "alpha" version 1
    When I add the following questions to "alpha" version 1
      | name         | type | multiple |
      | given_name   | str  | False    |
      | middle_names | str  | True     |
      | family_name  | str  | False    |
      | age          | int  | False    |
    Then Questionnaire "alpha" version 1 has the questions
      | name         | type | multiple |
      | given_name   | str  | False    |
      | middle_names | str  | True     |
      | family_name  | str  | False    |
      | age          | int  | False    |
