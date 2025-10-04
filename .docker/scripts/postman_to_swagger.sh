#!/bin/bash

# Parameters
API_KEY=$1
COLLECTION_ID=$2
FILENAME_LOCATION=$3

# Endpoint URL
URL="https://dashboard.rudo.es/parser/postman-to-swagger"

# JSON payload
PAYLOAD=$(cat <<EOF
{
  "api_key": "$API_KEY",
  "collection_id": "$COLLECTION_ID"
}
EOF
)

# Make the POST request and save the response
HTTP_STATUS=$(curl -s -o "$FILENAME_LOCATION" -w "%{http_code}" -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "X-API-ACCESS-TOKEN: y5cUsYg5A4CJsCUFPmUy4LwBUn0nGBOj" \
  -d "$PAYLOAD")

# Check if the request was successful
if [ "$HTTP_STATUS" -eq 200 ]; then
  echo "File saved successfully at $FILENAME_LOCATION"
else
  echo "Error: HTTP $HTTP_STATUS"
  rm -f "$FILENAME_LOCATION"  # Remove the file if the request failed
fi

