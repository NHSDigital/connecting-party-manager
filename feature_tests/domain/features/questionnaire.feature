Feature: Questionnaires

  Scenario: Add questions to a questionnaire
    Given Questionnaire "alpha" version 1
    When I add the following questions to "alpha" version 1
      | name         | type   | multiple |
      | given_name   | STRING | False    |
      | middle_names | STRING | True     |
      | family_name  | STRING | False    |
      | age          | INT    | False    |
    Then Questionnaire "alpha" version 1 has the questions
      | name         | type   | multiple |
      | given_name   | STRING | False    |
      | middle_names | STRING | True     |
      | family_name  | STRING | False    |
      | age          | INT    | False    |
