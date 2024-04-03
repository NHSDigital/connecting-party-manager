# Connecting Party Manager

## Overview

## Table of Contents

1. [Setup](#setup)
   1. [Prerequisites](#prerequisites)
   2. [Project build](#project-build)
   3. [AWS SSO Setup](#aws-sso-setup)
   4. [Other helpful commands](#other-helpful-commands)
2. [Tests](#tests)
3. [Workflow](#workflow)
4. [FHIR, Swagger and FHIR Pydantic models](#fhir-swagger-and-fhir-pydantic-models)

---

## Setup

### Prerequisites

We use `asdf` to fetch the required versions of prerequisite libraries instead of your system's default version. To get it up and running go to https://asdf-vm.com/guide/getting-started.html. You can check it installed properly by using the command `asdf --version`.

If you are using `pyenv` (you can check by typing `pyenv` and seeing whether it returns a nice list of commands) then you should run:

```
pyenv install $(cat .python-version)
```

Additionally you will need `wget` (doing `which wget` will return blank if not installed). Please Google "how to install wget on my operating system", if you don't already have this installed.

Otherwise `asdf` should do the work for you.

### Project build

Do `make build` every time you would like to pick up and install new local/project dependencies and artifacts. This will always detect changes to:

- `.tool-versions` (project prerequisites)
- `pyproject.toml` (python dependencies)
- non-development files in the `src` directory

The first time it will also set up your pre-commit hooks.

### Proxygen

We use [Proxygen](https://github.com/NHSDigital/proxygen-cli) to deploy our proxies and specs to APIM which we have wrapped up into a make command:

- `make apigee-deploy`

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
make terraform--plan TERRAFORM_WORKSPACE="<YOUR_SHORTCODE_AND_JIRA_NUMBER>" # Will attempt to build the project first
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

## Updating Roles

We have several roles that we currently handle outside of terraform as its needed to deploy the terraform:

-

To update any of the roles used for SSO then you need to do the following command which should prompt you to log in via SSO:

`make manage--non-mgmt-policies MGMT_ACCOUNT_ID=<ID> SSO_PROFILE="dev-admin"`

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

In order to run these you can do one of::

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

## FHIR, Swagger and FHIR Pydantic models

This is all done by `make build`. For more details on how to update the Swagger and FHIR Pydantic models, please see [the swagger README](infrastructure/swagger/README.md).

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

Before running the bulk trigger, you need to clear the initial ETL state, do:

```
make etl--clear-state
```
