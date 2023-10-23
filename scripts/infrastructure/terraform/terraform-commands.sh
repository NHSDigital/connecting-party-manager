#!/bin/bash

source ./scripts/infrastructure/terraform/terraform-constants.sh
source ./scripts/infrastructure/terraform/terraform-utils.sh

TERRAFORM_COMMAND="$1"
TERRAFORM_WORKSPACE="$2"
TERRAFORM_ACCOUNT_WIDE="$3"
TERRAFORM_ARGS="$4"
AWS_REGION_NAME="eu-west-2"

function _terraform() {
    local account_wide=$3
    local workspace
    local aws_account_id
    local var_file
    local current_date
    local terraform_dir
    local expiration_time
    workspace=$(_get_workspace_name $TERRAFORM_WORKSPACE) || return 1
    aws_account_id=$(_get_aws_account_id "$workspace") || return 1
    if [ "$RUNNING_IN_CI" = 1 ]; then
        # Ask Github Actions to mask the Account ID in the logs
        echo "::add-mask:: ${aws_account_id}"
    fi

    var_file=$(_get_workspace_vars_file "$workspace") || return 1
    terraform_dir=$(_get_terraform_dir "$workspace" "$TERRAFORM_ACCOUNT_WIDE")
    if [ $? -gt 0 ]; then
        echo ${terraform_dir}
        return 1
    fi
    current_date=$(_get_current_date) || return 1
    layers=$(_get_layer_list) || return 1
    lambdas=$(_get_lambda_list) || return 1
    contact_info=$(_get_contact_information) || return 1
    local plan_file="./tfplan"

    case $TERRAFORM_COMMAND in
        #----------------
        "validate")
            cd "$terraform_dir" || return 1
            terraform validate || return 1
        ;;
        #----------------
        "init")
            if [[ "${contact_info}" != *MGMT* ]]; then
                echo "Please log in as the mgmt account" >&2
                return 1
            fi

            cd "$terraform_dir" || return 1
            _terraform_init "$workspace" "$TERRAFORM_ARGS"
        ;;
        #----------------
        "plan")
            if [[ "${contact_info}" != *MGMT* ]]; then
                echo "Please log in as the mgmt account" >&2
                return 1
            fi

            cd "$terraform_dir" || return 1
            _terraform_plan "$workspace" "$var_file" "$plan_file" "$aws_account_id"
        ;;
        #----------------
        "apply")
            if [[ "${contact_info}" != *MGMT* ]]; then
                echo "Please log in as the mgmt account" >&2
                return 1
            fi

            cd "$terraform_dir" || return 1
            _terraform_apply "$workspace" "$plan_file"
        ;;
        #----------------
        "destroy")
            if [[ "${contact_info}" != *MGMT* ]]; then
                echo "Please log in as the mgmt account" >&2
                return 1
            fi

            if [[ -z ${workspace} ]]; then
                echo "Non-mgmt parameter required" >&2
                return 1
            fi

            cd "$terraform_dir" || return 1
            _terraform_destroy "$workspace" "$var_file" "$aws_account_id"
        ;;
        #----------------
        "unlock")
            if [[ "${contact_info}" != *MGMT* ]]; then
                echo "Please log in as the mgmt account" >&2
                return 1
            fi

            cd "$terraform_dir" || return 1
            _terraform_unlock "$workspace"
        ;;
    esac
}
function _terraform_init() {
    local workspace=$1
    local args=${@:2}

    terraform init $args || return 1
    terraform workspace select "$workspace" || terraform workspace new "$workspace" || return 1
}

function _terraform_plan() {
    local workspace=$1
    local var_file=$2
    local plan_file=$3
    local aws_account_id=$4
    local args=${@:5}


    terraform init || return 1
    terraform workspace select "$workspace" || terraform workspace new "$workspace" || return 1
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
    local workspace=$1
    local plan_file=$2
    local args=${@:4}

    terraform workspace select "$workspace" || terraform workspace new "$workspace" || return 1
    terraform apply $args "$plan_file" || return 1
    terraform output -json > output.json || return 1
}

function _terraform_destroy() {
    local workspace=$1
    local var_file=$2
    local aws_account_id=$3
    local args=${@:4}

    terraform init || return 1
    terraform workspace select "$workspace" || terraform workspace new "$workspace" || return 1
    terraform destroy \
        -var-file="$var_file" \
        -var "assume_account=${aws_account_id}" \
        -var "assume_role=${TERRAFORM_ROLE_NAME}" \
        -var "workspace_type=${workspace_type}" \
        -var "lambdas=${lambdas}" \
        -var "layers=${layers}" \
        $args || return 1
    if [ "$workspace" != "default" ]; then
        terraform workspace select default || return 1
        terraform workspace delete "$workspace" || return 1
    fi
}

function _terraform_unlock() {
    terraform force-unlock "$workspace"
}

_terraform $@
