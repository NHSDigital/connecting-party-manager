Feature: Search SDS Endpoints - failure scenarios
  These scenarios demonstrate failure SDS Endpoints searching

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Unsuccessfully search SDS Endpoints without query params
    When I make a "GET" request with "default" headers to "searchSdsEndpoint"
    Then I receive a status code "400" with body
      | path             | value                                                    |
      | errors.0.code    | MISSING_VALUE                                            |
      | errors.0.message | SearchSDSDeviceQueryParams.nhs_id_code: field required   |
      | errors.1.code    | MISSING_VALUE                                            |
      | errors.1.message | SearchSDSDeviceQueryParams.nhs_as_svc_ia: field required |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 206              |

  Scenario: Unsuccessfully search an SDS Device without nhs_id_code query param
    When I make a "GET" request with "default" headers to "searchSdsDevice?nhs_as_svc_ia=Foo"
    Then I receive a status code "400" with body
      | path             | value                                                  |
      | errors.0.code    | MISSING_VALUE                                          |
      | errors.0.message | SearchSDSDeviceQueryParams.nhs_id_code: field required |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 108              |

  Scenario: Unsuccessfully search an SDS Device without nhs_as_svc_ia query param
    When I make a "GET" request with "default" headers to "searchSdsDevice?nhs_id_code=Foo"
    Then I receive a status code "400" with body
      | path             | value                                                    |
      | errors.0.code    | MISSING_VALUE                                            |
      | errors.0.message | SearchSDSDeviceQueryParams.nhs_as_svc_ia: field required |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 110              |

  Scenario: Unsuccessfully search an SDS Device with unknown query param
    When I make a "GET" request with "default" headers to "searchSdsDevice?nhs_id_code=Foo&nhs_as_svc_ia=Bar&foo=bar"
    Then I receive a status code "400" with body
      | path             | value                                                      |
      | errors.0.code    | VALIDATION_ERROR                                           |
      | errors.0.message | SearchSDSDeviceQueryParams.foo: extra fields not permitted |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 115              |
