# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "python-dotenv"
# ]
# ///

import csv
import json
import os
import re

CSV_FILE = "private/50 Compleanno Palladiano (Responses) - Form responses 1.csv"
OUTPUT_FILE = "src/data/fomo.json"

if not os.path.exists(CSV_FILE):
    print(f"Error: {CSV_FILE} not found.")
    exit(1)

confirmed = 0
maybe = 0
need_accomodation = 0

with open(CSV_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        attendance = row.get("Ci sarai martedi 29 Dicembre 2026?", "").lower()
        
        # Get number of people
        people_str = row.get("Quante persone sarete in totale (tu + accompagnatori)?", "0")
        # Extract first number from the string
        match = re.search(r'\d+', people_str)
        people_count = int(match.group()) if match else 0
        
        if "si" in attendance or "sì" in attendance:
            confirmed += people_count
        elif "forse" in attendance:
            maybe += people_count
            
        # Get beds
        beds_str = row.get("Servono posti letto? Se si', quanti?", "0")
        beds_match = re.search(r'\d+', beds_str)
        beds_count = int(beds_match.group()) if beds_match else 0
        
        need_accomodation += beds_count

data = {
    "confirmed": confirmed,
    "maybe": maybe,
    "need_accomodation": need_accomodation,
    "total_accomodation": 35,
    "total_a_tavola": 100
}

with open(OUTPUT_FILE, "w") as f:
    json.dump(data, f, indent=2)

print(f"Successfully crunched CSV and updated {OUTPUT_FILE} with: {data}")
