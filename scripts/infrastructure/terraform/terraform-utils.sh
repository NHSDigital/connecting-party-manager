#!/bin/bash

source ./scripts/infrastructure/terraform/terraform-constants.sh
PERSISTENT_WORKSPACES=("dev" "qa" "ref" "int" "prod" "dev-sandbox" "int-sandbox" "ref-sandbox")


function _get_account_name() {
  local account=$1
  local workspace=$2

  # if account not specified then infer it
  if [[ -z "$account" ]]; then
    if [[ "$workspace" = "ci-"* ]]; then
      echo "ref" # ci builds go here
    else
      echo "dev" # personal builds co here
    fi
  else
    echo "$account"
  fi
}

function _get_workspace_name() {
  local account=$1
  local workspace=$2

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
  local account=$1
  local workspace=$2

  # persistent environments are where the workspace and account names match (e.g. qa/qa or qa/qa-sandbox)
  if [[ "${workspace}" = "${account}" || "${workspace}" = "${account}-sandbox" ]]; then
    echo "PERSISTENT"
  # CI environments start with 'ci-'
  elif [[ "${workspace}" = "ci-"* ]]; then
    echo "CI"
  # everything else is classified as 'LOCAL'
  else
    echo "LOCAL"
  fi
}

function _get_workspace_expiration() {
  case $1 in
    "PERSISTENT")
      echo "NEVER" ;;
    "CI")
      echo "168" ;;
    *)
      echo "72" ;;
  esac
}

function _get_account_id_location() {
    local account=$1
    local prefix=$2
    local version=$3

    echo "${prefix}--mgmt--${account}-account-id-${version}"
}

function _get_account_full_name(){
  echo $(aws account get-contact-information --region "${AWS_REGION_NAME}" | jq  .ContactInformation.FullName -r)
}

function _get_aws_account_id() {
    local account_id_location
    local profile_info
    account_id_location=$(_get_account_id_location "$1" "$2" "$3")

    aws secretsmanager get-secret-value \
      --secret-id "$account_id_location" \
      --query SecretString \
      --output text
}

function _get_workspace_vars_file() {
    local dir=$(pwd)
    local account=$1

    echo "${dir}/infrastructure/terraform/etc/${account}.tfvars"
}

function _get_terraform_scope() {
  if [[ -z "$TERRAFORM_SCOPE" ]]; then
    echo "per_workspace"
  else
    echo "$TERRAFORM_SCOPE"
  fi
}

function _get_terraform_dir() {
  local scope=$1
  local dir=$(pwd)

  echo "${dir}/infrastructure/terraform/${scope}"
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
