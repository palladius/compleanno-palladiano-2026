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
from collections import Counter

CSV_FILE = "private/50 Compleanno Palladiano (Responses) - Form responses 1.csv"
MAPPINGS_FILE = "src/data/city_mappings.csv"
OUTPUT_FILE = "src/data/fomo.json"

DEFAULT_CITY_NORMALIZATION = [
    {"pattern": "zurigo", "location": "Svizzera", "lat": 47.3769, "lng": 8.5417},
    {"pattern": "zurich", "location": "Svizzera", "lat": 47.3769, "lng": 8.5417},
    {"pattern": "oberbuchsiten", "location": "Svizzera", "lat": 47.3769, "lng": 8.5417},
    {"pattern": "ch", "location": "Svizzera", "lat": 47.3769, "lng": 8.5417},
    {"pattern": "svizzera", "location": "Svizzera", "lat": 47.3769, "lng": 8.5417},
    {"pattern": "switzerland", "location": "Svizzera", "lat": 47.3769, "lng": 8.5417},
    {"pattern": "castel guelfo", "location": "Bologna", "lat": 44.4949, "lng": 11.3426},
    {"pattern": "bulaggna", "location": "Bologna", "lat": 44.4949, "lng": 11.3426},
    {"pattern": "bologna", "location": "Bologna", "lat": 44.4949, "lng": 11.3426},
    {"pattern": "arzenta", "location": "Ferrara", "lat": 44.8381, "lng": 11.6198},
    {"pattern": "argenta", "location": "Ferrara", "lat": 44.8381, "lng": 11.6198},
    {"pattern": "conselice", "location": "Ravenna", "lat": 44.4178, "lng": 12.2035},
    {"pattern": "san patrizio", "location": "Ravenna", "lat": 44.4178, "lng": 12.2035},
    {"pattern": "lugo", "location": "Ravenna", "lat": 44.4178, "lng": 12.2035},
    {"pattern": "faenza", "location": "Ravenna", "lat": 44.4178, "lng": 12.2035},
    {"pattern": "ravenna", "location": "Ravenna", "lat": 44.4178, "lng": 12.2035},
    {"pattern": "peroscia", "location": "Perugia", "lat": 43.1107, "lng": 12.3908},
    {"pattern": "perugia", "location": "Perugia", "lat": 43.1107, "lng": 12.3908},
    {"pattern": "torino", "location": "Torino", "lat": 45.0703, "lng": 7.6869},
    {"pattern": "roma", "location": "Roma", "lat": 41.9028, "lng": 12.4964},
    {"pattern": "milano", "location": "Milano", "lat": 45.4642, "lng": 9.1900},
    {"pattern": "san marino", "location": "Rimini", "lat": 44.0594, "lng": 12.5683},
    {"pattern": "rsm", "location": "Rimini", "lat": 44.0594, "lng": 12.5683},
    {"pattern": "rimini", "location": "Rimini", "lat": 44.0594, "lng": 12.5683},
    {"pattern": "raiano", "location": "L'Aquila", "lat": 42.3498, "lng": 13.3995},
    {"pattern": "aquila", "location": "L'Aquila", "lat": 42.3498, "lng": 13.3995},
    {"pattern": "fabriano", "location": "Ancona", "lat": 43.6158, "lng": 13.5189},
    {"pattern": "ancona", "location": "Ancona", "lat": 43.6158, "lng": 13.5189},
    {"pattern": "fano", "location": "Pesaro e Urbino", "lat": 43.8406, "lng": 12.9142},
    {"pattern": "pesaro", "location": "Pesaro e Urbino", "lat": 43.9125, "lng": 12.9155},
    {"pattern": "urbino", "location": "Pesaro e Urbino", "lat": 43.7262, "lng": 12.6366},
]

def load_mappings(file_path=MAPPINGS_FILE):
    """Carica la tabella di approssimazione dal CSV se presente, altrimenti usa il default."""
    if os.path.exists(file_path):
        mappings = []
        try:
            with open(file_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    pattern = row.get("raw_pattern", "").strip().lower()
                    normalized = row.get("normalized_location", "").strip()
                    lat_str = row.get("lat", "").strip()
                    lng_str = row.get("lng", "").strip()
                    lat = float(lat_str) if lat_str else None
                    lng = float(lng_str) if lng_str else None
                    if pattern and normalized:
                        mappings.append({
                            "pattern": pattern,
                            "location": normalized,
                            "lat": lat,
                            "lng": lng
                        })
            if mappings:
                # Ordina per lunghezza decrescente del pattern (più specifici prima)
                mappings.sort(key=lambda x: len(x["pattern"]), reverse=True)
                return mappings
        except Exception as e:
            print(f"Warning: errore nel leggere {file_path}: {e}. Uso fallback.")
    return sorted(DEFAULT_CITY_NORMALIZATION, key=lambda x: len(x["pattern"]), reverse=True)

def resolve_location(c, mappings=None):
    """Restituisce (nome_approssimato, coordinate [lat, lng]) dato il testo grezzo."""
    if not c or not str(c).strip():
        return "", None
    c_lower = str(c).strip().lower()
    if mappings is None:
        mappings = DEFAULT_CITY_NORMALIZATION
    for item in mappings:
        if item["pattern"] in c_lower:
            coords = [item["lat"], item["lng"]] if item.get("lat") is not None and item.get("lng") is not None else None
            return item["location"], coords
    return str(c).strip().title(), None

def normalize_city(c, mappings=None):
    """Approssima il testo libero dell'utente a provincia (IT) o nazione (estero)."""
    loc, _ = resolve_location(c, mappings)
    return loc

def crunch_data(rows, mappings_path=MAPPINGS_FILE):
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

    mappings = load_mappings(mappings_path)
    city_counts = Counter()

    for row in rows:
        attendance = str(row.get("Ci sarai martedi 29 Dicembre 2026?", "")).lower()
        
        # City / Location approximation
        raw_city = str(row.get("Da dove vieni/viaggi?", ""))
        city, _ = resolve_location(raw_city, mappings)
        if city:
            city_counts[city] += 1
            
        # Get number of people
        people_str = str(row.get("Quante persone sarete in totale (tu + accompagnatori)?", "0"))
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

    # Mostra città/province con più di 1 risposta
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

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Successfully crunched CSV and updated {OUTPUT_FILE} with: {data}")

if __name__ == "__main__":
    main()
