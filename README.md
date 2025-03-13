# Connecting Party Manager

## Overview

## Table of Contents

1. [TLDR](#tldr)
   1. [Requirements](#requirements)
   2. [Building a local environment](#building-a-local-environment)
   3. [Testing](#testing)
   4. [Destroying a local environment](#destroying-a-local-environment)
1. [Setup](#setup)
   1. [Prerequisites](#prerequisites)
   2. [Useful tools](#useful-tools)
   3. [Project build](#project-build)
   4. [Proxygen](#proxygen)
   5. [Temporary Proxies](#temporary-proxies)
   6. [AWS SSO Setup](#aws-sso-setup)
   7. [Build a local workspace on AWS (DEV)](#build-a-local-workspace-on-aws-dev)
   8. [Build a local workspace on AWS (QA)](#build-a-local-workspace-on-aws-qa)
   9. [Destroy a local workspace on AWS](#destroy-a-local-workspace-on-aws)
   10. [Automated workspace destroys](#automated-workspace-destroys)
   11. [Destroy Expired Workspaces](#destroy-expired-workspaces)
   12. [Destroy Redundant Workspaces](#destroy-redundant-workspaces)
   13. [Destroy Corrupted Workspaces](#destroy-corrupted-workspaces)
   14. [Updating Roles](#updating-roles)
   15. [Other helpful commands](#other-helpful-commands)
1. [Tests](#tests)
   1. [pytest tests](#pytest-tests)
   2. [End-to-End feature tests](#end-to-end-feature-tests)
   3. [Local](#local)
   4. [Integration](#integration)
   5. [Generate the Feature Test Postman collection](#generate-the-feature-test-postman-collection)
1. [Data modelling](#data-modelling)
   1. [Domain models](#domain-models)
   2. [Database models](#database-models)
   3. [Response models](#response-models)
   4. [Request models](#request-models)
1. [Workflow](#workflow)
1. [Deployment](#deployment)
1. [Swagger](#swagger)
1. [Setting Lamba permissions](#setting-lambda-permissions)
1. [Terraform](#terraform)
1. [Administration](#administration)
1. [SBOM](#sbom)
1. [Extras](#extras)
   1. [Archive](#archive)

---

## TLDR

If you want to get up and running as quickly as possible then read this section. However it is advisable to read the full README when possible.

### Requirements

- Ensure you have `AWS SSO` setup. For more information please read the [AWS SSO Setup](#aws-sso-setup) section.
- Ensure you have `asdf` installed and the `docker engine` running. For more information please read the [Setup](#setup) section.

### Building a local environment

- Inside the connecting party manager root directory, run...
- `make terraform--apply`
- For more information please read the [Build a local workspace on AWS (DEV)](#build-a-local-workspace-on-aws-dev) section.

### Testing

- Inside the connecting party manager root directory, run any of the following commands...
- `make test--unit`
- `make test--integration`
- `make test--feature--local`
- `make test--feature--integration`
- `make test--smoke`

### Destroying a local environment

- Provided you haven't changed the workspace name, then.
- Inside the connecting party manager root directory, run...
- `make terraform--destroy`
- For more information please read the [Destroy a local workspace on AWS](#destroy-a-local-workspace-on-aws) section.

## Setup

### Prerequisites

We use `asdf` to fetch the required versions of prerequisite libraries instead of your system's default version. To get it up and running go to <https://asdf-vm.com/guide/getting-started.html>. You can check it installed properly by using the command `asdf --version`.

You will also need to install the `docker engine` separately

Additionally you will need `wget` (doing `which wget` will return blank if not installed). Please Google "how to install wget on my operating system", if you don't already have this installed.

Update any dependencies on your system as required.

Otherwise `asdf` should do the work for you.

### Useful tools

`VScode` is a useful IDE and we have a workspace file setup to allow easy integration

`Postman` &/or `Newman`. Feature tests create a postman.collection which can be used for manual testing.

### Project build

Do `make build` every time you would like to pick up and install new local/project dependencies and artifacts. This will always detect changes to:

- `.tool-versions` (project prerequisites)
- `pyproject.toml` (python dependencies)
- non-development files in the `src` directory

The first time it will also set up your pre-commit hooks.

### Proxygen

We use [Proxygen](https://github.com/NHSDigital/proxygen-cli) to deploy our proxies and specs to APIM which we have wrapped up into a make command:

- `make apigee--deploy`

When you run this locally you will need to have done a local `terraform--plan` and `terraform--apply` (as it will read some details from the output files)

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

Your workspace will build with an 8 digit hash of your system username by default. Therefore you do not need to provide a workspace name, however, if you would like to give your workspace a specific name then you must pass a `TERRAFORM_WORKSPACE` variable to each command. It is recommended that you use the format `YOUR_SHORTCODE_AND_JIRA_NUMBER`, but it will accept any name, however this variable must not contain spaces, but can contain underscores and hyphens. `e.g. jobl3-PI-100`

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

There are three types of `pytest` in this project:

- Unit: these _do not have_ any `@pytest.mark` markers;
- Integration: these have `@pytest.mark.integration` markers;
- Smoke: these have `@pytest.mark.smoke` markers;

In order to run these you can do one of:

```shell
make test--unit
make test--integration   # Will attempt to log you into AWS first
make test--smoke         # Will attempt to log you into AWS first
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

The Partition Key (`pk`) that we use for all objects\* in the database is a unique combination of prefix (aligned with the object type, e.g. `PT#` for `ProductTeam`) and identifier (generally a UUID). The Sort Key (`sk`) that we use is the id of the entity itself. We inject 2 columns into the row of each entity during writing and do not display on the domain classes themselves. These are `row_type` and `root`

The table is structured as below. (For purposes of clarity extra "entity specific" attributes have been left out.)

|    PK     |     SK      |      row_type      |    Id     |      name      |            created_on            | updated_on | deleted_on | status |  pk_read_1  |  sk_read_1  | pk_read_2 |  sk_read_2  | root  |
| :-------: | :---------: | :----------------: | :-------: | :------------: | :------------------------------: | :--------: | :--------: | :----: | :---------: | :---------: | :-------: | :---------: | :---: |
| PT#12345  |  PT#12345   |    product_team    |   12345   | A Product Team | 2025-01-30T14:30:18.191643+00:00 |    null    |    null    | active |  PT#12345   |  PT#12345   | ORG#AB123 |  PT#12345   | true  |
| PT#12345  | P#P.123-XYZ |      product       | P.123-XYZ |   A product    | 2025-01-30T14:30:18.191643+00:00 |    null    |    null    | active | P#P.123-XYZ | P#P.123-XYZ | ORG#AB123 | P#P.123-XYZ | true  |
| PT#FOOBAR |  PT#FOOBAR  | product_team_alias |   12345   | A Product Team | 2025-01-30T14:30:18.191643+00:00 |    null    |    null    | active |  PT#FOOBAR  |  PT#FOOBAR  |   NULL    |    NULL     | false |

Product Teams can additionally be indexed by any keys (see [Domain models](#domain-models)) that they have. For a key in an domain object, that is of type product_team_id,
a copy is made in the database with the index being that key, rather
than the object's identifier. Such copies are referred to as non-root
objects, whereas the "original" (indexed by identifier) is referred to
as the root object.

#### Read/search interface

We have implemented 2 Global Secondary Indexes (GSI) for attributes named `pk_read_1`, `sk_read_1`, `pk_read_2` and `sk_read_2`. The pattern that is place is as follows:

A `read` and `search` is available on all `Repository` patterns (almost) for free (the base `_read` and `_search` require a shallow wrapper).

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

## Deployment

### Create a Release branch

When requested by QA

- Create a release branch using the make command described in the previous section
- Create a new changelog file with the correct date in the changelog directory. (Follow the patterns used in previous files.)
- merge the required branches through the command line into the release branch. i.e. `git merge origin/feature/PI-123-A_branch_for_qa`
- commit and push the release branch to github and create a PR.
- Use the workflow on the #platforms-connecting-party-manager Slack channel to notify of the new release branch.

### After QA has approved the changes

QA should approve the release branch PR and notify developers on the #platforms-connecting-party-manager slack channel of a request to merge the release branch.

- Merge the release branch within the github UI. This will merge the release and close any feature branches that are associated with it.
- Reply to the QA notification on slack that its has been merged and to rebase. Make sure this reply also appears on the main feed. `Merged, rebase rebase :alert:` is usually enough.
- Now we need to deploy to all environments.
- In the github UI, navigate to the actions tab Select `Deploy: Workspace - Nonprod` and select the dropdown `Run workflow`
- Select the `Tag` to deploy (This is the release branch that has just been merged.)
- Select the Account to deploy to as well as if it should be the sandbox or not.
- You must do this for all the environments.
- Now navigate to the `Deploy: Workspace - Production` on the left
- Run workflow. Select the Tag to deploy and Run.
- In production you will need to approve the deployment once the terraform plan has run. All other environments will deploy until finish without any user interaction.
- Once all environments are deployed successfully you can move any Jira tickets to "Done"

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

The Spec is also available on the NHS API Catalogue.

`https://digital.nhs.uk/developer/api-catalogue/connecting-party-manager/content`

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
