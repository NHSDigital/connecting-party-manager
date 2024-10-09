Feature: Create Device Reference Data - failure scenarios
  These scenarios demonstrate failures to create a new Device Reference Data

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Cannot create a Device Reference Data with a Device Reference Data that is missing fields (no name) and has extra param
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | ${ uuid(1) }                                                   |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ uuid(1) }/Product" with body:
      | path         | value            |
      | product_name | My Great Product |
    # ### TODO: REMOVE THESE TWO LINES AFTER PI-533
    When I make a "GET" request with "default" headers to the id in the location response header to the endpoint prefix "ProductTeam/${ uuid(1) }/Product/<id>"
    Given I note the response field "$.id" as "product_id"
    # ### TODO: UNCOMMENT THIS LINE AFTER PI-533
    # And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ uuid(1) }/Product/${ note(product_id) }/DeviceReferenceData" with body:
      | path      | value                    |
      | bad_field | My Device Reference Data |
    Then I receive a status code "400" with body
      | path             | value                                                                 |
      | errors.0.code    | MISSING_VALUE                                                         |
      | errors.0.message | CreateDeviceReferenceDataParams.name: field required                  |
      | errors.1.code    | VALIDATION_ERROR                                                      |
      | errors.1.message | CreateDeviceReferenceDataParams.bad_field: extra fields not permitted |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 220              |

  Scenario: Cannot create a Device Reference Data with a Device Reference Data with a corrupt body
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | ${ uuid(1) }                                                   |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ uuid(1) }/Product" with body:
      | path         | value            |
      | product_name | My Great Product |
    # ### TODO: REMOVE THESE TWO LINES AFTER PI-533
    When I make a "GET" request with "default" headers to the id in the location response header to the endpoint prefix "ProductTeam/${ uuid(1) }/Product/<id>"
    Given I note the response field "$.id" as "product_id"
    # ### TODO: UNCOMMENT THIS LINE AFTER PI-533
    # And I note the response field "$.id" as "product_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ uuid(1) }/Product/${ note(product_id) }/DeviceReferenceData" with body:
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

  Scenario: Cannot create a Device Reference Data with a Product Team that does not exist
    When I make a "POST" request with "default" headers to "ProductTeam/not-a-product-team/Product/not-a-product/DeviceReferenceData" with body:
      | path | value                    |
      | name | My Device Reference Data |
    Then I receive a status code "404" with body
      | path             | value                                                     |
      | errors.0.code    | RESOURCE_NOT_FOUND                                        |
      | errors.0.message | Could not find ProductTeam for key ('not-a-product-team') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 116              |

  Scenario: Cannot create a Device Reference Data with a Product that does not exist
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path                     | value                                                          |
      | resourceType             | Organization                                                   |
      | identifier.0.system      | connecting-party-manager/product-team-id                       |
      | identifier.0.value       | ${ uuid(1) }                                                   |
      | name                     | My Great Product Team                                          |
      | partOf.identifier.system | https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations |
      | partOf.identifier.value  | F5H1R                                                          |
    When I make a "POST" request with "default" headers to "ProductTeam/${ uuid(1) }/Product/not-a-product/DeviceReferenceData" with body:
      | path | value                    |
      | name | My Device Reference Data |
    Then I receive a status code "404" with body
      | path             | value                                                               |
      | errors.0.code    | RESOURCE_NOT_FOUND                                                  |
      | errors.0.message | Could not find CpmProduct for key ('${ uuid(1) }', 'not-a-product') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 150              |
