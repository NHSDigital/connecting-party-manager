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

This project uses Single Sign On (SSO) for consuming AWS services, please ensure that you have NHS SSO enabled in your browser. You should add the following lines to your `~/.aws/config` file:

```
[profile nhse-cpm-mgmt-admin]
sso_start_url = https://***********.awsapps.com/start#
sso_region = ***********
sso_account_id = ***********
sso_role_name = ***********
region = ***********
```

You can find the above values by asking a team member, or going to the AWS SSO in your browser. To test that you've been set up ok, do:

```
make aws--login
```

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
