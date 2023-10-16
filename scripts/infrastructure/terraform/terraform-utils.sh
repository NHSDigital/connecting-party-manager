#!/bin/bash

source ./scripts/infrastructure/terraform/terraform-constants.sh

function _get_environment_name() {
  local environment=$1

  if [[ -z $environment ]]; then
    if [[ -z $TERRAFORM_LOCAL_WORKSPACE_OVERRIDE ]]; then
      echo "$(whoami | openssl dgst -sha1 -binary | xxd -p | cut -c1-8)"
    else
      echo "$TERRAFORM_LOCAL_WORKSPACE_OVERRIDE"
    fi
  else
    echo "$environment"
  fi
}

function _get_workspace_type() {
    if [ "$RUNNING_IN_CI" = 1 ]; then
      if [ "$CI_DEPLOY_PERSISTENT_ENV" != 1]; then
        echo "CI"
      else
        echo "PERSISTENT"
      fi
    else
      echo "LOCAL"
    fi
}

function _get_workspace_expiration() {
    if [ "$RUNNING_IN_CI" = 1 ]; then
      if [ "$CI_DEPLOY_PERSISTENT_ENV" != 1]; then
        echo "168"
      else
        echo "NEVER"
      fi
    else
      echo "72"
    fi
}

function _get_account_id_location() {
    local environment=$1

    if [ "$RUNNING_IN_CI" = 1 ] && [ "$CI_DEPLOY_PERSISTENT_ENV" != 1 ]; then
        echo "${TEST_ACCOUNT_ID_LOCATION}"     # CI deployments to TEST by default
    elif [ "$environment" = "mgmt" ]; then
        echo "${MGMT_ACCOUNT_ID_LOCATION}"
    elif [ "$environment" = "prod" ]; then
        echo "${PROD_ACCOUNT_ID_LOCATION}"
    elif [ "$environment" = "ref" ] || [ "$environment" = "test" ] || [ "$environment" = "ref-sandbox" ]; then
        echo "${TEST_ACCOUNT_ID_LOCATION}"
    elif [ "$environment" = "int" ] || [ "$environment" = "int-sandbox" ]; then
        echo "${TEST_ACCOUNT_ID_LOCATION}"
    else
        echo "${DEV_ACCOUNT_ID_LOCATION}"
    fi
}

function _get_aws_account_id() {
    local account_id_location
    account_id_location=$(_get_account_id_location "$1")
    aws secretsmanager get-secret-value --secret-id "$account_id_location" --query SecretString --output text --profile nhse-cpm-mgmt-admin
}

function _get_environment_vars_file() {
    local dir=$(pwd)
    local environment=$1
    local vars_prefix="dev"

    if [ "$RUNNING_IN_CI" = 1 ] && [ "$CI_DEPLOY_PERSISTENT_ENV" != 1 ]; then
        vars_prefix="test"
    elif [ "$environment" = "mgmt" ]; then
        vars_prefix="mgmt"
    elif [ "$environment" = "prod" ]; then
        vars_prefix="prod"
    elif [ "$environment" = "ref" ] || [ "$environment" = "test" ] || [ "$environment" = "ref-sandbox" ]; then
        vars_prefix="test"
    elif [ "$environment" = "int" ] || [ "$environment" = "int-sandbox" ]; then
        vars_prefix="uat"
    fi

    echo "${dir}/infrastructure/terraform/etc/${vars_prefix}.tfvars"
}

function _get_terraform_dir() {
  local env=$1
  local account_wide=$2
  local dir=$(pwd)
  if [ "$RUNNING_IN_CI" = 1 ]; then
    echo "$root/infrastructure/terraform/per_workspace"
  elif [ "$account_wide" = "account_wide" ]; then
    echo "$root/infrastructure/terraform/per_account/$env"
  else
    echo "${dir}/infrastructure/terraform/per_workspace"
  fi
}

function _get_current_date() {
    local timestamp=$(python -c "from datetime import datetime, timedelta, timezone; print(format(datetime.now(timezone.utc), '%Y-%m-%dT%H:%M:%SZ'))")
    echo "${timestamp}"
}

function _get_expiration_date() {
    local offset=$1
    if [ "$offset" != "NEVER" ]; then
      local timestamp=$(python -c "from datetime import datetime, timedelta, timezone; print(format(datetime.now(timezone.utc) + timedelta(hours=${offset}), '%Y-%m-%dT%H:%M:%SZ'))")
      echo "${timestamp}"
    else
      echo "${offset}"
    fi
}

function _get_layer_list() {
    local dir=$(pwd)
    local layers=$(find "$(pwd)/src/layers" -maxdepth 1 -mindepth 1 -type d -exec basename {} \; | jq -R -s -c 'split("\n")[:-1]')
    echo $layers
}

function _get_lambda_list() {
    local dir=$(pwd)
    local lambdas=$(find "$(pwd)/src/api" -maxdepth 1 -mindepth 1 -type d -exec basename {} \; | jq -R -s -c 'split("\n")[:-1]')
    echo $lambdas
}
