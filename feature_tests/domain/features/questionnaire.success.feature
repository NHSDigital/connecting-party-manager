Feature: Success Scenarios

  Scenario: Create new questionnaire
    When I create a Questionnaire with the following attributes
      | name                   | version |
      | example_questionnaire  | 1       |
      | example_questionnaire2 | 1       |
    Then a questionnaire with the following attributes is created
      | expected_name          | expected_version |
      | example_questionnaire  | 1                |
      | example_questionnaire2 | 1                |

  Scenario: Add questions to a questionnaire
    Given Questionnaire "example_questionnaire" version 1
    When I add the following questions to Questionnaire "example_questionnaire" version 1
      | name         | type | multiple |
      | given_name   | str  | False    |
      | middle_names | str  | True     |
      | family_name  | str  | False    |
      | age          | int  | False    |
    Then Questionnaire "example_questionnaire" version 1 has the questions
      | name         | type | multiple |
      | given_name   | str  | False    |
      | middle_names | str  | True     |
      | family_name  | str  | False    |
      | age          | int  | False    |

  Scenario: Successfully validate questionnaire responses
    Given the following questions in Questionnaire "contact details" version 1
      | name         | type | multiple |
      | given_name   | str  | False    |
      | middle_names | str  | True     |
      | family_name  | str  | False    |
      | age          | int  | False    |
    When the following questionnaire responses are provided to Questionnaire "contact details" version 1
      | question     | answer |
      | given_name   | "Jane" |
      | middle_names | ""     |
      | family_name  | "Doe"  |
      | age          | 22     |
    Then the questionnaire responses are validated successfully against Questionnaire "contact details" version 1
