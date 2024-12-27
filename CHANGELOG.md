# Changelog

## 2024-12-27
- [PI-602] Update spine_as Questionnaire
- [PI-687] ETL: Delete an MHS
- [PI-686] ETL: Add an AS
- [PI-629] Add search DRD tests

## 2024-12-23
- [PI-652] Evironment layers

## 2024-12-16
- [PI-681] EPR endpoints requirements
- [PI-702] Prod bulk tweak
- [PI-653] EPR create endpoints - forbid duplicate interactions
- [PI-606] ETL Updates, with "add an mhs"

## 2024-12-11
- [PI-650] Modify the Read Device endpoint for AS Devices
- [PI-666] Create an ASID for AS Device and add as a DeviceKey
- [PI-603] Update the spine_mhs questionnaire
- [PI-645] Update the spine_mhs_message_sets questionnaire

## 2024-12-05
- [PI-631] Generate Product Ids
- [PI-691] Allow devs to clear terminal after each Feature Test
- [PI-618] Bulk ETL

## 2024-12-02
- [PI-572] Create an AS Device
- [PI-582] AS Additional Interations smoke test

## 2024-11-27
- [PI-605] Bulk ETL (transform layer)
- [PI-582] Read MHS Device

## 2024-11-25
- [PI-643] Add status to Device Reference Data
- Dependabot: slack-github-action, pydantic

## 2024-11-22
- [PI-528] Collapse versioning to v1
- [PI-581] MHS Device with Device Reference Data

## 2024-11-19
- [PI-601] Workspace destroy, use main branch as fallback

## 2024-11-18
- [PI-601] Workspace destroy, use main branch if branch no longer exists

## 2024-11-13
- [PI-617] Stream bulk LDIF into blocks of party key
- [PI-527] Swagger fix
- [PI-592] GSI Upgrade
- [PI-590] Read/write by alias

## 2024-11-08
- [PI-508] Search DeviceReferenceData
- [PI-578] Create MHS Device
- [PI-512] AS Interactions DeviceReferenceData

## 2024-11-06
- [PI-593] Readme updates
- [PI-594] More smoke tests
- [PI-575] Remove implicit OK from responses
- [PI-558] Add search wrapper
- [PI-591] Better postman
- [PI-293] E2E tests with apigee
- [PI-601] Destroy workspaces on PR close

## 2024-11-05
- [PI-585] PR/release CI builds in dev

## 2024-10-31
- [PI-555] Remov fhir from create device endpoint
- [PI-556] Remov fhir from read device endpoint
- [PI-559] Remov fhir from make file
- [PI-530] Clean up fhir
- [PI-571] Recreate swagger
- [PI-589] Publish swagger spec int

## 2024-10-29
- [PI-565] Add EPR questionnaires
- [PI-577] Create Message Set Device Reference Data
- [PI-574] CPM Smoke tests don't write data to DB

## 2024-10-25
- [PI-551] Remove FHIR from Read CPM Product flow
- [PI-553] Remove FHIR from Delete CPM Product flow

## 2024-10-22
- [PI-552] Remove FHIR from search CPMProduct
- [PI-557] Remove search Device
- [PI-560] Proxy naming
- [PI-563] Read a Questionnaire
- [PI-546] Fix ETL item exists failure

## 2024-10-16
- [PI-501] Create Device Reference Data
- [PI-503] Read Device Reference Data
- [PI-536] Create Cpm Product without FHIR
- [PI-535] Read Product Team without FHIR
- [PI-548] Sonarcloud configuration
- [PI-365] Locust load testing
- [PI-276] Proxygen Spec
- [PI-562] Feature Tests for CpmProduct

## 2024-10-15
- [PI-533] Create Product Team without FHIR

## 2024-10-14
- [PI-534] Errors without FHIR

## 2024-10-09
- [PI-504] Delete product
- [PI-498] Search products
- [PI-549] Fix flaky CI

## 2024-10-07
- [PI-505] Create EPR Product
- [PI-538] Increase rate limiting
- Dependabot: pre-commit

## 2024-10-02
- [PI-497] Read a CPM Product
- [PI-543] Remove snapshot from etl

## 2024-09-30
- [PI-473] Serialise tags more nicer
- [PI-522] Shorten lambda name

## 2024-09-26
- [PI-525] Update path structure for ProductTeams and Products

## 2024-09-25
- [PI-465] Extract worker bug
- [PI-479] SDS endpoint error messaging
- [PI-515] Drop tags field by default when searching tags
- [PI-520] Don't do SDS smoke test for dev-sandbox

## 2024-09-19
- [PI-495] Generating Product Ids
- [PI-496] Create CPM product
- [PI-519] Spike CI pipeline - terraform-base-build failure

## 2024-09-13
- [PI-477] query_by_tag ignore chunky device fields
- [PI-506] Upgrade lambda memory

## 2024-09-11
- [PI-493] Generating Party Keys
- [PI-494] Generating ASIDs
- [PI-499] CI s3 tests are running twice
- [PI-513] Unit test post request failing

## 2024-09-05
- [PI-219] Upgrade to Python 3.12
- [PI-491] Case-insensitive search

## 2024-09-02
- [PI-302] SDS Smoke Test
- [PI-245] Matrix Testing

## 2024-08-28
- [PI-468] Bulk and upload fixes

## 2024-08-22
- [PI-445] ETL v2
- [PI-452] Sonarcloud fixes
- [PI-271] Apigee key fixes
- [PI-476] Split ETL lambdas
- [PI-475] Query by tag

## 2024-08-20
- [PI-470] Hide inactive devices
- [PI-305] Add product to app CI
- [PI-279] Block ref sandbox deploy workflow

## 2024-08-09
- [PI-469] SDS search use query_by_tag
- [PI-379] Delete apigee proxy after smoke tests

## 2024-08-05
- [PI-447] SDS search endpoints
- [PI-446] Repo v2
- [PI-285] Questionnaire Response v2
- [PI-464] Device tags in repo
- [PI-392] updated_on after any Device modification
- [PI-381] pentest: clean up default vpc security groups

## 2024-07-26
- [PI-444] Domain v2
- [PI-285] Questionnaire v2

## 2024-07-23
- [PI-362] SPIKE - Write load test code

## 2024-07-22
- [PI-357] Automatic snapshots of ETL
- [PI-454] Delete corrupted workspace variable check

## 2024-07-16
- [PI-206] Complete "retry" trigger
- [PI-456] Turn off changelog in dev, ref & int

## 2024-07-15
- [PI-457] Run update sub-ETL on loop
- [PI-214] ETL debugger fix

## 2024-07-09
- [PI-450] ETL translation error

## 2024-07-08
- [PI-451] Improves ETL logging, may fix [PI-450] by allowing ldif deletions by replacing with empty value
- [PI-437] Sonarcloud improvements

## 2024-07-05
- [PI-435] REDLINE Repo changes
- [PI-360] Deployment of changelog

## 2024-07-03
- [PI-449] Batch up changelog changes

## 2024-07-02
- [PI-443] Run entire sds bulk transform/load in batches of 250k to save lambda memory and improve CPU time

## 2024-06-27
- [PI-319] Rename lambda connectivity module
- [PI-208] ETL notify lambda and slack hook

## 2024-06-25
- [PI-371] Prepare manual snapshots
- [PI-290] Rename and document SDS Bulk test data

## 2024-06-19
- [PI-207] Etl state lock lambda
- [PI-318] Seperate cache

## 2024-06-14
- [PI-179] Improve Slack messaging for deployments
- [PI-385] PENTEST - reject HTTP and enable access logs on S3 buckets

## 2024-06-04
- [PI-322] State machine lambda error messages truncated
- [PI-346] Update now includes modify changes, plus testing suite
- [PI-347] Updates implemented sequentially
- [PI-358] Disable SDS ETL update timer on persistent environments

## 2024-05-31
- [PI-342] Add redacted-fields to context loggers
- [PI-376] Check releases fully rebased on main

## 2024-05-29
- [PI-344] Added smoke test role

## 2024-05-23
- [PI-320] Add created_on, updated_on and deleted_on fields to a Device

## 2024-05-20-a
- [PI-373] authoriser fix
- [PI-172] spec in confluence and github
- [PI-275] fix connections between SDS FHIR and CPM

## 2024-05-15
- [PI-336] Changelog deletes
- Dependabot (pydantic)

## 2024-05-02
- [PI-341] Prod permissions
- [PI-268] Search for a device
- [PI-321] Inactive devices not returned during search

## 2024-04-26
- [PI-315] Update trigger
- [PI-343] Remove people branch

## 2024-04-16
- [PI-311] Smoke tests
- [PI-213] Connect to LDAP
- [PI-222] Connect to LDAP via VPC endpoint

## 2024-04-10
- [PI-307] Deploy user workspaces to qa environment
- [PI-292] Prod bulk data (SDS ETL)

## 2024-04-02
- [PI-180] Smoke tests
- [PI-205] Updates trigger
- [PI-288] Remove feature tests

## 2024-03-21
- [PI-272] Enable APIKey
- [PI-282] Fix int deploy
- [PI-260] Questionnaire responses in ETL

## 2024-03-15
- [PI-193] Search for a Device (MOCK)
- [PI-278] Fix expired workspace
- [PI-281] Fix Redundant workspace deletion

## 2024-03-11
- [PI-223] LDAP search on Lambda
- [PI-240] Domain name updates

## 2024-03-04
- [PI-203] Transform and load

## 2024-02-28
- [PI-192] create spine device questionnaire
- [PI-191] create spine endpoint questionnaire

## 2024-02-15
- [PI-229] Github Actions workflow run names
- [PI-201] ETL: Extract worker
- [PI-204] ETL: Bulk trigger

## 2024-02-13
- [PI-45] DNS
- [PI-221] Sonarcloud security hotspot fixes

## 2024-02-06
- [PI-187] Questionnaire response validation logic

## 2024-01-26
- [PI-200] Parsing LDIF files
- [PI-122] Proxygen in the CI

## 2024-01-19
- [PI-196] SDS ETL step function

## 2024-01-09
- [PI-131] Swagger narrative

## 2024-01-05
- [PI-158] Generate Product ID

## 2024-01-02
- [PI-129] Postman collection from local tests
- [PI-165] AWS environments

## 2023-12-20
- [PI-166] Versioning

## 2023-12-19
- [PI-162] Missing destroy permissions
- [PI-139] Fine-grained lambda permissions
- [PI-138] End-to-end feature tests run locally

## 2023-12-15
- [PI-82] Device e2e
- [PI-143] DynamoDb errors

## 2023-12-13
- [PI-81] Translation layer (FHIR Device)

## 2023-12-08
- [PI-145] Switch id to identifier
- [PI-80] Domain logic for Device
- [PI-127] PR feedback

## 2023-12-05
- PI-127 Rename Product to Device

## 2023-11-30
- [PI-118] End-to-end product team endpoints
- dependabot (datamodel-codegen)
- [PI-146] Lambda timeouts

## 2023-11-29
- [PI-128] Less Zealous Caching
- [PI-134] Developer Role

## 2023-11-24
- [PI-124] Revert Domain to AR model
- [PI-130] Move Check Branch to the beginning of CI Pipeline

## 2023-11-23
- [PI-110] Step chain refactor
- [PI-100] NHS Context logging
- Dependabot: pydantic, datamodel-codegen

## 2023-11-22
- [PI-120] Initial Apigee instance

## 2023-11-17
- [PI-77] Translation layer for FHIR Organization to ProductTeam
- [PI-73] Error Handling

## 2023-11-14
- [PI-125] FHIR / Swagger / Pydantic generation
- [PI-000] Dependabot
- [PI-000] debug

## 2023-11-09-a
- [PI-75] Create general table and repository interface

## 2023-11-07
- PI-112: Refactor API Gateway Terraform

## 2023-11-03
- [PI-53] Swagger models and a REST API that calls domain logic

## 2023-11-02
- [PI-52] ProductTeam Domain logic

## 2023-11-01
- [PI-107] Destroy workspaces

## 2023-10-30
- [PI-72] Validate ODS Code

## 2023-10-27-a
- [PI-71] Created releases
