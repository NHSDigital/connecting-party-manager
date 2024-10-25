Feature: Read Questionnaire - failure scenarios
  These scenarios demonstrate failure to read from the GET Questionnaire endpoint

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario Outline: Read an non-existing Questionnaire, do not fail early due to bad characters
    When I make a "GET" request with "default" headers to "Questionnaire/<questionnaire_name>"
    Then I receive a status code "404" with body
      | path             | value                                                         |
      | errors.0.code    | RESOURCE_NOT_FOUND                                            |
      | errors.0.message | Could not find Questionnaire for key ('<questionnaire_name>') |

    Examples:
      | questionnaire_name |
      | isMixedCase        |

  Scenario Outline: Read an non-existing Questionnaire, but fail early due to bad characters
    When I make a "GET" request with "default" headers to "Questionnaire/<questionnaire_name>"
    Then I receive a status code "400" with body
      | path             | value                                                                                                |
      | errors.0.code    | VALIDATION_ERROR                                                                                     |
      | errors.0.message | QuestionnairePathParams.questionnaire_id: string does not match regex "^[a-zA-Z0-9 _]*${ dollar() }" |

    Examples:
      | questionnaire_name   |
      | has-hyphen-in-it     |
      | has+other+characters |
