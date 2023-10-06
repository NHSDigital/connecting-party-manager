Feature: Questionnaires

  Scenario: Add questions to a questionnaire
    Given Questionnaire "alpha"
    When I add the following questions to "alpha"
      | name         | type   | multiple |
      | given_name   | STRING | False    |
      | middle_names | STRING | True     |
      | family_name  | STRING | False    |
      | age          | INT    | False    |
    Then Questionnaire "alpha" has the questions
      | name         | type   | multiple |
      | given_name   | STRING | False    |
      | middle_names | STRING | True     |
      | family_name  | STRING | False    |
      | age          | INT    | False    |
