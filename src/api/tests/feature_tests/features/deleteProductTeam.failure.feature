Feature: Delete Product Team - failure scenarios
  These scenarios demonstrate failures to delete a CPM Product Team

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: CPM Product Team doesn't exist
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                                |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "DELETE" request with "default" headers to "ProductTeam/123"
    Then I receive a status code "404" with body
      | path             | value                                      |
      | errors.0.code    | RESOURCE_NOT_FOUND                         |
      | errors.0.message | Could not find ProductTeam for key ('123') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 101              |

  Scenario Outline: CPM Product Team has associated products
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                                |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |
    Given I note the response field "$.id" as "product_team_id"
    Given I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product" with body:
      | path | value               |
      | name | My Great CpmProduct |
    And I note the response field "$.id" as "product_id"
    When I make a "DELETE" request with "default" headers to "ProductTeam/<product_team_id>"
    Then I receive a status code "409" with body
      | path             | value                                                                                           |
      | errors.0.code    | CONFLICT                                                                                        |
      | errors.0.message | Product Team cannot be deleted as it still has associated Product Ids ['${ note(product_id) }'] |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 132              |

    Examples:
      | product_team_id                      |
      | ${ note(product_team_id) }           |
      | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |

  Scenario Outline: Cannot delete CPM Product Team with a non existent product team alias
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                                |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |
    Given I note the response field "$.id" as "product_team_id"
    When I make a "DELETE" request with "default" headers to "ProductTeam/<product_team_id>"
    Then I receive a status code "404" with body
      | path             | value                                                                       |
      | errors.0.code    | RESOURCE_NOT_FOUND                                                          |
      | errors.0.message | Could not find ProductTeam for key ('43252144-9bce-460c-8fa2-b0ab8cd74e72') |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 134              |

    Examples:
      | product_team_id                      |
      | 43252144-9bce-460c-8fa2-b0ab8cd74e72 |
