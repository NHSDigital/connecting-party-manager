Feature: Delete Product Team - success scenarios
  These scenarios demonstrate success in deleting an CPM Product Team

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario Outline: Successfully delete a CPM Product Team
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                                |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |
    And I note the response field "$.id" as "product_team_id"
    When I make a "DELETE" request with "default" headers to "ProductTeam/<product_team_id>"
    Then I receive a status code "200" with body
      | path    | value                                        |
      | code    | RESOURCE_DELETED                             |
      | message | ${ note(product_team_id) } has been deleted. |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 97               |

    Examples:
      | product_team_id                      |
      | ${ note(product_team_id) }           |
      | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |

  Scenario Outline: Successfully delete a CPM Product Team and try to read it.
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                                |
      | name             | My Great Product Team                |
      | ods_code         | F5H1R                                |
      | keys.0.key_type  | product_team_id                      |
      | keys.0.key_value | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |
      | keys.1.key_type  | product_team_id                      |
      | keys.1.key_value | 43252144-9bce-460c-8fa2-b0ab8cd74e72 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "DELETE" request with "default" headers to "ProductTeam/<product_team_id>"
    When I make a "GET" request with "default" headers to "ProductTeam/<product_team_id>"
    Then I receive a status code "404" with body
      | path             | value                                                    |
      | errors.0.code    | RESOURCE_NOT_FOUND                                       |
      | errors.0.message | Could not find ProductTeam for key ('<product_team_id>') |
    And the response headers contain:
      | name         | value            |
      | Content-Type | application/json |

    Examples:
      | product_team_id                      |
      | ${ note(product_team_id) }           |
      | 0a78ee8f-5bcf-4db1-9341-ef1d67248715 |
      | 43252144-9bce-460c-8fa2-b0ab8cd74e72 |
