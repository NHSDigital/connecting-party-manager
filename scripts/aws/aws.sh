#!/bin/bash

SSO_CACHE=${HOME}/.aws/sso/cache

# Log in, if not already logged in
aws sts get-caller-identity --profile ${PROFILE} &> /dev/null
if [ $? -gt 0 ]; then
    aws sso login --profile ${PROFILE} &> /dev/null
fi
set -e

# Collect required info to get role credentials
LATEST_SSO_JWT=${SSO_CACHE}/$(ls -t ${SSO_CACHE} | head -1)
ACCESS_TOKEN=$(cat ${LATEST_SSO_JWT} | jq -r '.accessToken')
ACCOUNT_ID=$(aws sts get-caller-identity --profile=${PROFILE} | jq -r '.Account')

# Get the role credentials and share them with the shell
CREDENTIALS=$(aws sso get-role-credentials \
    --profile=${PROFILE} \
    --role-name=${ROLE_NAME} \
    --access-token=${ACCESS_TOKEN} \
    --account-id=${ACCOUNT_ID}
)

AWS_ACCESS_KEY_ID=$(echo -n ${CREDENTIALS} | jq -r '.roleCredentials.accessKeyId')
AWS_SECRET_ACCESS_KEY=$(echo -n ${CREDENTIALS} | jq -r '.roleCredentials.secretAccessKey')
AWS_SESSION_TOKEN=$(echo -n ${CREDENTIALS} | jq -r '.roleCredentials.sessionToken')
AWS_SESSION_EXPIRY=$(echo -n ${CREDENTIALS} | jq -r '.roleCredentials.expiration')

echo -n "AWS_ACCESS_KEY_ID:=${AWS_ACCESS_KEY_ID} AWS_SECRET_ACCESS_KEY:=${AWS_SECRET_ACCESS_KEY} AWS_SESSION_TOKEN:=${AWS_SESSION_TOKEN} AWS_SESSION_EXPIRY:=${AWS_SESSION_EXPIRY}"
