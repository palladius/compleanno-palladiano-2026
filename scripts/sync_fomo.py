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

rsvps = 0
posti_letto = 0

# TODO: RICCARDO, please update these keys to match your actual Google Form column headers!
# e.g., "Ci sarai?", "Hai bisogno di un posto letto?"
COMING_KEY = "Ci sarai?"
BED_KEY = "Posti letto"

for row in records:
    # Example logic: count if coming is "Sì" or similar
    coming = str(row.get(COMING_KEY, "")).strip().lower()
    if coming in ["sì", "si", "yes", "certo"]:
        rsvps += 1
    
    # Example logic: count beds (can be a number or "Sì")
    beds = str(row.get(BED_KEY, "")).strip().lower()
    if beds.isdigit():
        posti_letto += int(beds)
    elif beds in ["sì", "si", "yes"]:
        posti_letto += 1

data = {
    "replied": rsvps,
    "bedsTaken": posti_letto,
    "bedsTotal": 25
}

with open(OUTPUT_FILE, "w") as f:
    json.dump(data, f, indent=2)

print(f"Successfully updated {OUTPUT_FILE} with: {data}")
