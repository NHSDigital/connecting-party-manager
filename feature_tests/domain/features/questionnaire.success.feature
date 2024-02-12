Feature: Success Scenarios

  Scenario: Create new questionnaire
    When the user creates a Questionnaire with the following attributes
      | name                   | version |
      | example_questionnaire  | 1       |
      | example_questionnaire2 | 1       |
    Then the operation is successful
    And the result is a questionnaire with the following attributes
      | expected_name          | expected_version |
      | example_questionnaire  | 1                |
      | example_questionnaire2 | 1                |

  Scenario: Add questions to a questionnaire
    Given Questionnaire "example_questionnaire" version 1
    When the user adds the following questions to Questionnaire "example_questionnaire" version 1
      | name      | type     |
      | string    | str      |
      | integer   | int      |
      | boolean   | bool     |
      | date-time | datetime |
      | float     | float    |
      | date      | date     |
      | time      | time     |
    Then the operation is successful
    And Questionnaire "example_questionnaire" version 1 has the questions
      | name      | type     |
      | string    | str      |
      | integer   | int      |
      | boolean   | bool     |
      | date-time | datetime |
      | float     | float    |
      | date      | date     |
      | time      | time     |

  Scenario: Successfully validate questionnaire responses
    Given the following questions in Questionnaire "example_questionnaire" version 1
      | name      | type     |
      | string    | str      |
      | integer   | int      |
      | boolean   | bool     |
      | date-time | datetime |
      | float     | float    |
      | date      | date     |
      | time      | time     |
    When the following questionnaire responses are provided to Questionnaire "example_questionnaire" version 1
      | question  | answer              | answer_type |
      | string    | alpha               | str         |
      | integer   | 27                  | int         |
      | boolean   | True                | bool        |
      | date-time | 2024-02-05 14:30:00 | datetime    |
      | float     | 2.22                | float       |
      | date      | 2024-02-05          | date        |
      | time      | 14:30:00            | time        |
    And the responses are validated against Questionnaire "example_questionnaire" version 1
    Then the operation is successful

  Scenario: Successfully validate questionnaire response that does not answer all the questions in the questionnaire
    Given the following questions in Questionnaire "example_questionnaire" version 1
      | name    | type |
      | string  | str  |
      | integer | int  |
      | boolean | bool |
    When the following questionnaire responses are provided to Questionnaire "example_questionnaire" version 1
      | question | answer | answer_type |
      | string   | alpha  | str         |
    And the responses are validated against Questionnaire "example_questionnaire" version 1
    Then the operation is successful
