Feature: Search Device Reference Data - success scenarios
  These scenarios demonstrate successful Device Reference Data Search

  Background:
    Given "default" request headers:
      | name          | value   |
      | version       | 1       |
      | Authorization | letmein |

  Scenario Outline: Successfully search Device Reference Data with no results
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/<product_team_id>/Product" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    When I make a "GET" request with "default" headers to "ProductTeam/<product_team_id>/Product/<product_id>/dev/DeviceReferenceData"
    Then I receive a status code "200" with body
      | path    | value |
      | results | []    |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 15               |

    Examples:
      | product_team_id            | product_id            |
      | ${ note(product_team_id) } | ${ note(product_id) } |
      | FOOBAR                     | ${ note(product_id) } |

  Scenario Outline: Successfully search more than one Device Reference Data
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/<product_team_id>/Product" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/<product_team_id>/Product/<product_id>/dev/DeviceReferenceData" with body:
      | path | value                      |
      | name | My Device Reference Data 1 |
    And I note the response field "$.id" as "device_reference_data_id_1"
    And I have already made a "POST" request with "default" headers to "ProductTeam/<product_team_id>/Product/<product_id>/dev/DeviceReferenceData" with body:
      | path | value                      |
      | name | My Device Reference Data 2 |
    And I note the response field "$.id" as "device_reference_data_id_2"
    And I have already made a "POST" request with "default" headers to "ProductTeam/<product_team_id>/Product/<product_id>/dev/DeviceReferenceData" with body:
      | path | value                      |
      | name | My Device Reference Data 3 |
    And I note the response field "$.id" as "device_reference_data_id_3"
    When I make a "GET" request with "default" headers to "ProductTeam/<product_team_id>/Product/<product_id>/dev/DeviceReferenceData"
    Then I receive a status code "200" with body where "results" has a length of "3"
      | path                              | value                                 |
      | results.0.id                      | ${ note(device_reference_data_id_1) } |
      | results.0.name                    | My Device Reference Data 1            |
      | results.0.status                  | active                                |
      | results.0.environment             | dev                                   |
      | results.0.product_id              | ${ note(product_id) }                 |
      | results.0.product_team_id         | ${ note(product_team_id) }            |
      | results.0.ods_code                | F5H1R                                 |
      | results.0.created_on              | << ignore >>                          |
      | results.0.updated_on              | << ignore >>                          |
      | results.0.deleted_on              | << ignore >>                          |
      | results.0.questionnaire_responses | {}                                    |
      | results.1.id                      | ${ note(device_reference_data_id_2) } |
      | results.1.name                    | My Device Reference Data 2            |
      | results.1.status                  | active                                |
      | results.1.environment             | dev                                   |
      | results.1.product_id              | ${ note(product_id) }                 |
      | results.1.product_team_id         | ${ note(product_team_id) }            |
      | results.1.ods_code                | F5H1R                                 |
      | results.1.created_on              | << ignore >>                          |
      | results.1.updated_on              | << ignore >>                          |
      | results.1.deleted_on              | << ignore >>                          |
      | results.1.questionnaire_responses | {}                                    |
      | results.2.id                      | ${ note(device_reference_data_id_3) } |
      | results.2.name                    | My Device Reference Data 3            |
      | results.2.status                  | active                                |
      | results.2.environment             | dev                                   |
      | results.2.product_id              | ${ note(product_id) }                 |
      | results.2.product_team_id         | ${ note(product_team_id) }            |
      | results.2.ods_code                | F5H1R                                 |
      | results.2.created_on              | << ignore >>                          |
      | results.2.updated_on              | << ignore >>                          |
      | results.2.deleted_on              | << ignore >>                          |
      | results.2.questionnaire_responses | {}                                    |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 1099             |

    Examples:
      | product_team_id            | product_id            |
      | ${ note(product_team_id) } | ${ note(product_id) } |
      | FOOBAR                     | ${ note(product_id) } |

  Scenario Outline: Successfully search multiple EPR Device Reference Data (Message set & Additional Interactions)
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path             | value                 |
      | name             | My Great Product Team |
      | ods_code         | F5H1R                 |
      | keys.0.key_type  | product_team_id_alias |
      | keys.0.key_value | FOOBAR                |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/<product_team_id>/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I note the response field "$.keys.0.key_value" as "party_key"
    And I have already made a "POST" request with "default" headers to "ProductTeam/<product_team_id>/Product/<product_id>/dev/DeviceReferenceData/MhsMessageSet"
    And I note the response field "$.id" as "device_reference_data_id_msg_set"
    And I have already made a "POST" request with "default" headers to "ProductTeam/<product_team_id>/Product/<product_id>/dev/DeviceReferenceData/AccreditedSystemsAdditionalInteractions"
    And I note the response field "$.id" as "device_reference_data_id_additional_interactions"
    When I make a "GET" request with "default" headers to "ProductTeam/<product_team_id>/Product/<product_id>/dev/DeviceReferenceData"
    Then I receive a status code "200" with body where "results" has a length of "2"
      | path                              | value                                                       |
      | results.0.id                      | ${ note(device_reference_data_id_msg_set) }                 |
      | results.0.name                    | F5H1R-850000 - MHS Message Sets                             |
      | results.0.status                  | active                                                      |
      | results.0.environment             | dev                                                         |
      | results.0.product_id              | ${ note(product_id) }                                       |
      | results.0.product_team_id         | ${ note(product_team_id) }                                  |
      | results.0.ods_code                | F5H1R                                                       |
      | results.0.questionnaire_responses | {}                                                          |
      | results.0.created_on              | << ignore >>                                                |
      | results.0.updated_on              | << ignore >>                                                |
      | results.0.deleted_on              | << ignore >>                                                |
      | results.1.id                      | ${ note(device_reference_data_id_additional_interactions) } |
      | results.1.name                    | F5H1R-850000 - AS Additional Interactions                   |
      | results.1.status                  | active                                                      |
      | results.1.environment             | dev                                                         |
      | results.1.product_id              | ${ note(product_id) }                                       |
      | results.1.product_team_id         | ${ note(product_team_id) }                                  |
      | results.1.ods_code                | F5H1R                                                       |
      | results.1.questionnaire_responses | {}                                                          |
      | results.1.created_on              | << ignore >>                                                |
      | results.1.updated_on              | << ignore >>                                                |
      | results.1.deleted_on              | << ignore >>                                                |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 757              |

    Examples:
      | product_team_id            | product_id            |
      | ${ note(product_team_id) } | ${ note(product_id) } |
      | ${ note(product_team_id) } | ${ note(party_key) }  |
      | FOOBAR                     | ${ note(product_id) } |
      | FOOBAR                     | ${ note(party_key) }  |

  Scenario: Successfully create and retrieve an EPR product with MHSMessageSet and ASAdditionalInteractions containing questionnaire responses
    Given I have already made a "POST" request with "default" headers to "ProductTeam" with body:
      | path     | value                 |
      | name     | My Great Product Team |
      | ods_code | F5H1R                 |
    And I note the response field "$.id" as "product_team_id"
    And I have already made a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/Epr" with body:
      | path | value            |
      | name | My Great Product |
    And I note the response field "$.id" as "product_id"
    And I note the response field "$.keys.0.key_value" as "party_key"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/MhsMessageSet" with body:
      | path                                                                                        | value                          |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS SN                                     | urn:nhs:names:services:ers     |
      | questionnaire_responses.spine_mhs_message_sets.0.MHS IN                                     | READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_mhs_message_sets.1.MHS SN                                     | urn:nhs:names:services:ebs     |
      | questionnaire_responses.spine_mhs_message_sets.1.MHS IN                                     | PRSC_IN080000UK07              |
      | questionnaire_responses.spine_mhs_message_sets.1.Reliability Configuration Retry Interval   | PT1M                           |
      | questionnaire_responses.spine_mhs_message_sets.1.Reliability Configuration Retries          | ${ integer(2) }                |
      | questionnaire_responses.spine_mhs_message_sets.1.Reliability Configuration Persist Duration | PT10M                          |
    Then I receive a status code "201" with body
      | path                                                                                               | value                                                                          |
      | id                                                                                                 | << ignore >>                                                                   |
      | name                                                                                               | F5H1R-850000 - MHS Message Sets                                                |
      | status                                                                                             | active                                                                         |
      | environment                                                                                        | dev                                                                            |
      | product_id                                                                                         | ${ note(product_id) }                                                          |
      | product_team_id                                                                                    | ${ note(product_team_id) }                                                     |
      | ods_code                                                                                           | F5H1R                                                                          |
      | created_on                                                                                         | << ignore >>                                                                   |
      | updated_on                                                                                         | << ignore >>                                                                   |
      | deleted_on                                                                                         | << ignore >>                                                                   |
      | questionnaire_responses.spine_mhs_message_sets/1.0.id                                              | << ignore >>                                                                   |
      | questionnaire_responses.spine_mhs_message_sets/1.0.questionnaire_name                              | spine_mhs_message_sets                                                         |
      | questionnaire_responses.spine_mhs_message_sets/1.0.questionnaire_version                           | 1                                                                              |
      | questionnaire_responses.spine_mhs_message_sets/1.0.created_on                                      | << ignore >>                                                                   |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.MHS SN                                     | urn:nhs:names:services:ers                                                     |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.MHS IN                                     | READ_PRACTITIONER_ROLE_R4_V001                                                 |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.Interaction ID                             | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001                      |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.MHS CPA ID                                 | ${ note(party_key) }:urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_mhs_message_sets/1.0.data.Unique Identifier                          | ${ note(party_key) }:urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_mhs_message_sets/1.1.id                                              | << ignore >>                                                                   |
      | questionnaire_responses.spine_mhs_message_sets/1.1.questionnaire_name                              | spine_mhs_message_sets                                                         |
      | questionnaire_responses.spine_mhs_message_sets/1.1.questionnaire_version                           | 1                                                                              |
      | questionnaire_responses.spine_mhs_message_sets/1.1.created_on                                      | << ignore >>                                                                   |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.MHS IN                                     | PRSC_IN080000UK07                                                              |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.MHS SN                                     | urn:nhs:names:services:ebs                                                     |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Interaction ID                             | urn:nhs:names:services:ebs:PRSC_IN080000UK07                                   |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.MHS CPA ID                                 | ${ note(party_key) }:urn:nhs:names:services:ebs:PRSC_IN080000UK07              |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Unique Identifier                          | ${ note(party_key) }:urn:nhs:names:services:ebs:PRSC_IN080000UK07              |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Reliability Configuration Retry Interval   | PT1M                                                                           |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Reliability Configuration Retries          | ${ integer(2) }                                                                |
      | questionnaire_responses.spine_mhs_message_sets/1.1.data.Reliability Configuration Persist Duration | PT10M                                                                          |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 1582             |
    And I note the response field "$.id" as "mhs_device_reference_data_id"
    When I make a "POST" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData/AccreditedSystemsAdditionalInteractions" with body:
      | path                                                                      | value                                                     |
      | questionnaire_responses.spine_as_additional_interactions.0.Interaction ID | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_as_additional_interactions.1.Interaction ID | urn:nhs:names:services:ebs:PRSC_IN080000UK07              |
    Then I receive a status code "201" with body
      | path                                                                               | value                                                     |
      | id                                                                                 | << ignore >>                                              |
      | name                                                                               | F5H1R-850000 - AS Additional Interactions                 |
      | status                                                                             | active                                                    |
      | environment                                                                        | dev                                                       |
      | product_id                                                                         | ${ note(product_id) }                                     |
      | product_team_id                                                                    | ${ note(product_team_id) }                                |
      | ods_code                                                                           | F5H1R                                                     |
      | created_on                                                                         | << ignore >>                                              |
      | updated_on                                                                         | << ignore >>                                              |
      | deleted_on                                                                         | << ignore >>                                              |
      | questionnaire_responses.spine_as_additional_interactions/1.0.id                    | << ignore >>                                              |
      | questionnaire_responses.spine_as_additional_interactions/1.0.questionnaire_name    | spine_as_additional_interactions                          |
      | questionnaire_responses.spine_as_additional_interactions/1.0.questionnaire_version | 1                                                         |
      | questionnaire_responses.spine_as_additional_interactions/1.0.created_on            | << ignore >>                                              |
      | questionnaire_responses.spine_as_additional_interactions/1.0.data.Interaction ID   | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
      | questionnaire_responses.spine_as_additional_interactions/1.1.id                    | << ignore >>                                              |
      | questionnaire_responses.spine_as_additional_interactions/1.1.questionnaire_name    | spine_as_additional_interactions                          |
      | questionnaire_responses.spine_as_additional_interactions/1.1.questionnaire_version | 1                                                         |
      | questionnaire_responses.spine_as_additional_interactions/1.1.created_on            | << ignore >>                                              |
      | questionnaire_responses.spine_as_additional_interactions/1.1.data.Interaction ID   | urn:nhs:names:services:ebs:PRSC_IN080000UK07              |
    And the response headers contain:
      | name           | value            |
      | Content-Type   | application/json |
      | Content-Length | 980              |
    And I note the response field "$.id" as "as_device_reference_data_id"
    When I make a "GET" request with "default" headers to "ProductTeam/${ note(product_team_id) }/Product/${ note(product_id) }/dev/DeviceReferenceData"
    Then I receive a status code "200" with body where "results" has a length of "2"
      | path                                                                                                         | value                                                                          |
      | results.0.id                                                                                                 | << ignore >>                                                                   |
      | results.0.name                                                                                               | F5H1R-850000 - MHS Message Sets                                                |
      | results.0.status                                                                                             | active                                                                         |
      | results.0.environment                                                                                        | dev                                                                            |
      | results.0.product_id                                                                                         | ${ note(product_id) }                                                          |
      | results.0.product_team_id                                                                                    | ${ note(product_team_id) }                                                     |
      | results.0.ods_code                                                                                           | F5H1R                                                                          |
      | results.0.created_on                                                                                         | << ignore >>                                                                   |
      | results.0.updated_on                                                                                         | << ignore >>                                                                   |
      | results.0.deleted_on                                                                                         | << ignore >>                                                                   |
      | results.0.questionnaire_responses.spine_mhs_message_sets/1.0.id                                              | << ignore >>                                                                   |
      | results.0.questionnaire_responses.spine_mhs_message_sets/1.0.questionnaire_name                              | spine_mhs_message_sets                                                         |
      | results.0.questionnaire_responses.spine_mhs_message_sets/1.0.questionnaire_version                           | 1                                                                              |
      | results.0.questionnaire_responses.spine_mhs_message_sets/1.0.created_on                                      | << ignore >>                                                                   |
      | results.0.questionnaire_responses.spine_mhs_message_sets/1.0.data.MHS SN                                     | urn:nhs:names:services:ers                                                     |
      | results.0.questionnaire_responses.spine_mhs_message_sets/1.0.data.MHS IN                                     | READ_PRACTITIONER_ROLE_R4_V001                                                 |
      | results.0.questionnaire_responses.spine_mhs_message_sets/1.0.data.Interaction ID                             | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001                      |
      | results.0.questionnaire_responses.spine_mhs_message_sets/1.0.data.MHS CPA ID                                 | ${ note(party_key) }:urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
      | results.0.questionnaire_responses.spine_mhs_message_sets/1.0.data.Unique Identifier                          | ${ note(party_key) }:urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001 |
      | results.0.questionnaire_responses.spine_mhs_message_sets/1.1.id                                              | << ignore >>                                                                   |
      | results.0.questionnaire_responses.spine_mhs_message_sets/1.1.questionnaire_name                              | spine_mhs_message_sets                                                         |
      | results.0.questionnaire_responses.spine_mhs_message_sets/1.1.questionnaire_version                           | 1                                                                              |
      | results.0.questionnaire_responses.spine_mhs_message_sets/1.1.created_on                                      | << ignore >>                                                                   |
      | results.0.questionnaire_responses.spine_mhs_message_sets/1.1.data.MHS SN                                     | urn:nhs:names:services:ebs                                                     |
      | results.0.questionnaire_responses.spine_mhs_message_sets/1.1.data.MHS IN                                     | PRSC_IN080000UK07                                                              |
      | results.0.questionnaire_responses.spine_mhs_message_sets/1.1.data.Reliability Configuration Retry Interval   | PT1M                                                                           |
      | results.0.questionnaire_responses.spine_mhs_message_sets/1.1.data.Reliability Configuration Retries          | ${ integer(2) }                                                                |
      | results.0.questionnaire_responses.spine_mhs_message_sets/1.1.data.Reliability Configuration Persist Duration | PT10M                                                                          |
      | results.0.questionnaire_responses.spine_mhs_message_sets/1.1.data.Interaction ID                             | urn:nhs:names:services:ebs:PRSC_IN080000UK07                                   |
      | results.0.questionnaire_responses.spine_mhs_message_sets/1.1.data.MHS CPA ID                                 | ${ note(party_key) }:urn:nhs:names:services:ebs:PRSC_IN080000UK07              |
      | results.0.questionnaire_responses.spine_mhs_message_sets/1.1.data.Unique Identifier                          | ${ note(party_key) }:urn:nhs:names:services:ebs:PRSC_IN080000UK07              |
      | results.1.id                                                                                                 | ${ note(as_device_reference_data_id) }                                         |
      | results.1.name                                                                                               | F5H1R-850000 - AS Additional Interactions                                      |
      | results.1.status                                                                                             | active                                                                         |
      | results.1.environment                                                                                        | dev                                                                            |
      | results.1.product_id                                                                                         | ${ note(product_id) }                                                          |
      | results.1.product_team_id                                                                                    | ${ note(product_team_id) }                                                     |
      | results.1.ods_code                                                                                           | F5H1R                                                                          |
      | results.1.questionnaire_responses.spine_as_additional_interactions/1.0.id                                    | << ignore >>                                                                   |
      | results.1.questionnaire_responses.spine_as_additional_interactions/1.0.questionnaire_name                    | spine_as_additional_interactions                                               |
      | results.1.questionnaire_responses.spine_as_additional_interactions/1.0.questionnaire_version                 | 1                                                                              |
      | results.1.questionnaire_responses.spine_as_additional_interactions/1.0.created_on                            | << ignore >>                                                                   |
      | results.1.questionnaire_responses.spine_as_additional_interactions/1.0.data.Interaction ID                   | urn:nhs:names:services:ers:READ_PRACTITIONER_ROLE_R4_V001                      |
      | results.1.questionnaire_responses.spine_as_additional_interactions/1.1.id                                    | << ignore >>                                                                   |
      | results.1.questionnaire_responses.spine_as_additional_interactions/1.1.questionnaire_name                    | spine_as_additional_interactions                                               |
      | results.1.questionnaire_responses.spine_as_additional_interactions/1.1.questionnaire_version                 | 1                                                                              |
      | results.1.questionnaire_responses.spine_as_additional_interactions/1.1.created_on                            | << ignore >>                                                                   |
      | results.1.questionnaire_responses.spine_as_additional_interactions/1.1.data.Interaction ID                   | urn:nhs:names:services:ebs:PRSC_IN080000UK07                                   |
      | results.1.created_on                                                                                         | << ignore >>                                                                   |
      | results.1.updated_on                                                                                         | << ignore >>                                                                   |
      | results.1.deleted_on                                                                                         | << ignore >>                                                                   |
