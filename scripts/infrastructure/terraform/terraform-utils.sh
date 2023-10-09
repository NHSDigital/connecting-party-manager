#!/bin/bash

source terraform-contstants.sh

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
    elif [ "$environment" = "int" ] || [ "$environment" = "uat" ] || [ "$environment" = "int-sandbox" ]; then
        echo "${TEST_ACCOUNT_ID_LOCATION}"
    else
        echo "${DEV_ACCOUNT_ID_LOCATION}"
    fi
}

function _get_aws_account_id() {
    local account_id_location
    account_id_location=$(_get_account_id_location "$1")
    aws secretsmanager get-secret-value --secret-id "$account_id_location" --query SecretString --output text
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
    elif [ "$environment" = "int" ] || [ "$environment" = "uat" ] || [ "$environment" = "int-sandbox" ]; then
        vars_prefix="uat"
    fi

    echo "${dir}/infrastructure/terraform/etc/${vars_prefix}.tfvars"
}

function _get_terraform_dir() {
  local env=$1
  local account_wide=$2
  local dir=$(pwd)
  if [ "$RUNNING_IN_CI" = 1 ]; then
    echo "$root/terraform/per_workspace"
  elif [ "$account_wide" = "account_wide" ]; then
    echo "$root/terraform/per_account/$env"
  else
    echo "${dir}/terraform/per_workspace"
  fi
}
