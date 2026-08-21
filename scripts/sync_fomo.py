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

# Read old data to compare
old_records = 0
if os.path.exists(OUTPUT_FILE):
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            old_data = json.load(f)
            old_records = old_data.get("total_records", 0)
    except Exception:
        pass

# Crunch the data using the unified logic
data = crunch_data(records)
new_records = data.get("total_records", 0)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

if new_records > old_records:
    print(f"\033[92m🎉 Nuovi records! {old_records} -> {new_records}\033[0m")
elif new_records < old_records:
    print(f"\033[91m⚠️ Record diminuiti? {old_records} -> {new_records}\033[0m")
else:
    print(f"\033[90mNessun nuovo record (sempre {new_records}). Aumenta la fomo!\033[0m")

if data.get("cities"):
    print("\n🏙️  Città con più di 1 invitato:")
    for city, count in data["cities"].items():
        print(f"  - {city}: {count}")

print(f"\nSuccessfully synced from Trix and updated {OUTPUT_FILE}!")
