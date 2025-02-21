# Connecting Party Manager

## Overview

## Table of Contents

1. [Setup](#setup)
   1. [Prerequisites](#prerequisites)
   2. [Project build](#project-build)
   3. [AWS SSO Setup](#aws-sso-setup)
   4. [Other helpful commands](#other-helpful-commands)
2. [Tests](#tests)
   1. [pytest tests](#pytest-tests)
   2. [End-to-End feature tests](#end-to-end-feature-tests)
   3. [Generate the Feature Test Postman collection](#generate-the-feature-test-postman-collection)
3. [Data modelling](#data-modelling)
   1. [Domain models](#domain-models)
   2. [Database models](#database-models)
   3. [Response models](#response-models)
   4. [Request models](#request-models)
4. [Workflow](#workflow)
5. [Swagger](#swagger)
6. [ETL](#etl)
7. [Administration](#administration)

---

## Setup

### Prerequisites

We use `asdf` to fetch the required versions of prerequisite libraries instead of your system's default version. To get it up and running go to <https://asdf-vm.com/guide/getting-started.html>. You can check it installed properly by using the command `asdf --version`.

However, you will also need to install the `docker engine` separately

Additionally you will need `wget` (doing `which wget` will return blank if not installed). Please Google "how to install wget on my operating system", if you don't already have this installed.

Update any dependencies on your system as required.

Otherwise `asdf` should do the work for you.

### Useful tools

`VScode` is useful and we have a workspace file setup to allow easy integration

`Postman` &/or `Newman` Feature tests create a postman.collection which can be used for manual testing.

### Project build

Do `make build` every time you would like to pick up and install new local/project dependencies and artifacts. This will always detect changes to:

- `.tool-versions` (project prerequisites)
- `pyproject.toml` (python dependencies)
- non-development files in the `src` directory

The first time it will also set up your pre-commit hooks.

### Proxygen

We use [Proxygen](https://github.com/NHSDigital/proxygen-cli) to deploy our proxies and specs to APIM which we have wrapped up into a make command:

- `make apigee--deploy`

This when run locally will need you to have done a local `terraform--plan` and `terraform--apply` (as it will read some details from the output files)

Caveats

- At present we have one set of credentials that we use across PTL and PROD (so that the name of the api remains constant)
- We are temporarily using the apikey method of authentication, which requires the deployment of a key that is used in the swagger - example below:
  - `proxygen secret put sandbox cpm-1 --apikey --secret-value=iamsecret`
  - We plan on replacing this with MTLS as soon as we can

#### Temporary Proxies

To avoid us having too many proxies deployed that we fail to manage, for anything that isnt a Persistent Environment or equivalent sandbox (dev, dev-sandbox) - then the Proxy will be tagged as `temporary`. This means that it will be deleted after a period of time determined by APIM and the code can be found in the swagger generation files under the `x-nhsd-apim` header

### AWS SSO Setup

This project uses Single Sign On (SSO) for consuming AWS services.

To configure SSO run the following command

```
aws configure sso
```

using the following parameters, where <REPLACE_ME> matches the URL of the SSO app you should have as a bookmark:

```
SSO session name (Recommended): NHS
SSO start URL [None]: https://<REPLACE_ME>.awsapps.com/start#
SSO region [None]: eu-west-2
SSO registration scopes [sso:account:access]: sso:account:access
```

A browser window should appear. To progress you will need to click "Confirm and continue" and then "Allow", after reading and understanding the instructions. Once complete you will be returned to the console.

You can now configure your first profile, by selecting a value from the list and answering the prompts. You should setup `NHS Digital Spine Core CPM MGMT` first. Successive profiles can be added by repeating `aws configure sso` but this time the SSO session name exists and will not be recreated.

Entries will now be visible in your `~/.aws/config` file.

You may now login to AWS via SSO using:

```
aws sso login --sso-session NHS
```

You may now switch between profiles by using, where <profile> is taken from the entry in your `~/.aws/config` file:

```
export AWS_PROFILE=<profile>
```

This is the preferred method of switching between profiles, as it will cause the profile name to appear in your BASH prompt.

### Build a local workspace on AWS (DEV)

You can build a working copy of the CPM service in your own workspace within the `dev` environment. To do this follow these steps. (You must have SSO setup on your system and have MGMT admin access)

You must pass a `TERRAFORM_WORKSPACE` variable to each command in the format `YOUR_SHORTCODE_AND_JIRA_NUMBER`. This variable must not contain spaces, but can contain underscores and hyphens. `e.g. jobl3-PI-100`

```shell
make terraform--init TERRAFORM_WORKSPACE="<YOUR_SHORTCODE_AND_JIRA_NUMBER>" # Will attempt to login to AWS first using SSO
make terraform--plan TERRAFORM_WORKSPACE="<YOUR_SHORTCODE_AND_JIRA_NUMBER>" # Will attempt to build the project first
make terraform--apply TERRAFORM_WORKSPACE="<YOUR_SHORTCODE_AND_JIRA_NUMBER>"
```

### Build a local workspace on AWS (QA)

For testing purposes we have another command to allow testers to deploy to QA (to avoid the often change heavy dev) - very similar to the above except the command hard codes the QA environment behind the scenes.

```shell
make terraform--init TERRAFORM_WORKSPACE="<YOUR_SHORTCODE_AND_JIRA_NUMBER>" # Will attempt to login to AWS first using SSO
make terraform--plan--qa TERRAFORM_WORKSPACE="<YOUR_SHORTCODE_AND_JIRA_NUMBER>" # Will attempt to build the project first
make terraform--apply--qa TERRAFORM_WORKSPACE="<YOUR_SHORTCODE_AND_JIRA_NUMBER>"
```

### Destroy a local workspace on AWS

Destroy the local workspace and it's corresponding state file on mgmt

```shell
make terraform--destroy TERRAFORM_WORKSPACE="<YOUR_SHORTCODE_AND_JIRA_NUMBER>" # Will attempt to login to AWS first using SSO
```

### Automated workspace destroys

We have some automated behaviour for destroying our workspaces - we build off a new commit each time we deploy and there are times where we forget to destroy old workspaces or have CI workspaces be removed. So we have two processes:

#### Destroy Expired Workspaces

- This is run on a cron job as a github workflow every evening and scans the workspaces in dev (local deployments) and ref (CI deployments)
- Each deployment is deployed with a resource group that has an expiration date on it, the workspace is destroyed if its past that date
- Each deploy or change within a workspace extends the expiration date
- Can be run adhoc by using the command: `make destroy--expired TERRAFORM_WORKSPACE="dev"`

#### Destroy Redundant Workspaces

- This is part of the Pull Request github workflow and checks to destroy previous commits on the same workspace leaving only the latest
- When you run locally you can override this with the `KILL_ALL` flag which destroys the current commit too
- Can be run adhoc with the command: `make destroy--redundant-workspaces BRANCH_NAME=mybranch DESTROY_ALL_COMMITS_ON_BRANCH=false KILL_ALL=false`

#### Destroy Corrupted Workspaces

- This is a way to destroy a workspace on dev if terraform is not destroying it. This is not fool-proof as there are many different "chicken and egg" scenarios to infrastructure. But it should go some way to having a destroyed environment
- Can be run manually by using the command: `make destroy--corrupted TERRAFORM_WORKSPACE="<WORKSPACE_TO_DESTROY>" TERRAFORM_ROLE_NAME="NHSDeploymentRole"`

## Updating Roles

We have several roles that we currently handle outside of terraform as its needed to deploy the terraform:

- NHSDeploymentRole
- NHSDevelopmentRole
- NHSTestCIRole
- NHSSmokeTestRole

To update any of the roles used for SSO then you need to do the following command which should prompt you to log in via SSO:

`make manage--non-mgmt-policies MGMT_ACCOUNT_ID=<ID> SSO_PROFILE="dev-admin"`
&
`make manage--non-mgmt-test-policies MGMT_ACCOUNT_ID=<ID> SSO_PROFILE="dev-admin"`

Where:

- MGMT ACCOUNT ID = The account id for mgmt so that it can be substituted into the role trust policy
- SSO_PROFILE = This is the profile in you .aws/config file where you will specify the details for each environment
  - dev-admin
  - qa-admin
  - ref-admin
  - int-admin
  - prod-admin

### Other helpful commands

Run `make` to get a list of helpful commands.

## Tests

### `pytest` tests

There are four types of `pytest` in this project:

- Unit: these _do not have_ any `@pytest.mark` markers;
- Integration: these have `@pytest.mark.integration` markers;
- Smoke: these have `@pytest.mark.smoke` markers;
- Matrix: these have `@pytest.mark.matrix` markers;

In order to run these you can do one of::

```shell
make test--unit
make test--integration   # Will attempt to log you into AWS first
make test--smoke         # Will attempt to log you into AWS first
make test--sds--matrix
```

If you would like to rerun all failed tests, you can append `--rerun` to the test command, e.g.:

```shell
make test--unit--rerun
```

If you would like to pass `pytest` flags you can do e.g. to \[stop after the first failure\] with \[very\] \[verbose\] feedback:

```shell
make test--unit PYTEST_FLAGS="-xvv"
```

Otherwise, feel free to run `pytest` from your `poetry` shell for more fine-grained control (see Google for more info!).

The VSCode settings for "Run and Debug" are also set up to run these tests if your prefer.

`make test--sds--matrix` is used for testing responses match in SDS FHIR between CPM and LDAP. You must provide `SDS_PROD_APIKEY` and `SDS_DEV_APIKEY`. There are 3 optional variables `USE_CPM_PROD`, defaults to `FALSE`, `COMPARISON_ENV`, defaults to `local` and `TEST_COUNT`, defaults to `10` and is the number of requests to make.
Add `PYTEST_FLAGS='-sv'`.

### End-to-End feature tests

The Feature tests use `behave` (rather than `pytest`) to execute cucumber/gherkin-style end-to-end tests of specific features, in principle
giving full end-to-end test coverage for API operations.

Executing feature tests locally will give you a good idea whether you have implemented a well-behaved feature whilst in development (i.e. no need to redeploy whilst developing).

Executing feature tests in integration mode will then give you confidence that the feature is ready to deploy in production, but has a much slower development cycle as it will need a full redeploy after codebase or infrastructure changes are implemented.

#### Local

To execute the feature tests entirely locally (executing lambdas directly, and otherwise mocking databases and responses to a high standard) you can do:

```shell
make test--feature--local
```

If you would like to pass `behave` flags, e.g. to \[stop after the first failure\]:

```shell
make test--feature--local BEHAVE_FLAGS="--stop"
```

#### Integration

To execute the feature tests across the entire stack (including Apigee and AWS) you can do

```shell
make test--feature--integration
```

### Generate the Feature Test Postman collection

Our [end-to-end feature tests](#end-to-end-feature-tests) also generate working Postman collections. To generate the Postman collection quickly, without Apigee credentials, you can run the local feature tests. If you would like the Apigee
credentials generating then you should run the integration feature tests. The generated files are:

- `src/api/tests/feature_tests/postman-collection.json`
- `src/api/tests/feature_tests/postman-environment.json`

You can drag and drop `postman-collection.json` into the `Collections` tab on Postman,
and `postman-environment.json` on to the `Environments` tab (remember to activate it). If you generated these
with the local feature tests, then you will need to manually update the Apigee `baseUrl` and `apiKey` fields
in the environment (but these are filled out already if generated with the integration feature tests).

💡 **The feature tests are only guaranteed to work out-of-the-box with an empty database**

## Data modelling

Modelling in Connecting Party Manager is split into four partially-decoupled components:

- Domain models: The conceptual entities of Connecting Party Manager, without any reference to database indexing, and request / response syntax.
- Database models: A wrapper on the domain models that we persist to database (DynamoDB), indicating write-integrity (primary keys) and a read/search interface (indexing).
- Response models: Deviations from the domain model (error handling, search result wrapping, private field exclusion, etc)
- Request models: API-specific models indicating the expected request bodies of create/update/search operations.

### Domain models

TBC

### Database models

#### Write-integrity (primary keys)

The Partition Key (`pk`) that we use for all objects\* in the database is a unique combination of prefix (aligned with the object type, e.g. `D#` for `Device`) and identifier (generally a UUID). The Sort Key (`sk`) that we use is always exactly equal to the Partition Key. This is opposed to having fully denormalised objects so that attributes are nested under their own `sk`. The reason for doing this is to limit multiple read operations for a given object, and also save I/O in our ETL process by reducing the number of database transactions required per object.

Objects can additionally be indexed by any keys (see [Domain models](#domain-models)) that they have. For every key in an domain object,
a copy is made in the database with the index being that key, rather
than the object's identifier. Such copies are referred to as non-root
objects, whereas the "original" (indexed by identifier) is referred to
as the root object.

\* In the case of `Device` tags, which sit outside of the standard database model, `pk` is equal to a query string and `sk` is equal to `pk` of the object that is referred to. A tag-indexed `Device` is otherwise a copy of the root `Device`.

#### Read/search interface

We have implemented a Global Secondary Index (GSI) for attributes named `pk_read` and `sk_read`. The pattern that is place is as follows:

- `pk_read`: A concatenation of parent `pk` values (joined with `#`, e.g. `PT#<product_team_id>#P<product_id>`)
- `sk_read`: Equal to the `pk` of the object itself.

We refer to this as an "ownership" model, as it allows for reads to be
executed in a way that mirrors the API read operations (GET `grandparent/parent/child`), whilst also giving us the ability to return all objects owned by the object indicated in the `pk_read` - which is a common operation for us.

A `read` and `search` is available on all `Repository` patterns (almost) for free (the base `_read` and `_search` require a shallow wrapper, but most of the work is done for you).

### Response models

TBC

### Request models

TBC

## Workflow

In order to create new branches, use the commands listed below. Note that the commands will throw an error if
you attempt to use them without rebasing on `origin/main`. If you need to rebase, then please do so carefully. We recommend
that you first inspect your divergent branch with:

```shell
git log --all --decorate --oneline --graph
```

If you branch is irreparably divergent from `origin/main`, you may find it easier to recreate your base branch and to pull in relevant changes.

### Create new feature branch

From `main` (or a branch based from `main`) do:

```shell
make workflow--create-feature-branch JIRA_TICKET="PI-123" DESCRIPTION="this Is MY ticKET"
```

which will create a branch of the form `feature/PI-123-this_is_my_ticket`.

### Create new release branch

From `main` (or a branch based from `main`) do:

```shell
make workflow--create-release-branch
```

which will create a branch of the form `release/YYYY-MM-DD`. If this branch name has already been taken it will append a patch version to the branch name.

This command will also:

- Update the version in `pyproject.toml` with the release branch version.
- Update the VERSION file with the release branch version number.

## Swagger

This is all done by `make build`. For more details on how to update the Swagger, please see [the swagger README](infrastructure/swagger/README.md).

## Setting Lambda permissions

Lambda permissions are able to be set individually, To do this,

- Inside the lambda src code. e.g. `src/api/createProductTeam` there is a subfolder called `policies`
- In here create a `json` file named after the aws resource type that you wish to create permissions for. For example if you wanted to add permissions to access s3 buckets then you would add a file called `s3.json`
- In this file add a list of permissions for s3 access. e.g. `["s3:ListBucket", "s3:GetObject"]`
- Finally in `infrastructure/terraform/per_workspace/locals.tf` there is a mapping `permission_resource_map`. Add the mapping to the resources that these permissions need access to. e.g.`s3 = "${module.s3.s3_arn}"`

## Terraform

If you find yourself with a locked terraform state, do:

```
make terraform--unlock TERRAFORM_ARGS=<lock_id>
```

## ETL

### Debugging the state after changelog errors

In order to get the latest head state of the ETL, do either (for your developer workspace)

```
make etl--head-state--developer
```

or for a persistent workspace (`dev`, `prod`, etc):

```
make etl--head-state--persistent-workspace WORKSPACE=<workspace_name>
```

For the developer operation, the script will automatically activate via SSO, however for the persistent-workspace
operation you will need to export credentials by navigating yourself to the SSO login page and exporting the
credentials for the workspace into your terminal.

### Clearing the state (don't take this lightly, intended for first time bulk upload only)

Before running the bulk trigger, you need to clear the initial ETL state, do:

```
make etl--clear-state
```

Before running the changelog trigger you additionally need to specify a changelog number (ideally close to the true latest changelog number, otherwise the logs will be pretty heavy!)

```
make etl--clear-state SET_CHANGELOG_NUMBER=540210
```

You can additionally set the workspace name if you want to clear the state for a given (e.g. persistent) workspace name:

```
make etl--clear-state WORKSPACE=dev
```

and

```
make etl--clear-state WORKSPACE=dev SET_CHANGELOG_NUMBER=540210
```

## Administration

### Generating Ids

In order to generate a persistent list of Ids across environments then run... (The example given will generate 100 ids.)

```
make admin--generate-ids--product SET_GENERATOR_COUNT=100
```

Any previously generated ids will not be overwritten.

### Documentation

We have several locations for the Swagger to keep things as visible as possible

In this repository there is a folder that contains the most recent Public facing swagger.yaml

`docs/public_swagger/swagger.yaml`

We also have a confluence page

`https://nhsd-confluence.digital.nhs.uk/display/SPINE/CPM+Swagger+Docs`

In time we will also have our spec uploaded to bloomreach via proxygen

## SBOM (Service Bill of Materials)

As a stop gap for now - you should download Syft and Grype to your machine (ASDF doesnt do grype for some reason)

`brew install syft`

`brew tap anchore/grype`
`brew install grype`

To run the SBOM commands there are some make commands that currently handle this:

`make generate--sbom`
`make validate--sbom`

## Extras

### Archive

The project originally was designed to have a concept of an EPRv2. This did not work out but we have kept the remains of the EPR work in an archive folder located in the `root/archived_epr`. The EPR code was supposed to fit into the structure of our existing CPM model but it became apparent as requirements came through that this would not be possible. You will find in this folder `swagger/OAS spec`, `lambdas`, `ETL` and `tests`.

This has been left in for future reference. The code would need to be transferred back into the root of the project, changing `src_old` back to `src` and merging into the existing `src` directory.
