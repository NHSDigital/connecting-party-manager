Feature: Create Device Reference Data - success scenarios
  These scenarios demonstrate successful Device Reference Data creation

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Successfully create a Device Reference Data
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
      | path | value                    |
      | name | My Device Reference Data |
    Then I receive a status code "201" with body
      | path            | value                    |
      | id              | << ignore >>             |
      | name            | My Device Reference Data |
      | product_id      | ${ note(product_id) }    |
      | product_team_id | ${ uuid(1) }             |
      | ods_code        | F5H1R                    |
      | created_on      | << ignore >>             |
      | updated_on      | << ignore >>             |
      | deleted_on      | << ignore >>             |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 279              |

# ### TODO: UNCOMMENT THIS FOR PI-503
# Given I note the response field "$.id" as "device_reference_data_id"
# When I make a "GET" request with "default" headers to "ProductTeam/${ uuid(1) }/Product/${ note(product_id) }/${ note(device_reference_data_id) }"
# Then I receive a status code "200" with body
# | path            | value                       |
# | id              | ${ note(device_reference_data_id) } |
# | name            | My Device Reference Data    |
# | product_id      | ${ note(product_id) }             |
# | product_team_id | ${ uuid(1) }                |
# | ods_code        | F5H1R                       |
# | created_on      | << ignore >>     |
# | updated_on      | << ignore >>     |
# | deleted_on      | << ignore >>     |
# And the response headers contain:
# | name           | value            |
# | Content-Type   | application/json |
# | Content-Length | 279              |
