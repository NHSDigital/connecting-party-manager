#!/bin/bash

function _validate_current_account() {
    required_account="$1"
    ACCOUNT_DETAILS=$(aws account get-contact-information | jq .ContactInformation.FullName -r)
    if [[ "$ACCOUNT_DETAILS" == "NHS Digital Spine Core CPM ${required_account}" ]]; then
        return 0
    else
        return 1
    fi
}
