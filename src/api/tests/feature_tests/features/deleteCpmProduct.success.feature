Feature: Delete CPM Product - success scenarios
  These scenarios demonstrate success in deleting an CPM Product

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario Outline: Successfully delete a CPM Product
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                                |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |
    Given I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "DELETE" request with "default" headers to "ProductTeam/<product_team_id>/Product/${ note(product_id) }"
    Then I receive a status code "200" with body
      | path    | value                                   |
      | code    | RESOURCE_DELETED                        |
      | message | ${ note(product_id) } has been deleted. |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 70               |

    Examples:
      | product_team_id                      |
      | ${ note(product_team_id) }           |
      | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |

  Scenario Outline: Successfully delete a CPM Product and try to read it.
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                                |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/<product_team_id>/Product" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I have already made a "DELETE" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/<product_id>"
    When I make a "GET" request with "default" headers to "Product/<product_id>"
    Then I receive a status code "404" with body
      | path             | value                                              |
      | errors.0.code    | RESOURCE_NOT_FOUND                                 |
      | errors.0.message | Could not find CpmProduct for key ('<product_id>') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 106              |

    Examples:
      | product_team_id                      | product_id            |
      | ${ note(product_team_id) }           | ${ note(product_id) } |
      | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 | ${ note(product_id) } |
