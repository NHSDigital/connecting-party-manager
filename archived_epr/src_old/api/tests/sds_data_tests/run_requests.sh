#!/bin/bash

# JSON file passed as the first argument
JSON_FILE="$1"
A_K="$2"
BASE_URL="$3"

total_times=()

# Loop over each object in the JSON file (using process substitution to avoid subshells)
while read -r item; do
    # Extract the path from the JSON
    path=$(echo "$item" | jq -r '.path')

    # Initialize query parameters string
    query_params=""

    # Extract request.params keys and values
    while read -r key value_json; do
        # Get the last part of the key (after the last dot)
        param_name=$(echo "$key" | awk -F. '{print $NF}')

        # Handle array values by appending each value as a separate query param
        for val in $(echo "$value_json" | jq -r '.[]'); do
            query_params="${query_params}${param_name}=${val}&"
        done
    done < <(echo "$item" | jq -r 'to_entries[] | select(.key | startswith("request.params.")) | "\(.key) \(.value | @json)"')

    # Remove the trailing '&' from query_params
    query_params=$(echo "$query_params" | sed 's/&$//')

    # Construct the full URL
    #full_url="${BASE_URL}${path}?${query_params}"
    full_url="${BASE_URL}${path}?${query_params}&use_cpm=iwanttogetdatafromcpm"

    # Execute the curl command and extract the "Total Time"
    echo "Requesting: $full_url"
    a_k="apikey: ${A_K}"
    total_time=$(curl -o /dev/null -s -w "%{time_total}" -i --location "$full_url" --header "$a_k")

    # Ensure total_time is not empty before adding to the array
    if [ -n "$total_time" ]; then
        echo "Total Time for this request: $total_time"
        total_times+=("$total_time")  # Append to the array
    else
        echo "Warning: Failed to retrieve Total Time for this request. Skipping."
    fi
done < <(jq -c '.[]' "$JSON_FILE")

# Ensure there are total times to calculate the average
if [ ${#total_times[@]} -gt 0 ]; then
    echo "All Total Times: ${total_times[@]}"  # Check contents of array

    # Calculate the sum of the "Total Time" values
    total_sum=0
    for time in "${total_times[@]}"; do
        total_sum=$(echo "$total_sum + $time" | bc)
    done

    # Calculate the average (sum divided by the number of elements)
    count=${#total_times[@]}
    average=$(echo "scale=3; $total_sum / $count" | bc)

    # Output the average "Total Time"
    echo "Average Total Time: $average"
else
    echo "No valid Total Time values were collected. Cannot calculate average."
fi
