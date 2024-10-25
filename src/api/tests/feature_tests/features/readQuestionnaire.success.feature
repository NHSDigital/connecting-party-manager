Feature: Read Questionnaire - success scenarios
  These scenarios demonstrate successful reads from the GET Questionnaire endpoint

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario Outline: Read an existing Questionnaire
    When I make a "GET" request with "default" headers to "Questionnaire/<questionnaire_name>"
    Then I receive a status code "200" with body
      | path      | value                |
      | name      | <questionnaire_name> |
      | version   | 1                    |
      | questions | << ignore >>         |

    Examples:
      | questionnaire_name |
      | spine_endpoint     |
      | spine_device       |
      | spine_ENDpoint     |
      | SPINE_DEVICE       |
