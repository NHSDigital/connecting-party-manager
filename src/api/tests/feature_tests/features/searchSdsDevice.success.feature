Feature: Search SDS Device - success scenarios
  These scenarios demonstrate successful SDS Device searching

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Successfully search an SDS Device with empty result
    When I make a "GET" request with "default" headers to "searchSdsDevice?nhs_id_code=foo&nhs_as_svc_ia=bar"
    Then I receive a status code "200" with an empty body
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 2                |

  Scenario: Successfully search an SDS Device with one result
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I note the response field "$.keys.0.key_type" as "party_key_type"
    And I note the response field "$.keys.0.key_value" as "party_key"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }/dev/DeviceReferenceData/MhsMessageSet" with body:
      | path                                                    | value                          |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS SN | urn:nhs:names:services:ers     |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS IN | READ_PRACTITIONER_ROLE_R4_V001 |
    And I note the response field "$.id" as "mhs_message_set_drd_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }/dev/Device/MessageHandlingSystem" with body:
      | path                                                              | value               |
      | questionnaire_responses.spine_mhs.0.MHS FQDN                      | mhs.example.com     |
      | questionnaire_responses.spine_mhs.0.MHS Service Description       | Example Description |
      | questionnaire_responses.spine_mhs.0.MHS Manufacturer Organisation | F5H1R               |
      | questionnaire_responses.spine_mhs.0.Product Name                  | Product Name        |
      | questionnaire_responses.spine_mhs.0.Product Version               | 1                   |
      | questionnaire_responses.spine_mhs.0.Approver URP                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.DNS Approver                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.Requestor URP                 | UI provided         |
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }/dev/DeviceReferenceData/AccreditedSystemsAdditionalInteractions" with body:
      | path                                                                      | value                                                     |
      | questionnaire_responses.spine_as_additional_interactions.0.Interaction ID | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V002 |
    And I note the response field "$.id" as "as_message_set_drd_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }/dev/Device/AccreditedSystem" with body:
      | path                                               | value             |
      | questionnaire_responses.spine_as.0.ODS Code        | F5H1R             |
      | questionnaire_responses.spine_as.0.Product Name    | My SPINE Product  |
      | questionnaire_responses.spine_as.0.Product Version | 2000.01           |
      | questionnaire_responses.spine_as.0.Requestor URP   | the-requestor-urp |
      | questionnaire_responses.spine_as.0.Approver URP    | the-approver-urp  |
    Then I receive a status code "201" with body
      | path                                                                    | value                                         |
      | id                                                                      | << ignore >>                                  |
      | name                                                                    | F5H1R-850000/200000100000 - Accredited System |
      | status                                                                  | active                                        |
      | product_id                                                              | ${ note(product_id) }                         |
      | product_team_id                                                         | ${ note(product_team_id) }                    |
      | ods_code                                                                | F5H1R                                         |
      | environment                                                             | dev                                           |
      | keys.0.key_type                                                         | accredited_system_id                          |
      | keys.0.key_value                                                        | 200000100000                                  |
      | created_on                                                              | << ignore >>                                  |
      | updated_on                                                              | << ignore >>                                  |
      | deleted_on                                                              | << ignore >>                                  |
      | questionnaire_responses.spine_as/1.0.id                                 | << ignore >>                                  |
      | questionnaire_responses.spine_as/1.0.questionnaire_name                 | spine_as                                      |
      | questionnaire_responses.spine_as/1.0.questionnaire_version              | 1                                             |
      | questionnaire_responses.spine_as/1.0.data.ODS Code                      | F5H1R                                         |
      | questionnaire_responses.spine_as/1.0.data.Product Name                  | My SPINE Product                              |
      | questionnaire_responses.spine_as/1.0.data.Product Version               | 2000.01                                       |
      | questionnaire_responses.spine_as/1.0.data.Requestor URP                 | the-requestor-urp                             |
      | questionnaire_responses.spine_as/1.0.data.Approver URP                  | the-approver-urp                              |
      | questionnaire_responses.spine_as/1.0.data.MHS Manufacturer Organisation | F5H1R                                         |
      | questionnaire_responses.spine_as/1.0.data.MHS Party Key                 | ${ note(party_key) }                          |
      | questionnaire_responses.spine_as/1.0.data.Product Key                   | ${ note(product_id) }                         |
      | questionnaire_responses.spine_as/1.0.data.ASID                          | 200000100000                                  |
      | questionnaire_responses.spine_as/1.0.data.Date Approved                 | << ignore >>                                  |
      | questionnaire_responses.spine_as/1.0.data.Date Requested                | << ignore >>                                  |
      | questionnaire_responses.spine_as/1.0.data.Client ODS Codes.0            | F5H1R                                         |
      | questionnaire_responses.spine_as/1.0.data.Temp UID                      | null                                          |
      | questionnaire_responses.spine_as/1.0.created_on                         | << ignore >>                                  |
      | device_reference_data                                                   | << ignore >>                                  |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 1267             |
    And I note the response field "$.id" as "device_id"
    When I make a "GET" request with "default" headers to "searchSdsDevice?nhs_id_code=F5H1R&nhs_as_svc_ia=urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V002"
    Then I receive a status code "200" with an empty body
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 2                |

  Scenario: Successfully search an SDS Device with one result with manufacturer_org in query param
    Given I have already made a "POST" request with "default" headers to "ProductTeamEpr" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I note the response field "$.keys.0.key_type" as "party_key_type"
    And I note the response field "$.keys.0.key_value" as "party_key"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }/dev/DeviceReferenceData/MhsMessageSet" with body:
      | path                                                    | value                          |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS SN | urn:nhs:names:services:ers     |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS IN | READ_PRACTITIONER_ROLE_R4_V001 |
    And I note the response field "$.id" as "mhs_message_set_drd_id"
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }/dev/Device/MessageHandlingSystem" with body:
      | path                                                              | value               |
      | questionnaire_responses.spine_mhs.0.MHS FQDN                      | mhs.example.com     |
      | questionnaire_responses.spine_mhs.0.MHS Service Description       | Example Description |
      | questionnaire_responses.spine_mhs.0.MHS Manufacturer Organisation | F5H1R               |
      | questionnaire_responses.spine_mhs.0.Product Name                  | Product Name        |
      | questionnaire_responses.spine_mhs.0.Product Version               | 1                   |
      | questionnaire_responses.spine_mhs.0.Approver URP                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.DNS Approver                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.Requestor URP                 | UI provided         |
    And I have already made a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }/dev/DeviceReferenceData/AccreditedSystemsAdditionalInteractions" with body:
      | path                                                                      | value                                                     |
      | questionnaire_responses.spine_as_additional_interactions.0.Interaction ID | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V002 |
    And I note the response field "$.id" as "as_message_set_drd_id"
    When I make a "POST" request with "default" headers to "ProductTeamEpr/${ note(product_team_id) }/ProductEpr/${ note(product_id) }/dev/Device/AccreditedSystem" with body:
      | path                                               | value             |
      | questionnaire_responses.spine_as.0.ODS Code        | F5H1R             |
      | questionnaire_responses.spine_as.0.Product Name    | My SPINE Product  |
      | questionnaire_responses.spine_as.0.Product Version | 2000.01           |
      | questionnaire_responses.spine_as.0.Requestor URP   | the-requestor-urp |
      | questionnaire_responses.spine_as.0.Approver URP    | the-approver-urp  |
    Then I receive a status code "201" with body
      | path                                                                    | value                                         |
      | id                                                                      | << ignore >>                                  |
      | name                                                                    | F5H1R-850000/200000100000 - Accredited System |
      | status                                                                  | active                                        |
      | product_id                                                              | ${ note(product_id) }                         |
      | product_team_id                                                         | ${ note(product_team_id) }                    |
      | ods_code                                                                | F5H1R                                         |
      | environment                                                             | dev                                           |
      | keys.0.key_type                                                         | accredited_system_id                          |
      | keys.0.key_value                                                        | 200000100000                                  |
      | created_on                                                              | << ignore >>                                  |
      | updated_on                                                              | << ignore >>                                  |
      | deleted_on                                                              | << ignore >>                                  |
      | questionnaire_responses.spine_as/1.0.id                                 | << ignore >>                                  |
      | questionnaire_responses.spine_as/1.0.questionnaire_name                 | spine_as                                      |
      | questionnaire_responses.spine_as/1.0.questionnaire_version              | 1                                             |
      | questionnaire_responses.spine_as/1.0.data.ODS Code                      | F5H1R                                         |
      | questionnaire_responses.spine_as/1.0.data.Product Name                  | My SPINE Product                              |
      | questionnaire_responses.spine_as/1.0.data.Product Version               | 2000.01                                       |
      | questionnaire_responses.spine_as/1.0.data.Requestor URP                 | the-requestor-urp                             |
      | questionnaire_responses.spine_as/1.0.data.Approver URP                  | the-approver-urp                              |
      | questionnaire_responses.spine_as/1.0.data.MHS Manufacturer Organisation | F5H1R                                         |
      | questionnaire_responses.spine_as/1.0.data.MHS Party Key                 | ${ note(party_key) }                          |
      | questionnaire_responses.spine_as/1.0.data.Product Key                   | ${ note(product_id) }                         |
      | questionnaire_responses.spine_as/1.0.data.ASID                          | 200000100000                                  |
      | questionnaire_responses.spine_as/1.0.data.Date Approved                 | << ignore >>                                  |
      | questionnaire_responses.spine_as/1.0.data.Date Requested                | << ignore >>                                  |
      | questionnaire_responses.spine_as/1.0.data.Client ODS Codes.0            | F5H1R                                         |
      | questionnaire_responses.spine_as/1.0.data.Temp UID                      | null                                          |
      | questionnaire_responses.spine_as/1.0.created_on                         | << ignore >>                                  |
      | device_reference_data                                                   | << ignore >>                                  |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 1267             |
    And I note the response field "$.id" as "device_id"
    When I make a "GET" request with "default" headers to "searchSdsDevice?nhs_id_code=F5H1R&nhs_as_svc_ia=urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V002&nhs_mhs_manufacturer_org=F5H1R"
    Then I receive a status code "200" with an empty body
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 2                |
