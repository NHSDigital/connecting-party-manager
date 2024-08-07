set -e

PATH_TO_HERE="scripts/infrastructure/apigee"
APIGEE_DEPLOYMENT_ROLE="NHSDeploymentRole"

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

function get_workspace_name(){
    jq -r '.workspace.value' ${WORKSPACE_OUTPUT_JSON}
}

function get_aws_environment(){
    jq -r '.environment.value' ${WORKSPACE_OUTPUT_JSON}
}


# connecting-party-manager--internal-dev--cpm-rel-2024-08-05-ae44973--app-level0

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

function get_access_token(){
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
    _product_name="connecting-party-manager--$_apigee_environment--cpm-$_workspace_name--app-level0"
    _secret_name="$_aws_environment--apigee-app-client-info"

        echo "
    Attaching product
    -------------------- ----------------------------------------
    workspace_name        ${_workspace_name}
    aws_environment       ${_aws_environment}
    apigee_environment    ${_apigee_environment}
"
    client_parameters=$(aws ssm get-parameter --name "apigee-app-client-info" --with-decryption --query "Parameter.Value" --output text)
    client_id=$(echo "$client_parameters" | jq -r '.client_id')
    client_secret=$(echo "$client_parameters" | jq -r '.client_secret')
    client_key=$(echo "$client_parameters" | jq -r '.client_key')
    email_that_owns_app="rowan.gill1@nhs.net"
    app_name="CPM%20PTL" # Next time it might be worth to not have the space in there haha

    _access_token=$(get_access_token ${client_id} ${client_secret})

    app_product=$(curl -X POST \
        https://api.enterprise.apigee.com/v1/o/$_org_name/developers/$email_that_owns_app/apps/CPM%20PTL/keys/$client_key \
        -H "Authorization: Bearer $_access_token" \
        -H "Content-type:application/json" \
        -d "{\"apiProducts\": [\"$_product_name\"]}")

    # add_product_response=$(curl -s -X POST \
    #   "https://api.enterprise.apigee.com/v1/organizations/$_org_name/apps/$_app_id" \
    #   -H "Authorization: Bearer $_access_token" \
    #   -H "Content-Type: application/json" \
    #   -d "{\"apiProducts\": [\"$_product_name\"]}")

    if [[ "$add_product_response" == *"\"status\": \"error\""* ]]; then
      echo "Failed to add product to the app"
      echo "Response: $add_product_response"
      exit 1
    else
      echo "Product added successfully!"
    fi
}

# Expose functions publicly
$@
