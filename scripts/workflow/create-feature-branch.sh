#!/bin/bash

# Check if the script has received the correct number of arguments
if [ $# -ne 2 ]; then
  echo "Usage: $0 <JIRA_TICKET> <DESCRIPTION>"
  exit 1
fi

JIRA_TICKET="$1"
DESCRIPTION="$2"

# Check that the JIRA ticket is of the correct form
JIRA_PATTERN="^PI-[0-9]+$"
if [[ ! $JIRA_TICKET =~ $JIRA_PATTERN ]]; then
    echo "JIRA_TICKET must be of the form '$JIRA_PATTERN'."
    exit 1
fi


# Sanitize DESCRIPTION to create a lower snake case version
SANITIZED_DESCRIPTION=$(echo "${DESCRIPTION}" | tr '[:upper:]' '[:lower:]' | tr ' ' '_')

# Create the Git branch
GIT_BRANCH="feature/${JIRA_TICKET}-${SANITIZED_DESCRIPTION}"
git checkout -b "${GIT_BRANCH}"
