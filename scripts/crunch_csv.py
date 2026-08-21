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

def crunch_data(rows):
    confirmed = 0
    maybe = 0
    respondents = 0
    maybe_respondents = 0
    need_accomodation = 0
    rompicoglioni = 0
    dietary_breakdown = {
        "celiaci": 0,
        "vegani": 0,
        "vegetariani": 0,
        "altro": 0
    }

    from collections import Counter
    city_counts = Counter()

    for row in rows:
        attendance = str(row.get("Ci sarai martedi 29 Dicembre 2026?", "")).lower()
        
        # City
        city = str(row.get("Da dove vieni/viaggi?", "")).strip().title()
        if city:
            city_counts[city] += 1
            
        # Get number of people
        people_str = str(row.get("Quante persone sarete in totale (tu + accompagnatori)?", "0"))
        # Extract first number from the string
        match = re.search(r'\d+', people_str)
        people_count = int(match.group()) if match else 0
        
        if "si" in attendance or "sì" in attendance:
            respondents += 1
            confirmed += people_count
        elif "forse" in attendance:
            maybe_respondents += 1
            maybe += people_count
            
        # Get beds
        beds_str = str(row.get("Servono posti letto? Se si', quanti?", "0"))
        beds_match = re.search(r'\d+', beds_str)
        beds_count = int(beds_match.group()) if beds_match else 0
        
        need_accomodation += beds_count
        
        # Dietary restrictions (rompicoglioni)
        dietary_str = str(row.get("Intolleranze alimentari, allergie o diete particolari", "")).strip().lower()
        if dietary_str and not any(x in dietary_str for x in ["mangiamo di tutto", "nessuna", "nessuno", "niente", "nessun"]):
            rompicoglioni += 1
            if "celiac" in dietary_str:
                dietary_breakdown["celiaci"] += 1
            elif "vegan" in dietary_str:
                dietary_breakdown["vegani"] += 1
            elif "vegetariana" in dietary_str or "vegetariano" in dietary_str:
                dietary_breakdown["vegetariani"] += 1
            else:
                dietary_breakdown["altro"] += 1

    cities = {city: count for city, count in city_counts.items() if count > 1}

    return {
        "total_records": len(rows),
        "respondents": respondents,
        "maybe_respondents": maybe_respondents,
        "confirmed": confirmed,
        "maybe": maybe,
        "need_accomodation": need_accomodation,
        "rompicoglioni": rompicoglioni,
        "dietary_breakdown": dietary_breakdown,
        "cities": cities,
        "total_accomodation": 35,
        "total_seats": 100
    }

def main():
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} not found.")
        exit(1)

    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    data = crunch_data(rows)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Successfully crunched CSV and updated {OUTPUT_FILE} with: {data}")

if __name__ == "__main__":
    main()
