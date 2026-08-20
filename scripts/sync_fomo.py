# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "gspread",
#     "python-dotenv"
# ]
# ///

import os
import json
import gspread
from dotenv import load_dotenv

from crunch_csv import crunch_data

load_dotenv()

SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
CREDENTIALS_FILE = "private/fomo-reader.json"
OUTPUT_FILE = "src/data/fomo.json"

if not SHEET_ID:
    print("Error: GOOGLE_SHEET_ID not found in .env")
    exit(1)

if not os.path.exists(CREDENTIALS_FILE):
    print(f"Error: {CREDENTIALS_FILE} not found. Please run scripts/setup_service_account.sh first.")
    exit(1)

print("Authenticating with Google Sheets...")
gc = gspread.service_account(filename=CREDENTIALS_FILE)

print("Fetching spreadsheet...")
sh = gc.open_by_key(SHEET_ID)
worksheet = sh.get_worksheet(0) # Get first sheet

records = worksheet.get_all_records()
print(f"Fetched {len(records)} records from Google Sheets.")

# Crunch the data using the unified logic
data = crunch_data(records)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Successfully synced from Trix and updated {OUTPUT_FILE} with: {data}")

