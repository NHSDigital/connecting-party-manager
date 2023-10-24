#!/bin/bash

source ./scripts/infrastructure/terraform/terraform-constants.sh
PERSISTENT_WORKSPACES=("dev" "ref" "int" "prod" "dev-sandbox" "int-sandbox" "ref-sandbox")

function _get_workspace_name() {
  local workspace=$1

  if [[ -z $workspace ]]; then
    if [[ -z $TERRAFORM_LOCAL_WORKSPACE_OVERRIDE ]]; then
      echo "$(whoami | openssl dgst -sha1 -binary | xxd -p | cut -c1-8)"
    else
      echo "$TERRAFORM_LOCAL_WORKSPACE_OVERRIDE"
    fi
  else
    echo "$workspace"
  fi
}

function _get_workspace_type() {
  local env=$1
  if [ "$RUNNING_IN_CI" = 1 ]; then
    if [[ ${PERSISTENT_WORKSPACES[@]} =~ $env ]]; then
      echo "PERSISTENT"
    else
      echo "CI"
    fi
  else
    echo "LOCAL"
  fi
}

function _get_workspace_expiration() {
  local env=$1
  if [ "$RUNNING_IN_CI" = 1 ]; then
    if [ ${PERSISTENT_WORKSPACES[@]} =~ $env ]]; then
      echo "NEVER"
    else
      echo "168"
    fi
  else
    echo "72"
  fi
}

function _get_account_id_location() {
    local workspace=$1

    if [ "$RUNNING_IN_CI" = 1 ]; then
        ## DELETE THIS WHEN TEST ACCOUNT ENABLED
        echo "${DEV_ACCOUNT_ID_LOCATION}"
        ## UNCOMMENT THIS WHEN TEST ACCOUNT ENABLED
        # echo "${TEST_ACCOUNT_ID_LOCATION}"     # CI deployments to TEST by default
    elif [ "$workspace" = "mgmt" ]; then
        echo "${MGMT_ACCOUNT_ID_LOCATION}"
    elif [ "$workspace" = "prod" ]; then
        echo "${PROD_ACCOUNT_ID_LOCATION}"
    elif [ "$workspace" = "ref" ] || [ "$workspace" = "ref-sandbox" ]; then
        echo "${TEST_ACCOUNT_ID_LOCATION}"
    elif [ "$workspace" = "int" ] || [ "$workspace" = "int-sandbox" ]; then
        echo "${TEST_ACCOUNT_ID_LOCATION}"
    else
        echo "${DEV_ACCOUNT_ID_LOCATION}"
    fi
}

function _get_contact_information(){
  echo $(aws account get-contact-information --region "${AWS_REGION_NAME}")
}

function _get_aws_account_id() {
    local account_id_location
    local profile_info
    account_id_location=$(_get_account_id_location "$1")
    profile_info="--profile nhse-cpm-mgmt-admin"
    if [ "$RUNNING_IN_CI" = 1 ]; then
      profile_info=""
    fi
    aws secretsmanager get-secret-value --secret-id "$account_id_location" --query SecretString --output text ${profile_info}
}

function _get_workspace_vars_file() {
    local dir=$(pwd)
    local workspace=$1
    local vars_prefix="dev"

    if [ "$RUNNING_IN_CI" = 1 ]; then
        ## DELETE THIS WHEN TEST ACCOUNT ENABLED
        vars_prefix="dev"
        ## UNCOMMENT THIS WHEN TEST ACCOUNT ENABLED
        #vars_prefix="test"
    elif [ "$workspace" = "mgmt" ]; then
        vars_prefix="mgmt"
    elif [ "$workspace" = "prod" ]; then
        vars_prefix="prod"
    elif [ "$workspace" = "ref" ] || [ "$workspace" = "ref-sandbox" ]; then
        vars_prefix="test"
    elif [ "$workspace" = "int" ] || [ "$workspace" = "int-sandbox" ]; then
        vars_prefix="test"
    fi

    echo "${dir}/infrastructure/terraform/etc/${vars_prefix}.tfvars"
}

function _get_terraform_dir() {
  local env=$1
  local account_wide=$2
  local dir=$(pwd)
  if [ "$RUNNING_IN_CI" = 1 ]; then
    echo "${dir}/infrastructure/terraform/per_workspace"
  elif [ "$account_wide" = "account_wide" ]; then
    echo "${dir}/infrastructure/terraform/per_account/$env"
  elif [ "$account_wide" = "non_account_wide" ]; then
    echo "${dir}/infrastructure/terraform/per_workspace"
  else
    echo "<account_wide> must either be 'non_account_wide' or 'account_wide'"
    return 1
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
