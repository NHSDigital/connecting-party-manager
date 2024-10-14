Feature: Create Product Team - failure scenarios
  These scenarios demonstrate failures to create a new Product Team (FHIR "Organization")

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Cannot create a ProductTeam that already exists
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | ${ uuid(1) }                                                   |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | ${ uuid(1) }                                                   |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    Then I receive a status code "400" with body
      | path             | value               |
      | errors.0.code    | VALIDATION_ERROR    |
      | errors.0.message | Item already exists |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 76               |

  Scenario: Cannot create a ProductTeam with an Organization that is missing fields (no partOf.identifier.value)
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | ${ uuid(1) }                                                   |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
    Then I receive a status code "400" with body
      | path             | value                                                |
      | errors.0.code    | MISSING_VALUE                                        |
      | errors.0.message | Organization.partOf.identifier.value: field required |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 106              |

  Scenario: Cannot create a ProductTeam with invalid FHIR
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      | path                | value                                    |
      | resourceType        | invalid_type                             |
      | identifier.0.system | connecting-party-manager/product-team-id |
      | identifier.0.value  | ${ uuid(1) }                             |
      | name                | My Great Product Team                    |
      | partOf.identifier   | invalid_identifier                       |
    Then I receive a status code "400" with body
      | path             | value                                                                  |
      | errors.0.code    | VALIDATION_ERROR                                                       |
      | errors.0.message | Organization.resourceType: unexpected value; permitted: 'Organization' |
      | errors.1.code    | VALIDATION_ERROR                                                       |
      | errors.1.message | Organization.partOf.identifier: value is not a valid dict              |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 229              |

  Scenario: Cannot create a ProductTeam with an invalid ID
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | invalid_id                                                     |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    Then I receive a status code "400" with body
      | path             | value                                                      |
      | errors.0.code    | VALIDATION_ERROR                                           |
      | errors.0.message | Organization.identifier.0.value: value is not a valid uuid |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 115              |

  Scenario: Cannot create a ProductTeam with a syntactically invalid ODS Code
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | ${ uuid(1) }                                                   |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | invalid_ods_code                                               |
    Then I receive a status code "400" with body
      | path             | value                                                                                    |
      | errors.0.code    | VALIDATION_ERROR                                                                         |
      | errors.0.message | Organization.partOf.identifier.value: string does not match regex "^([a-zA-Z0-9]{1,9})$" |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 147              |

  Scenario: Cannot create a ProductTeam with an ODS code that is syntatically correct but doesn't exist
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | ${ uuid(1) }                                                   |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H11                                                          |
    Then I receive a status code "422" with body
      | path             | value                                                                                                      |
      | errors.0.code    | UNPROCESSABLE_ENTITY                                                                                       |
      | errors.0.message | Invalid ODS Code: could not resolve 'https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/F5H11' |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 167              |

  Scenario: Cannot create a ProductTeam with corrupt body
    When I make a "POST" request with "default" headers to "ProductTeam" with body:
      """
      {"invalid_array": [}
      """
    Then I receive a status code "400" with body
      | path             | value                                                      |
      | errors.0.code    | VALIDATION_ERROR                                           |
      | errors.0.message | Invalid JSON body was provided: line 1 column 20 (char 19) |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 115              |
