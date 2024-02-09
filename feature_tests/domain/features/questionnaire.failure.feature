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
      | name        | type |
      | given_name  | str  |
      | family_name | str  |
      | mobile      | int  |
    When the user adds the following questions to Questionnaire "example_questionnaire" version 1
      | name       | type |
      | given_name | str  |
    Then the operation is not successful
    And the error is DuplicateError

  Scenario: Failure to add new question to questionnaire as question isnt of correct format
    Given Questionnaire "example_questionnaire" version 1
    When the user adds the following Questions to Questionnaire "example_questionnaire" version 1
      | name     | type |
      |          | str  |
      | question |      |
    Then the operation is not successful
    And the error is ValidationError

  Scenario: Invalid questionnaire response provided
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
      | question  | answer   | answer_type |
      | string    | 1        | int         |
      | integer   | alpha    | str         |
      | boolean   | 2.22     | float       |
      | date-time | beta     | str         |
      | float     | True     | bool        |
      | date      | 14:30:00 | time        |
      | time      | gamma    | str         |
    And the responses are validated against Questionnaire "example_questionnaire" version 1
    Then the operation is not successful
    And the error is ValidationError
