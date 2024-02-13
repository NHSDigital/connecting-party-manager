Feature: Failure Scenarios

  Scenario: Failure to create a new Questionnaire due to missing name
    When the user creates a Questionnaire with the following attributes
      | name | version |
      |      | 1       |
    Then the operation is not successful
    And the error is ValidationError

  Scenario: Failure to create a new Questionnaire due to missing/invalid version
    When the user creates a Questionnaire with the following attributes
      | name                  | version |
      | example_questionnaire |         |
      | example_questionnaire | a       |
    Then the operation is not successful
    And the error is ValueError

  Scenario: Failure to add a duplicate question to a questionnaire
    Given the following questions in Questionnaire "example_questionnaire" version 1
      | name                                         | type |
      | Question with a short free-text entry answer | str  |
      | Question with an integer answer              | int  |
    When the user adds the following questions to Questionnaire "example_questionnaire" version 1
      | name                                         | type |
      | Question with a short free-text entry answer | str  |
    Then the operation is not successful
    And the error is DuplicateError

  Scenario: Failure to add new question to questionnaire as question isnt of correct format
    Given Questionnaire "example_questionnaire" version 1
    When the user adds the following Questions to Questionnaire "example_questionnaire" version 1
      | name     | type |
      |          | str  |
      | Question |      |
    Then the operation is not successful
    And the error is ValidationError

  Scenario: Invalid questionnaire response provided - answer types invalid
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
      | question                                        | answer   | answer_type |
      | Question with a short free-text entry answer    | 1        | int         |
      | Question with an integer answer                 | alpha    | str         |
      | Question with a true/flase answer               | 2.22     | float       |
      | Question with a date and time answer            | beta     | str         |
      | Question with a real number answer              | True     | bool        |
      | Question with a date answer                     | 14:30:00 | time        |
      | Question with a time answer independent of date | gamma    | str         |
    And the responses are validated against Questionnaire "example_questionnaire" version 1
    Then the operation is not successful
    And the error is ValidationError

  Scenario: Invalid questionnaire response provided - questions answered that are not in questionnaire
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
      | question                                     | answer | answer_type |
      | Question with a short free-text entry answer | alpha  | str         |
      | Question with an integer answer              | 27     | int         |
      | Question with a true/flase answer            | True   | bool        |
      | Question not in questionnaire                | name   | str         |
    And the responses are validated against Questionnaire "example_questionnaire" version 1
    Then the operation is not successful
    And the error is ValidationError
