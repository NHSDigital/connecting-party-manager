#!/bin/bash

function _validate_current_account() {
    required_account="$1"
    ACCOUNT_DETAILS=$(aws account get-contact-information)
    if [[ "$ACCOUNT_DETAILS" == *"$required_account"* ]]; then
        return 1
    else
        return 0
    fi
}
