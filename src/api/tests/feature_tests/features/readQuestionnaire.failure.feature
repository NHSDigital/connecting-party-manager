Feature: Read Questionnaire - failure scenarios
  These scenarios demonstrate failure to read from the GET Questionnaire endpoint

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Read an existing Questionnaire
    When I make a "GET" request with "default" headers to "Questionnaire/does-not-exist"
    Then I receive a status code "404" with body
      | path             | value                                                   |
      | errors.0.code    | RESOURCE_NOT_FOUND                                      |
      | errors.0.message | Could not find Questionnaire for key ('does-not-exist') |
