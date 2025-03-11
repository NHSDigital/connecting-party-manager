set -e

source ./scripts/infrastructure/terraform/terraform-utils.sh
source ./scripts/infrastructure/terraform/terraform-constants.sh

PATH_TO_HERE="scripts/infrastructure/apigee"
APIGEE_DEPLOYMENT_ROLE="NHSDeploymentRole"
PERSISTENT_ENVIRONMENT_BUILD="${2:-false}"
API_NAME="connecting-party-manager"



if [[ -z ${WORKSPACE_OUTPUT_JSON} ]]; then
    echo "WORKSPACE_OUTPUT_JSON not set"
    exit 1
fi

if [[ -z ${ENVIRONMENT_MAPPING_YAML} ]]; then
    echo "ENVIRONMENT_MAPPING_YAML not set"
    exit 1
fi

if [[ -z ${STAGE_MAPPING_YAML} ]]; then
    echo "STAGE_MAPPING_YAML not set"
    exit 1
fi

if [[ -z ${APIGEE_CONFIG_PATH} ]]; then
    echo "APIGEE_CONFIG_PATH not set"
    exit 1
fi

function get_workspace_name(){
    jq -r '.workspace.value' ${WORKSPACE_OUTPUT_JSON}
}

function get_aws_environment(){
    jq -r '.environment.value' ${WORKSPACE_OUTPUT_JSON}
}

function get_apigee_environment(){
    workspace_name=${1}
    aws_environment=${2}

    _scoped_environment=${aws_environment}
    if [[ ${workspace_name} == "${aws_environment}-sandbox" ]]; then
        _scoped_environment=${workspace_name}
    fi

    apigee_environment=$(yq ".${_scoped_environment}" ${ENVIRONMENT_MAPPING_YAML})
    if [[ ${apigee_environment} == "null" ]]; then
        # Default to internal-dev if not named in ${ENVIRONMENT_MAPPING_YAML}
        echo "internal-dev"
    else
        echo ${apigee_environment}
    fi
}

function get_apigee_stage(){
    workspace_name=${1}
    apigee_stage=$(yq ".${workspace_name}" ${STAGE_MAPPING_YAML})
    if [[ ${apigee_stage} == "null" ]]; then
        # Default to ptl if not named in ${STAGE_MAPPING_YAML}
        echo "ptl"
    else
        echo ${apigee_stage}
    fi
}

function get_access_token(){
    client_id=${1}
    client_secret=${2}
    token_url='https://login.apigee.com/oauth/token'

    access_token=$(curl -s -X POST "$token_url" \
        -u "$client_id:$client_secret" \
        -d 'grant_type=client_credentials' | jq -r '.access_token')

    if [ "$access_token" == "null" ] || [ -z "$access_token" ]; then
      echo "Failed to obtain access token"
      exit 1
    else
      echo ${access_token}
    fi
}

function attach_product(){
    _workspace_name=$(get_workspace_name)
    _aws_environment=$(get_aws_environment)
    _apigee_environment=$(get_apigee_environment ${_workspace_name} ${_aws_environment})
    # Written to only initially add products for PRs
    _org_name="nhsd-nonprod"
    # Currently hardcoded to CPM PTL id for PR running purposes, could be passed in for adjusting other apps in the future
    _app_id="9d28b416-311b-4523-bda9-686baa2fc437"

    if [ "$PERSISTENT_ENVIRONMENT_BUILD" = "false" ]; then
        API_NAME=$_workspace_name
    fi

    _product_name="connecting-party-manager--$_apigee_environment--$API_NAME--app-level0"
    _secret_name="$_aws_environment--apigee-app-client-info"
    _apigee_stage=$(get_apigee_stage ${_workspace_name})
    external_id_secret_name="nhse-cpm--mgmt--${_aws_environment}-external-id"
    external_id=$(aws secretsmanager get-secret-value --secret-id $external_id_secret_name --query SecretString --output text)



    echo "
    Attaching product
    -------------------- ----------------------------------------
    workspace_name        ${_workspace_name}
    aws_environment       ${_aws_environment}
    apigee_environment    ${_apigee_environment}
    product_name          ${_product_name}
    secret_name           ${_secret_name}
    "

    terraform_role_name=NHSDeploymentRole
    account_to_assume=$(_get_aws_account_id "$_aws_environment" "$PROFILE_PREFIX" "$VERSION")
    role_arn="arn:aws:iam::${account_to_assume}:role/${terraform_role_name}"
    session_name="attach-product-session"
    duration_seconds=900

    assume_role_output=$(aws sts assume-role --role-arn "$role_arn" --role-session-name "$session_name" --external-id "$external_id" --duration-seconds "$duration_seconds")
    # Check if the assume-role command was successful
    if [ $? -eq 0 ]; then

            # Download the pem file if it does not exist
        if [ ! -f "${APIGEE_CONFIG_PATH}/${_apigee_stage}/.proxygen/private_key.pem" ]; then
            poetry run python ${PATH_TO_HERE}/download_pem.py ${_apigee_stage} ${APIGEE_DEPLOYMENT_ROLE}
        fi

        access_key=$(echo "$assume_role_output" | jq -r '.Credentials.AccessKeyId')
        secret_key=$(echo "$assume_role_output" | jq -r '.Credentials.SecretAccessKey')
        session_token=$(echo "$assume_role_output" | jq -r '.Credentials.SessionToken')
        export AWS_ACCESS_KEY_ID="$access_key"
        export AWS_SECRET_ACCESS_KEY="$secret_key"
        export AWS_SESSION_TOKEN="$session_token"

        client_parameters=$(aws secretsmanager get-secret-value --secret-id $_secret_name --query SecretString --output text)
        client_id=$(echo "$client_parameters" | jq -r '.client_id')
        email_that_owns_app="rowan.gill1@nhs.net"
        app_name="CPM%20PTL" # Next time it might be worth to not have the space in there haha

        token_response=$(DOT_PROXYGEN=${APIGEE_CONFIG_PATH}/${_apigee_stage} \
            poetry run \
            python ${PATH_TO_HERE}/proxygen.py pytest-nhsd-apim \
            get-token)

        token=$(echo "$token_response" | jq -r '.pytest_nhsd_apim_token')
        url=https://api.enterprise.apigee.com/v1/organizations/$_org_name/developers/$email_that_owns_app/apps/$app_name/keys/$client_id

        add_product_response=$(curl --retry 100 -sS -X POST \
            $url \
            -H "Authorization: Bearer $token" \
            -H "Content-type:application/json" \
            -d "{\"apiProducts\": [\"$_product_name\"]}")

        status=$(echo "$add_product_response" | jq -r '.status')
        if [ -z "$status" ] || [ "$status" != "approved" ]; then
          echo "Failed to add product to the app"
          echo "Response: $add_product_response"
          exit 1
        else
          echo "Product added successfully!"
        fi
    else
        # Print an error message if assume-role command fails
        echo "Error executing aws sts assume-role command"
    fi
}

function detach_product(){
    _workspace_name=$(get_workspace_name)
    _aws_environment=$(get_aws_environment)
    _apigee_environment=$(get_apigee_environment ${_workspace_name} ${_aws_environment})
    # Written to only initially add products for PRs
    _org_name="nhsd-nonprod"
    # Currently hardcoded to CPM PTL id for PR running purposes, could be passed in for adjusting other apps in the future
    _app_id="9d28b416-311b-4523-bda9-686baa2fc437"

    if [ "$PERSISTENT_ENVIRONMENT_BUILD" = "false" ]; then
        API_NAME=$_workspace_name
    fi

    _product_name="connecting-party-manager--$_apigee_environment--$API_NAME--app-level0"
    _secret_name="$_aws_environment--apigee-app-client-info"
    _apigee_stage=$(get_apigee_stage ${_workspace_name})
    external_id_secret_name="nhse-cpm--mgmt--${_aws_environment}-external-id"
    external_id=$(aws secretsmanager get-secret-value --secret-id $external_id_secret_name --query SecretString --output text)


    echo "
    Detaching product
    -------------------- ----------------------------------------
    workspace_name        ${_workspace_name}
    aws_environment       ${_aws_environment}
    apigee_environment    ${_apigee_environment}
    product_name          ${_product_name}
    secret_name           ${_secret_name}
    "

    terraform_role_name=NHSDeploymentRole
    account_to_assume=$(_get_aws_account_id "$_aws_environment" "$PROFILE_PREFIX" "$VERSION")
    role_arn="arn:aws:iam::${account_to_assume}:role/${terraform_role_name}"
    session_name="attach-product-session"
    duration_seconds=900

    assume_role_output=$(aws sts assume-role --role-arn "$role_arn" --role-session-name "$session_name" --external-id "$external_id" --duration-seconds "$duration_seconds")
    # Check if the assume-role command was successful
    if [ $? -eq 0 ]; then

            # Download the pem file if it does not exist
        if [ ! -f "${APIGEE_CONFIG_PATH}/${_apigee_stage}/.proxygen/private_key.pem" ]; then
            poetry run python ${PATH_TO_HERE}/download_pem.py ${_apigee_stage} ${APIGEE_DEPLOYMENT_ROLE}
        fi

        access_key=$(echo "$assume_role_output" | jq -r '.Credentials.AccessKeyId')
        secret_key=$(echo "$assume_role_output" | jq -r '.Credentials.SecretAccessKey')
        session_token=$(echo "$assume_role_output" | jq -r '.Credentials.SessionToken')
        export AWS_ACCESS_KEY_ID="$access_key"
        export AWS_SECRET_ACCESS_KEY="$secret_key"
        export AWS_SESSION_TOKEN="$session_token"

        client_parameters=$(aws secretsmanager get-secret-value --secret-id $_secret_name --query SecretString --output text)
        client_id=$(echo "$client_parameters" | jq -r '.client_id')
        email_that_owns_app="rowan.gill1@nhs.net"
        app_name="CPM%20PTL" # Next time it might be worth to not have the space in there haha

        token_response=$(DOT_PROXYGEN=${APIGEE_CONFIG_PATH}/${_apigee_stage} \
            poetry run \
            python ${PATH_TO_HERE}/proxygen.py pytest-nhsd-apim \
            get-token)

        token=$(echo "$token_response" | jq -r '.pytest_nhsd_apim_token')
        url=https://api.enterprise.apigee.com/v1/organizations/$_org_name/developers/$email_that_owns_app/apps/$app_name/keys/$client_id/apiproducts/$_product_name

        detach_product_response=$(curl -sS -X DELETE \
            $url \
            -H "Authorization: Bearer $token" \
            -H "Content-type:application/json" \
            -d "{\"apiProducts\": [\"$_product_name\"]}")

        status=$(echo "$detach_product_response" | jq -r '.status')
        if [ -z "$status" ] || [ "$status" != "approved" ]; then
          echo "Failed to remove product from the app"
          echo "Response: $detach_product_response"
          exit 1
        else
          echo "Product removed successfully!"
        fi
    else
        # Print an error message if assume-role command fails
        echo "Error executing aws sts assume-role command"
    fi
}

# Expose functions publicly
$@
