#!/bin/bash

source ./scripts/infrastructure/terraform/terraform-constants.sh
source ./scripts/infrastructure/terraform/terraform-utils.sh

TERRAFORM_COMMAND="$1"
TERRAFORM_ENVIRONMENT="$2"
TERRAFORM_ACCOUNT_WIDE="$3"
TERRAFORM_ARGS="$4"
AWS_REGION_NAME="eu-west-2"

function _terraform() {
    local account_wide=$3
    local env
    local aws_account_id
    local var_file
    local current_date
    local terraform_dir
    local expiration_time
    env=$(_get_environment_name $TERRAFORM_ENVIRONMENT)
    aws_account_id=$(_get_aws_account_id "$env")
    var_file=$(_get_environment_vars_file "$env")
    terraform_dir=$(_get_terraform_dir "$env" "$TERRAFORM_ACCOUNT_WIDE")
    workspace_type=$(_get_workspace_type)
    workspace_expiration=$(_get_workspace_expiration)
    expiration_date=$(_get_expiration_date "$workspace_expiration")
    current_date=$(_get_current_date)
    layers=$(_get_layer_list)
    lambdas=$(_get_lambda_list)
    local plan_file="./tfplan"
    # local ci_log_bucket="${PROFILE_PREFIX}--mgmt--github-ci-logging"

    case $TERRAFORM_COMMAND in
        #----------------
        "validate")
            cd "$terraform_dir" || return 1
            terraform validate || return 1
        ;;
        #----------------
        "init")
            if [[ "$(aws account get-contact-information --region "${AWS_REGION_NAME}")" != *MGMT* ]]; then
                echo "Please log in as the mgmt account" >&2
                return 1
            fi

            cd "$terraform_dir" || return 1
            _terraform_init "$env" "$TERRAFORM_ARGS"
        ;;
        #----------------
        "plan")
            if [[ "$(aws account get-contact-information --region "${AWS_REGION_NAME}")" != *MGMT* ]]; then
                echo "Please log in as the mgmt account" >&2
                return 1
            fi

            cd "$terraform_dir" || return 1
            _terraform_plan "$env" "$var_file" "$plan_file" "$aws_account_id"
        ;;
        #----------------
        "apply")
            if [[ "$(aws account get-contact-information --region "${AWS_REGION_NAME}")" != *MGMT* ]]; then
                echo "Please log in as the mgmt account" >&2
                return 1
            fi

            cd "$terraform_dir" || return 1
            _terraform_apply "$env" "$plan_file"
        ;;
        #----------------
        "destroy")
            if [[ "$(aws account get-contact-information --region "${AWS_REGION_NAME}")" != *MGMT* ]]; then
                echo "Please log in as the mgmt account" >&2
                return 1
            fi

            if [[ -z ${env} ]]; then
                echo "Non-mgmt parameter required" >&2
                return 1
            fi

            cd "$terraform_dir" || return 1
            _terraform_destroy "$env" "$var_file" "$aws_account_id"
        ;;
    esac
}
function _terraform_init() {
    local env=$1
    local args=${@:2}

    terraform init $args || return 1
    terraform workspace select "$env" || terraform workspace new "$env" || return 1
}

function _terraform_plan() {
    local env=$1
    local var_file=$2
    local plan_file=$3
    local aws_account_id=$4
    local args=${@:5}


    terraform init || return 1
    terraform workspace select "$env" || terraform workspace new "$env" || return 1
    terraform plan \
        -out="$plan_file" \
        -var-file="$var_file" \
        -var "assume_account=${aws_account_id}" \
        -var "assume_role=${TERRAFORM_ROLE_NAME}" \
        -var "updated_date=${current_date}" \
        -var "expiration_date=${expiration_date}" \
        -var "lambdas=${lambdas}" \
        -var "workspace_type=${workspace_type}" \
        -var "layers=${layers}"  || return 1
}

function _terraform_apply() {
    local env=$1
    local plan_file=$2
    local args=${@:4}

    terraform workspace select "$env" || terraform workspace new "$env" || return 1
    terraform apply $args "$plan_file" || return 1
    terraform output -json > output.json || return 1
}

function _terraform_destroy() {
  local env=$1
  local var_file=$2
  local aws_account_id=$3
  local args=${@:4}

  terraform workspace select "$env" || terraform workspace new "$env" || return 1
  terraform destroy \
    -var-file="$var_file" \
    -var "assume_account=${aws_account_id}" \
    -var "assume_role=${TERRAFORM_ROLE_NAME}" \
    -var "workspace_type=${workspace_type}" \
    -var "lambdas=${lambdas}" \
    -var "layers=${layers}" \
    $args || return 1
  if [ "$env" != "default" ]; then
    terraform workspace select default || return 1
    terraform workspace delete "$env" || return 1
  fi
}

_terraform $@
