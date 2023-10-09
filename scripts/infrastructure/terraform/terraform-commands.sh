#!/bin/bash

source terraform-constants.sh
source terraform-utils.sh

function _terraform() {
    local command=$1
    local account_wide=$3
    # local env
    # local aws_account_id
    # local var_file
    # local current_timestamp
    local terraform_dir
    env=$(_get_environment_name "$2")
    aws_account_id=$(_get_aws_account_id "$env")
    var_file=$(_get_environment_vars_file "$env")
    terraform_dir=$(_get_terraform_dir "$env" "$account_wide")
    current_timestamp="$(date '+%Y_%m_%d__%H_%M_%S')"
    # local plan_file="./tfplan"
    # local ci_log_bucket="${PROFILE_PREFIX}--mgmt--github-ci-logging"

    case $command in
        # "truststore") _terraform_truststore $env ;;
        #----------------
        "validate")
            cd "$terraform_dir" || return 1
            terraform validate || return 1
        ;;
        #----------------
        # "init")
        #     if [[ "$(aws sts get-caller-identity)" != *mgmt* ]]; then
        #         echo "Please log in as the mgmt account" >&2
        #         return 1
        #     fi

        #     cd "$terraform_dir" || return 1
        #     _terraform_init "$env"
        # ;;
    esac
}

function _terraform_init() {
  local env=$1
  local args=${@:2}

  terraform init $args || return 1
  terraform workspace select "$env" || terraform workspace new "$env" || return 1
}
