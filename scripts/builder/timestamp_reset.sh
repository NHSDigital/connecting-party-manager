#!/bin/bash
set -e

RESET_TIMESTAMP="2001-01-01T01:01:01"

if [[ -d ${FILEPATH} ]]; then
    find ${FILEPATH} -type f -exec touch -d ${RESET_TIMESTAMP} {} +
    echo "Reset all timestamps files under '${FILEPATH}' to ${RESET_TIMESTAMP}"
elif [[ -f $FILEPATH ]]; then
    touch -d ${RESET_TIMESTAMP} ${FILEPATH}
    echo "Reset the timestamp of '${FILEPATH}' to ${RESET_TIMESTAMP}"
else
    echo "'${FILEPATH}' does not exist"
    exit 1
fi
