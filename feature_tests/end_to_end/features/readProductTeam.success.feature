Feature: Read Product Team - success scenarios

  Background:
    Given "default" request headers:
      | name             | value      |
      | version          | 1          |
      | x-correlation-id | ${guid: 1} |
      | x-version-id     | ${guid: 1} |
      | Authorization    | letmein    |

  Scenario: Read an existing ProductTeam
    Given I have already made a "POST" request with "default" headers to "Organization" with body:
      | path                    | value                                |
      | resourceType            | Organization                         |
      | id                      | f9518c12-6c83-4544-97db-d9dd1d64da97 |
      | name                    | My Great Product Team                |
      | partOf.identifier.id    | F5H1R                                |
      | partOf.identifier.value | ROYAL DERBY HOSPITAL UTC             |
      | contact.0.name.text     | My Company Name                      |
      | telecom.0.system        | email                                |
      | telecom.0.value         | admin@mycompanyname.com              |
    When I make a "GET" request with "default" headers to "Organization/f9518c12-6c83-4544-97db-d9dd1d64da97"
    Then I receive a status code "200" with body
      | path                    | value                                |
      | resourceType            | Organization                         |
      | id                      | f9518c12-6c83-4544-97db-d9dd1d64da97 |
      | name                    | My Great Product Team                |
      | partOf.identifier.id    | F5H1R                                |
      | partOf.identifier.value | ROYAL DERBY HOSPITAL UTC             |
      | contact.0.name.text     | My Company Name                      |
      | telecom.0.system        | email                                |
      | telecom.0.value         | admin@mycompanyname.com              |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 449              |
