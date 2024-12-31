Feature: Create AS Device - success scenarios
  These scenarios demonstrate successful AS Device creation

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario: Successfully create an AS Device
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I note the response field "$.keys.0.key_type" as "party_key_type"
    And I note the response field "$.keys.0.key_value" as "party_key"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/MhsMessageSet" with body:
      | path                                                    | value                          |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS SN | urn:nhs:names:services:ers     |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS IN | READ_PRACTITIONER_ROLE_R4_V001 |
    And I note the response field "$.id" as "mhs_message_set_drd_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/MessageHandlingSystem" with body:
      | path                                                              | value               |
      | questionnaire_responses.spine_mhs.0.MHS FQDN                      | mhs.example.com     |
      | questionnaire_responses.spine_mhs.0.MHS Service Description       | Example Description |
      | questionnaire_responses.spine_mhs.0.MHS Manufacturer Organisation | F5H1R               |
      | questionnaire_responses.spine_mhs.0.Product Name                  | Product Name        |
      | questionnaire_responses.spine_mhs.0.Product Version               | 1                   |
      | questionnaire_responses.spine_mhs.0.Approver URP                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.DNS Approver                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.Requestor URP                 | UI provided         |
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/AccreditedSystemsAdditionalInteractions" with body:
      | path                                                                      | value                                                     |
      | questionnaire_responses.spine_as_additional_interactions.0.Interaction ID | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V002 |
    And I note the response field "$.id" as "as_message_set_drd_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/AccreditedSystem" with body:
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
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/${ note(device_id) }"
    Then I receive a status code "200" with body
      | path                    | value                                         |
      | id                      | ${ note(device_id) }                          |
      | name                    | F5H1R-850000/200000100000 - Accredited System |
      | status                  | active                                        |
      | environment             | dev                                           |
      | product_id              | ${ note(product_id) }                         |
      | product_team_id         | ${ note(product_team_id) }                    |
      | ods_code                | F5H1R                                         |
      | created_on              | << ignore >>                                  |
      | updated_on              | << ignore >>                                  |
      | deleted_on              | << ignore >>                                  |
      | keys.0.key_type         | accredited_system_id                          |
      | keys.0.key_value        | 200000100000                                  |
      | tags.0.0.0              | ${ note(party_key_type) }                     |
      | tags.0.0.1              | ${ lower_note(party_key) }                    |
      | questionnaire_responses | << ignore >>                                  |
      | device_reference_data   | << ignore >>                                  |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 1920             |

  Scenario: Successfully create a AS Device with MHSMessageSet and ASAdditionalInteractions containing no questionnaire responses
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I note the response field "$.keys.0.key_type" as "party_key_type"
    And I note the response field "$.keys.0.key_value" as "party_key"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/MhsMessageSet"
    And I note the response field "$.id" as "mhs_message_set_drd_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/AccreditedSystemsAdditionalInteractions"
    And I note the response field "$.id" as "as_message_set_drd_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/AccreditedSystem" with body:
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
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/${ note(device_id) }"
    Then I receive a status code "200" with body
      | path                    | value                                         |
      | id                      | ${ note(device_id) }                          |
      | name                    | F5H1R-850000/200000100000 - Accredited System |
      | status                  | active                                        |
      | environment             | dev                                           |
      | product_id              | ${ note(product_id) }                         |
      | product_team_id         | ${ note(product_team_id) }                    |
      | ods_code                | F5H1R                                         |
      | created_on              | << ignore >>                                  |
      | updated_on              | << ignore >>                                  |
      | deleted_on              | << ignore >>                                  |
      | keys.0.key_type         | accredited_system_id                          |
      | keys.0.key_value        | 200000100000                                  |
      | tags.0.0.0              | ${ note(party_key_type) }                     |
      | tags.0.0.1              | ${ lower_note(party_key) }                    |
      | questionnaire_responses | << ignore >>                                  |
      | device_reference_data   | << ignore >>                                  |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 1310             |

  Scenario: Successfully create multiple AS Devices
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I note the response field "$.keys.0.key_type" as "party_key_type"
    And I note the response field "$.keys.0.key_value" as "party_key"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/MhsMessageSet" with body:
      | path                                                    | value                          |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS SN | urn:nhs:names:services:ers     |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS IN | READ_PRACTITIONER_ROLE_R4_V001 |
    And I note the response field "$.id" as "mhs_message_set_drd_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/MessageHandlingSystem" with body:
      | path                                                              | value               |
      | questionnaire_responses.spine_mhs.0.MHS FQDN                      | mhs.example.com     |
      | questionnaire_responses.spine_mhs.0.MHS Service Description       | Example Description |
      | questionnaire_responses.spine_mhs.0.MHS Manufacturer Organisation | F5H1R               |
      | questionnaire_responses.spine_mhs.0.Product Name                  | Product Name        |
      | questionnaire_responses.spine_mhs.0.Product Version               | 1                   |
      | questionnaire_responses.spine_mhs.0.Approver URP                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.DNS Approver                  | UI provided         |
      | questionnaire_responses.spine_mhs.0.Requestor URP                 | UI provided         |
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/AccreditedSystemsAdditionalInteractions" with body:
      | path                                                                      | value                                                     |
      | questionnaire_responses.spine_as_additional_interactions.0.Interaction ID | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V002 |
    And I note the response field "$.id" as "as_message_set_drd_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/AccreditedSystem" with body:
      | path                                               | value             |
      | questionnaire_responses.spine_as.0.ODS Code        | F5H1R             |
      | questionnaire_responses.spine_as.0.Product Name    | My SPINE Product  |
      | questionnaire_responses.spine_as.0.Product Version | 2000.01           |
      | questionnaire_responses.spine_as.0.Requestor URP   | the-requestor-urp |
      | questionnaire_responses.spine_as.0.Approver URP    | the-approver-urp  |
    And I note the response field "$.id" as "device_id"
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
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/AccreditedSystem" with body:
      | path                                               | value             |
      | questionnaire_responses.spine_as.0.ODS Code        | F5H1R             |
      | questionnaire_responses.spine_as.0.Product Name    | My SPINE Product  |
      | questionnaire_responses.spine_as.0.Product Version | 2000.01           |
      | questionnaire_responses.spine_as.0.Requestor URP   | the-requestor-urp |
      | questionnaire_responses.spine_as.0.Approver URP    | the-approver-urp  |
    And I note the response field "$.id" as "device_id_2"
    Then I receive a status code "201" with body
      | path                                                                    | value                                         |
      | id                                                                      | << ignore >>                                  |
      | name                                                                    | F5H1R-850000/200000100001 - Accredited System |
      | status                                                                  | active                                        |
      | product_id                                                              | ${ note(product_id) }                         |
      | product_team_id                                                         | ${ note(product_team_id) }                    |
      | ods_code                                                                | F5H1R                                         |
      | environment                                                             | dev                                           |
      | keys.0.key_type                                                         | accredited_system_id                          |
      | keys.0.key_value                                                        | 200000100001                                  |
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
      | questionnaire_responses.spine_as/1.0.data.ASID                          | 200000100001                                  |
      | questionnaire_responses.spine_as/1.0.data.Date Approved                 | << ignore >>                                  |
      | questionnaire_responses.spine_as/1.0.data.Date Requested                | << ignore >>                                  |
      | questionnaire_responses.spine_as/1.0.data.Client ODS Codes.0            | F5H1R                                         |
      | questionnaire_responses.spine_as/1.0.data.Temp UID                      | null                                          |
      | questionnaire_responses.spine_as/1.0.created_on                         | << ignore >>                                  |
      | device_reference_data                                                   | << ignore >>                                  |
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/${ note(device_id) }"
    Then I receive a status code "200" with body
      | path                    | value                                         |
      | id                      | ${ note(device_id) }                          |
      | name                    | F5H1R-850000/200000100000 - Accredited System |
      | environment             | dev                                           |
      | status                  | active                                        |
      | product_id              | ${ note(product_id) }                         |
      | product_team_id         | ${ note(product_team_id) }                    |
      | ods_code                | F5H1R                                         |
      | created_on              | << ignore >>                                  |
      | updated_on              | << ignore >>                                  |
      | deleted_on              | << ignore >>                                  |
      | keys.0.key_type         | accredited_system_id                          |
      | keys.0.key_value        | 200000100000                                  |
      | tags.0.0.0              | ${ note(party_key_type) }                     |
      | tags.0.0.1              | ${ lower_note(party_key) }                    |
      | questionnaire_responses | << ignore >>                                  |
      | device_reference_data   | << ignore >>                                  |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 1920             |
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/Device/${ note(device_id_2) }"
    Then I receive a status code "200" with body
      | path                    | value                                         |
      | id                      | ${ note(device_id_2) }                        |
      | name                    | F5H1R-850000/200000100001 - Accredited System |
      | status                  | active                                        |
      | product_id              | ${ note(product_id) }                         |
      | product_team_id         | ${ note(product_team_id) }                    |
      | ods_code                | F5H1R                                         |
      | environment             | dev                                           |
      | created_on              | << ignore >>                                  |
      | updated_on              | << ignore >>                                  |
      | deleted_on              | << ignore >>                                  |
      | keys.0.key_type         | accredited_system_id                          |
      | keys.0.key_value        | 200000100001                                  |
      | tags.0.0.0              | ${ note(party_key_type) }                     |
      | tags.0.0.1              | ${ lower_note(party_key) }                    |
      | questionnaire_responses | << ignore >>                                  |
      | device_reference_data   | << ignore >>                                  |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 1920             |
