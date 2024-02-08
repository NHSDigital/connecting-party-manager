Feature: Failure Scenarios

  Scenario: Failure to create a new questionnaire due to missing name
    When I try to create a Questionnaire without a name attribute
      | name | version |
      |      | 1       |
    Then the result for missing name is error ValidationError

  Scenario: Failure to create a new questionnaire due to missing version
    When I try to create a Questionnaire without a version attribute
      | name                  | version |
      | example_questionnaire |         |
    Then the result for missing version is error ValidationError

  Scenario: Failure to add new question to questionnaire as question isn't of correct format
    Given Questionnaire "example_questionnaire" version 1
    When I try to add an invalid question to Questionnaire "example_questionnaire" version 1
      | name |
      |      |
    Then the result is TypeError for missing question name

  Scenario: Invalid questionnaire response provided
    Given the following questions in Questionnaire "example_questionnaire" version 1
      | name         | type | multiple |
      | given_name   | str  | False    |
      | middle_names | str  | True     |
      | family_name  | str  | False    |
    When the following questionnaire responses are provided to Questionnaire "example_questionnaire" version 1
      | question     | answer |
      | given_name   | 007    |
      | middle_names |        |
      | family_name  | Doe    |
    Then the questionnaire responses fail validation against the Questionnaire "example_questionnaire" version 1

  Scenario: Failure to add a duplicate question to a questionnaire
    Given the following questions in Questionnaire "example_questionnaire" version 1
      | name         | type | multiple |
      | given_name   | str  | False    |
      | middle_names | str  | True     |
      | family_name  | str  | False    |
      | mobile       | int  | False    |
    When I try to add the following duplicate questions to Questionnaire "example_questionnaire" version 1
      | name       | type   | multiple |
      | given_name | STRING | False    |
    Then the result for duplicate questions is error DuplicateError
