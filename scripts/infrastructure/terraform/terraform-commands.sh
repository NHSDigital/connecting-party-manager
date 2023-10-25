#!/bin/bash

source ./scripts/infrastructure/terraform/terraform-utils.sh

TERRAFORM_COMMAND="$1"
TERRAFORM_WORKSPACE="$2"
ACCOUNT_WIDE="$3"
PARAMETER_DEPLOY="$4"
TERRAFORM_ARGS="$5"
AWS_REGION_NAME="eu-west-2"

function _terraform() {
    local workspace
    local aws_account_id
    local var_file
    local current_date
    local terraform_dir
    local expiration_time
    local terraform_role_name="NHSDeploymentRole"
    workspace=$(_get_workspace_name $TERRAFORM_WORKSPACE) || return 1
    aws_account_id=$(_get_aws_account_id "$workspace") || return 1
    if [ "$RUNNING_IN_CI" = 1 ]; then
        # Ask Github Actions to mask the Account ID in the logs
        echo "::add-mask:: ${aws_account_id}"
    fi

    var_file=$(_get_workspace_vars_file "$workspace") || return 1
    terraform_dir=$(_get_terraform_dir "$workspace" "$ACCOUNT_WIDE" "$PARAMETER_DEPLOY")
    if [ $? -gt 0 ]; then
        echo ${terraform_dir}
        return 1
    fi
    workspace_type=$(_get_workspace_type "$workspace")
    workspace_expiration=$(_get_workspace_expiration "$workspace")
    expiration_date=$(_get_expiration_date "$workspace_expiration")
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
            _terraform_plan "$workspace" "$var_file" "$plan_file" "$aws_account_id" "$ACCOUNT_WIDE" "$TERRAFORM_ARGS"
        ;;
        #----------------
        "apply")
            if [[ "${contact_info}" != *MGMT* ]]; then
                echo "Please log in as the mgmt account" >&2
                return 1
            fi

            cd "$terraform_dir" || return 1
            _terraform_apply "$workspace" "$plan_file" "$ACCOUNT_WIDE" "$TERRAFORM_ARGS"
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
            _terraform_destroy "$workspace" "$var_file" "$aws_account_id" "$ACCOUNT_WIDE" "$TERRAFORM_ARGS"
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
    local account_wide=$5
    local args=${@:6}


    terraform init || return 1
    terraform workspace select "$workspace" || terraform workspace new "$workspace" || return 1

    if [[ "${account_wide}" = "account_wide" ]]; then
        terraform plan \
            -out="$plan_file" \
            -var-file="$var_file" \
            -var "assume_account=${aws_account_id}" \
            -var "assume_role=${terraform_role_name}" \
            -var "updated_date=${current_date}" \
            -var "expiration_date=${expiration_date}" || return 1
    else
        terraform plan \
            -out="$plan_file" \
            -var-file="$var_file" \
            -var "assume_account=${aws_account_id}" \
            -var "assume_role=${terraform_role_name}" \
            -var "updated_date=${current_date}" \
            -var "expiration_date=${expiration_date}" \
            -var "lambdas=${lambdas}" \
            -var "workspace_type=${workspace_type}" \
            -var "layers=${layers}"  || return 1
    fi
}

function _terraform_apply() {
    local workspace=$1
    local plan_file=$2
    local account_wide=$3
    local args=${@:4}

    terraform init || return 1
    terraform workspace select "$workspace" || terraform workspace new "$workspace" || return 1
    terraform apply $args "$plan_file" || return 1
    terraform output -json > output.json || return 1
}

function _terraform_destroy() {
    local workspace=$1
    local var_file=$2
    local aws_account_id=$3
    local account_wide=$4
    local args=${@:5}

    terraform init -reconfigure || return 1
    terraform workspace select "$workspace" || terraform workspace new "$workspace" || return 1

    if [[ "${account_wide}" = "account_wide" ]]; then
        terraform destroy \
            -var-file="$var_file" \
            -var "assume_account=${aws_account_id}" \
            -var "assume_role=${terraform_role_name}" \
            $args || return 1
    else
        terraform destroy \
            -var-file="$var_file" \
            -var "assume_account=${aws_account_id}" \
            -var "assume_role=${terraform_role_name}" \
            -var "workspace_type=${workspace_type}" \
            -var "lambdas=${lambdas}" \
            -var "layers=${layers}" \
            $args || return 1
    fi

    if [ "$workspace" != "default" ]; then
        terraform workspace select default || return 1
        terraform workspace delete "$workspace" || return 1
    fi
}

function _terraform_unlock() {
    terraform force-unlock "$workspace"
}

_terraform $@
