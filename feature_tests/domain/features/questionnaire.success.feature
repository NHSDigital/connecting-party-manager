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
      | name                                            | type     |
      | Question with a short free-text entry answer    | str      |
      | Question with an integer answer                 | int      |
      | Question with a true/flase answer               | bool     |
      | Question with a date and time answer            | datetime |
      | Question with a real number answer              | float    |
      | Question with a date answer                     | date     |
      | Question with a time answer independent of date | time     |
    Then the operation is successful
    And Questionnaire "example_questionnaire" version 1 has the questions
      | name                                            | type     |
      | Question with a short free-text entry answer    | str      |
      | Question with an integer answer                 | int      |
      | Question with a true/flase answer               | bool     |
      | Question with a date and time answer            | datetime |
      | Question with a real number answer              | float    |
      | Question with a date answer                     | date     |
      | Question with a time answer independent of date | time     |

  Scenario: Successfully validate questionnaire responses
    Given the following questions in Questionnaire "example_questionnaire" version 1
      | name                                            | type     |
      | Question with a short free-text entry answer    | str      |
      | Question with an integer answer                 | int      |
      | Question with a true/flase answer               | bool     |
      | Question with a date and time answer            | datetime |
      | Question with a real number answer              | float    |
      | Question with a date answer                     | date     |
      | Question with a time answer independent of date | time     |
    When the following questionnaire responses are provided to Questionnaire "example_questionnaire" version 1
      | question                                        | answer              | answer_type |
      | Question with a short free-text entry answer    | alpha               | str         |
      | Question with an integer answer                 | 27                  | int         |
      | Question with a true/flase answer               | True                | bool        |
      | Question with a date and time answer            | 2024-02-05 14:30:00 | datetime    |
      | Question with a real number answer              | 2.22                | float       |
      | Question with a date answer                     | 2024-02-05          | date        |
      | Question with a time answer independent of date | 14:30:00            | time        |
    And the responses are validated against Questionnaire "example_questionnaire" version 1
    Then the operation is successful

  Scenario: Successfully validate questionnaire response that does not answer all the questions in the questionnaire
    Given the following questions in Questionnaire "example_questionnaire" version 1
      | name                                         | type |
      | Question with a short free-text entry answer | str  |
      | Question with an integer answer              | int  |
      | Question with a true/flase answer            | bool |
    When the following questionnaire responses are provided to Questionnaire "example_questionnaire" version 1
      | question                                     | answer | answer_type |
      | Question with a short free-text entry answer | alpha  | str         |
    And the responses are validated against Questionnaire "example_questionnaire" version 1
    Then the operation is successful