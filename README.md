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
4. [FHIR, Swagger and Pydantic](#fhir-swagger-and-pydantic)

---

## Setup

### Prerequisites

We use `asdf` to fetch the required versions of prerequisite libraries instead of your system's default version. To get it up and running go to https://asdf-vm.com/guide/getting-started.html. You can check it installed properly by using the command `asdf --version`.

If you are using `pyenv` (you can check by typing `pyenv` and seeing whether it returns a nice list of commands) then you should run:

```
pyenv install $(cat .python-version)
```

Otherwise `asdf` should do the work for you.

### Project build

Do `make build` every time you would like to pick up and install new local/project dependencies and artifacts. This will always detect changes to:

- `.tool-versions` (project prerequisites)
- `pyproject.toml` (python dependencies)
- non-development files in the `src` directory

The first time it will also set up your pre-commit hooks.

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

### Build a local workspace on AWS

You can build a working copy of the CPM service in your own workspace within the `dev` environment. To do this follow these steps. (You must have SSO setup on your system and have MGMT admin access)

You must pass a `TERRAFORM_WORKSPACE` variable to each command in the format `YOUR_SHORTCODE_AND_JIRA_NUMBER`. This variable must not contain spaces, but can contain underscores and hyphens. `e.g. jobl3-PI-100`

```shell
make terraform--init TERRAFORM_WORKSPACE="<YOUR_SHORTCODE_AND_JIRA_NUMBER>" # Will attempt to login to AWS first using SSO
make terraform--plan TERRAFORM_WORKSPACE="<YOUR_SHORTCODE_AND_JIRA_NUMBER>" # Will attempt to build the project first
make terraform--apply TERRAFORM_WORKSPACE="<YOUR_SHORTCODE_AND_JIRA_NUMBER>"
```

### Destroy a local workspace on AWS

Destroy the local workspace and it's corresponding state file on mgmt

```shell
make terraform--destroy TERRAFORM_WORKSPACE="<YOUR_SHORTCODE_AND_JIRA_NUMBER>" # Will attempt to login to AWS first using SSO
```

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

## FHIR, Swagger and Pydantic

We have a "swagger merge" routine to generate our OpenAPI 3 spec for the project. This
spec file is used to underpin our API Gateway (via terraform) as well as acting as public
documentation of the REST API.

It is automatically constructed based initially on swagger models from the open source
[FHIR Swagger Generator tool](https://github.com/LinuxForHealth/FHIR/tree/main/
fhir-swagger-generator). You can modify available FHIR endpoints by
editing (our swagger-fhir-generator-definitions/config.yaml)[infrastructure/swagger/
swagger-fhir-generator-definitions/config.yaml]. Updating this file will also
cascade changes to the pydantic models found under the module [domain.fhir.r4](src/layers/
domain/fhir/r4), which are used for parsing and validating FHIR objects.

In general, any other additions to be merged on top of the FHIR swagger definition should be
included under [infrastructure/swagger/](infrastructure/swagger/). The enumerated files
(starting with `00_base.yaml`) indicate the order in which the swagger files are merged (note
`00_base.yaml` is actually the base and the FHIR swagger definitions will be merged on top of
this). Therefore if you want to hook up a new endpoint to a e.g. new FHIR definition, then
you should update `05_paths.yaml` and any other relevant files accordingly.

The generated OpenAPI 3 specs, `infrastructure/swagger/dist/aws` and `infrastructure/swagger/ dist/public`, are automatically validated via the node package `redocly-cli`. Any
intermediate merge steps can be viewed under `infrastructure/swagger/build`. Note that
`infrastructure/swagger/dist/aws` is intended for use with API Gateway (and will be rendered
during the `make terraform--apply` into `infrastructure/swagger/dist/aws/rendered`), whilst
`infrastructure/swagger/dist/public` is intended to be used for public facing documentation.

### How to re/generate the OpenAPI 3 specs

To re/generate the OpenAPI 3 specs and pydantic models after updates to the `swagger-fhir-generator-definitions/config.yaml` or other `infrastructure/swagger` files:

```
make swagger--merge
```

however since this is a dependency of the terraform plan, it is sufficient to run `make terraform--plan` and the OpenAPI 3 specs will be updated accordingly.
