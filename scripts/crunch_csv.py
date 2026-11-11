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
NICKNAMES_FILE = "src/data/nicknames.csv"
VERBAL_FILE = "src/data/verbal_guests.csv"
OUTPUT_FILE = "src/data/fomo.json"
GUESTS_OUTPUT_FILE = "src/data/guests.json"
CARS_FILE = "src/data/cars.json"

DEFAULT_CITY_NORMALIZATION = [
    {"pattern": "zurigo", "location": "Svizzera", "lat": 46.0037, "lng": 8.9511},
    {"pattern": "zurich", "location": "Svizzera", "lat": 46.0037, "lng": 8.9511},
    {"pattern": "oberbuchsiten", "location": "Svizzera", "lat": 46.0037, "lng": 8.9511},
    {"pattern": "ch", "location": "Svizzera", "lat": 46.0037, "lng": 8.9511},
    {"pattern": "svizzera", "location": "Svizzera", "lat": 46.0037, "lng": 8.9511},
    {"pattern": "switzerland", "location": "Svizzera", "lat": 46.0037, "lng": 8.9511},
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


def abbreviate_name(full_name: str) -> str:
    """Converte 'Nome Cognome' in 'Nome C.' per privacy (es. 'Riccardo Carlesso' -> 'Riccardo C.')."""
    cleaned = re.sub(r"\d+", "", str(full_name or "")).strip()
    parts = [p.strip() for p in cleaned.split() if p.strip()]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0].title()
    first_name = parts[0].title()
    initials = " ".join(f"{p[0].upper()}." for p in parts[1:] if p)
    return f"{first_name} {initials}"


def load_nicknames(file_path=NICKNAMES_FILE) -> dict[str, dict[str, str]]:
    """Carica la mappa Nome C. -> {nickname, gruppo, city_override, promote_companion, role_badge, music_note}."""
    out: dict[str, dict[str, str]] = {}
    if not file_path or not os.path.exists(file_path):
        return out
    try:
        with open(file_path, mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                key = (row.get("nome_c") or "").strip()
                if key:
                    out[key.lower()] = {k: (v or "").strip() for k, v in row.items()}
    except Exception as e:
        print(f"Warning: errore nel leggere {file_path}: {e}")
    return out


def load_verbal_guests(file_path=VERBAL_FILE) -> list[dict[str, str]]:
    """Carica gli invitati verbalmente promessi (WhatsApp / Carovane) ma non ancora sul Form."""
    out: list[dict[str, str]] = []
    if not file_path or not os.path.exists(file_path):
        return out
    try:
        with open(file_path, mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                cleaned = {k: (v or "").strip() for k, v in row.items()}
                if cleaned.get("nickname") or cleaned.get("nome_c"):
                    out.append(cleaned)
    except Exception as e:
        print(f"Warning: errore nel leggere {file_path}: {e}")
    return out


def build_guests_data(
    rows,
    mappings_path=MAPPINGS_FILE,
    nicknames_path=NICKNAMES_FILE,
    verbal_path=VERBAL_FILE,
) -> dict:
    """Costruisce la lista privacy-safe di Confermati e In Forse (Nome C., nickname, +1)."""
    mappings = load_mappings(mappings_path)
    nicknames_map = load_nicknames(nicknames_path)
    verbal_rows = load_verbal_guests(verbal_path)

    confirmed_list = []
    maybe_form_list = []
    seen_names_c = set()
    seen_nicks = set()

    for idx, row in enumerate(rows, 1):
        attendance = str(row.get("Ci sarai martedi 29 Dicembre 2026?", "")).lower()
        if "si" in attendance or "sì" in attendance:
            status = "confirmed"
        elif "forse" in attendance:
            status = "maybe"
        else:
            continue

        raw_name = str(row.get("Nome e Cognome", "")).strip()
        nome_c = abbreviate_name(raw_name)
        if not nome_c:
            continue

        meta = nicknames_map.get(nome_c.lower(), {})
        nickname = meta.get("nickname", "")
        group = meta.get("gruppo", "")
        role_badge = meta.get("role_badge", "")
        music_note = meta.get("music_note", "")

        raw_city = str(row.get("Da dove vieni/viaggi?", "")).strip()
        region, _ = resolve_location(raw_city, mappings)
        city_display = meta.get("city_override") or region or raw_city

        people_str = str(row.get("Quante persone sarete in totale (tu + accompagnatori)?", "1"))
        match = re.search(r"\d+", people_str)
        people_count = int(match.group()) if match else 1
        extra_people = max(0, people_count - 1)
        is_family = "famiglia" in people_str.lower() or "bambini" in people_str.lower() or extra_people >= 2
        has_maybe_plus = "forse" in people_str.lower() and extra_people == 0

        # Verifica se tra gli accompagnatori c'è un amico noto con promote_companion=true (es. Stefano G. -> Giua')
        companions_raw = str(row.get("Nomi degli eventuali accompagnatori (+1 e/o figli)", "")).strip()
        promoted_friends = []
        if companions_raw:
            for comp_line in re.split(r"[\n,;]+", companions_raw):
                comp_abbr = abbreviate_name(comp_line)
                if not comp_abbr:
                    continue
                comp_meta = nicknames_map.get(comp_abbr.lower(), {})
                if comp_meta.get("promote_companion", "").lower() == "true":
                    promoted_friends.append((comp_abbr, comp_meta))

        partner_friend_label = ""
        if promoted_friends:
            extra_people = max(0, extra_people - len(promoted_friends))
            first_friend_abbr, first_friend_meta = promoted_friends[0]
            friend_nick = first_friend_meta.get("nickname") or first_friend_abbr
            partner_friend_label = f"con {friend_nick}"

        if extra_people == 1:
            plus_label_it = "+1"
            plus_label_en = "+1"
        elif extra_people >= 2 or (extra_people > 0 and is_family):
            plus_label_it = f"+{extra_people} (Famiglia)"
            plus_label_en = f"+{extra_people} (Family)"
        elif has_maybe_plus:
            plus_label_it = "+1 in forse"
            plus_label_en = "+1 maybe"
        else:
            plus_label_it = ""
            plus_label_en = ""

        guest_entry = {
            "id": f"guest-{idx}",
            "name": nome_c,
            "nickname": nickname,
            "status": status,
            "source": "form",
            "party_size": 1 + extra_people,
            "plus_ones": extra_people,
            "is_family": is_family and extra_people > 0,
            "plus_label_it": plus_label_it,
            "plus_label_en": plus_label_en,
            "partner_friend": partner_friend_label,
            "city": city_display,
            "region": region,
            "group": group,
            "role_badge": role_badge,
            "music_note": music_note,
        }

        target_list = confirmed_list if status == "confirmed" else maybe_form_list
        target_list.append(guest_entry)
        seen_names_c.add(nome_c.lower())
        if nickname:
            seen_nicks.add(nickname.lower())

        # Emetti scheda separata per gli amici promossi dal campo +1 (es. Stefano G. «Giua'»)
        for f_idx, (friend_abbr, friend_meta) in enumerate(promoted_friends, 1):
            f_nick = friend_meta.get("nickname", "")
            f_entry = {
                "id": f"guest-{idx}-friend-{f_idx}",
                "name": friend_abbr,
                "nickname": f_nick,
                "status": status,
                "source": "form",
                "party_size": 1,
                "plus_ones": 0,
                "is_family": False,
                "plus_label_it": "",
                "plus_label_en": "",
                "partner_friend": f"con {nickname or nome_c}",
                "city": friend_meta.get("city_override") or city_display,
                "region": region,
                "group": friend_meta.get("gruppo", ""),
                "role_badge": friend_meta.get("role_badge", ""),
                "music_note": friend_meta.get("music_note", ""),
            }
            target_list.append(f_entry)
            seen_names_c.add(friend_abbr.lower())
            if f_nick:
                seen_nicks.add(f_nick.lower())

    # Metti il festeggiato (Riccardo C. / Palladius) in cima ai confermati
    confirmed_list.sort(key=lambda g: 0 if g.get("nickname") == "Palladius" else 1)

    # Aggiungi gli invitati verbali / WhatsApp non ancora presenti nel Form
    maybe_verbal_list = []
    for v_idx, v in enumerate(verbal_rows, 1):
        v_nick = v.get("nickname", "")
        v_name = v.get("nome_c", "")
        if (v_nick and v_nick.lower() in seen_nicks) or (v_name and v_name.lower() in seen_names_c):
            continue
        raw_c = v.get("citta", "")
        v_region, _ = resolve_location(raw_c, mappings)
        maybe_verbal_list.append({
            "id": f"verbal-{v_idx}",
            "name": v_name,
            "nickname": v_nick,
            "status": "maybe_verbal",
            "source": v.get("fonte", "WhatsApp 💬"),
            "party_size": 1,
            "plus_ones": 0,
            "is_family": False,
            "plus_label_it": "",
            "plus_label_en": "",
            "partner_friend": "",
            "city": raw_c,
            "region": v_region or raw_c,
            "group": v.get("gruppo", ""),
            "role_badge": "",
            "music_note": "",
            "emoji": v.get("emoji", "⏳"),
        })

    confirmed_heads = sum(g["party_size"] for g in confirmed_list)
    maybe_form_heads = sum(g["party_size"] for g in maybe_form_list)
    maybe_verbal_heads = sum(g["party_size"] for g in maybe_verbal_list)

    return {
        "summary": {
            "confirmed_heads": confirmed_heads,
            "confirmed_cards": len(confirmed_list),
            "plus_ones_total": sum(g["plus_ones"] for g in confirmed_list),
            "maybe_form_heads": maybe_form_heads,
            "maybe_form_cards": len(maybe_form_list),
            "maybe_verbal_cards": len(maybe_verbal_list),
            "total_maybe_heads": maybe_form_heads + maybe_verbal_heads,
            "total_seats": 100,
        },
        "confirmed": confirmed_list,
        "maybe_form": maybe_form_list,
        "maybe_verbal": maybe_verbal_list,
    }

def crunch_data(rows, mappings_path=MAPPINGS_FILE):
    confirmed = 0
    maybe = 0
    respondents = 0
    maybe_respondents = 0
    confirmed_beds = 0
    maybe_beds = 0
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
            is_confirmed = True
        elif "forse" in attendance:
            maybe_respondents += 1
            maybe += people_count
            is_confirmed = False
        else:
            is_confirmed = False
            
        # Get beds
        beds_str = str(row.get("Servono posti letto? Se si', quanti?", "0"))
        beds_match = re.search(r'\d+', beds_str)
        beds_count = int(beds_match.group()) if beds_match else 0
        
        if is_confirmed:
            confirmed_beds += beds_count
        else:
            maybe_beds += beds_count
        
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
        "confirmed_beds": confirmed_beds,
        "maybe_beds": maybe_beds,
        "need_accomodation": confirmed_beds + maybe_beds,
        "rompicoglioni": rompicoglioni,
        "dietary_breakdown": dietary_breakdown,
        "cities": cities,
        "total_accomodation": 35,
        "total_seats": 100
    }


def reconcile_cars(guests_data: dict, cars_path: str = CARS_FILE) -> list[str]:
    """Confronta gli invitati (Confermati / In Forse) con src/data/cars.json e segnala discrepanze."""
    if not cars_path or not os.path.exists(cars_path):
        return []
    try:
        with open(cars_path, "r", encoding="utf-8") as f:
            cars_data = json.load(f)
    except Exception:
        return []

    rides = cars_data.get("rides", [])
    covered_regions: dict[str, str] = {}
    rides_text_blob = json.dumps(rides, ensure_ascii=False).lower()
    for r in rides:
        city_norm = normalize_city(r.get("city", ""))
        if city_norm:
            covered_regions[city_norm.lower()] = r.get("status", "maybe")

    local_regions = {"ravenna", "ferrara", ""}
    warnings: list[str] = []

    for g in guests_data.get("confirmed", []) + guests_data.get("maybe_form", []):
        region = (g.get("region") or "").strip()
        city = (g.get("city") or "").strip()
        name = g.get("name", "")
        nick = g.get("nickname", "")
        status = g.get("status", "")
        first_name = name.split()[0].lower() if name else ""

        if region.lower() in local_regions:
            continue

        # Rimini copre anche Raiano (Fabio M.) tramite treno -> Rimini
        if region.lower() == "l'aquila" and ("fabio" in rides_text_blob or "raiano" in rides_text_blob):
            continue

        if region.lower() not in covered_regions:
            label = f"{name} ({nick})" if nick else name
            st_icon = "🟢 CONFERMATO" if status == "confirmed" else "🟡 IN FORSE"
            warnings.append(
                f"{st_icon} fuori zona senza auto su /map: {label} da {city} [{region}] (party={g.get('party_size', 1)})"
            )
        elif status == "confirmed" and covered_regions[region.lower()] == "maybe":
            if first_name and first_name in rides_text_blob:
                warnings.append(
                    f"⚠️  Stato disallineato su /map per {region}: {name} è 🟢 CONFERMATO nel Form ma il pin di {region} in cars.json è ancora 'maybe' (🟡)!"
                )

    return warnings


def main():
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} not found.")
        exit(1)

    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    data = crunch_data(rows)
    guests_data = build_guests_data(rows)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    with open(GUESTS_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(guests_data, f, indent=2, ensure_ascii=False)

    print(f"Successfully crunched CSV and updated {OUTPUT_FILE} and {GUESTS_OUTPUT_FILE}")
    warnings = reconcile_cars(guests_data)
    if warnings:
        print("\n🚗 Riconciliazione Mappa Auto (src/data/cars.json):")
        for w in warnings:
            print(f"  - {w}")

if __name__ == "__main__":
    main()
