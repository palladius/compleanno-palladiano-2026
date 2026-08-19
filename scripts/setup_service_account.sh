#!/bin/bash
set -e

if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create one from .env.template"
    exit 1
fi
source .env
if [ -z "$GCP_PROJECT_ID" ]; then
    echo "Error: GCP_PROJECT_ID not set in .env"
    exit 1
fi
PROJECT_ID=$GCP_PROJECT_ID
SA_NAME="fomo-reader"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Creating Service Account ($SA_NAME)..."
# This might prompt you to touch your security key (Gnubby)
gcloud iam service-accounts create $SA_NAME \
    --description="Read-only access for Compleanno FOMO stats" \
    --display-name="Compleanno FOMO Reader" \
    --project=$PROJECT_ID || true

echo "Generating Key..."
mkdir -p private
# This might also prompt you to touch your security key
gcloud iam service-accounts keys create private/credentials.json \
    --iam-account=$SA_EMAIL \
    --project=$PROJECT_ID

echo "Done! Key saved to private/credentials.json."
echo ""
echo "=========================================================="
echo " IMPORTANT: "
echo " Please open your Google Sheet:"
echo " https://docs.google.com/spreadsheets/d/1H-dXCYIUBjTfqstoa600kZAgkh77OOsou598loZZaMM"
echo " And share it (Read-Only/Viewer) with this email address:"
echo " $SA_EMAIL"
echo " (And also share it with palladiusbonton@gmail.com if not already!)"
echo "=========================================================="
