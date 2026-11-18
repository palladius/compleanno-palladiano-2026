# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "gspread",
#     "python-dotenv"
# ]
# ///
"""Gestione DB Posti Letto (Trix tab `LETTI`) + Planner + Bozza Email Jasmin 🛏️

Fonte di verità: il tab `LETTI` dello spreadsheet Google (`GOOGLE_SHEET_ID`).
Mantiene:
  - `private/letti_full.csv` (gitignored: nomi completi, email, note)
  - `private/email_jasmin.md` (gitignored: bozza email pronta per Jasmin)
  - `src/data/beds.json` (pubblico, sanitizzato: solo `Nome C.` + soprannomi, zero email)

Comandi:
    seed    Crea/popola il tab `LETTI` su Trix (idempotente salvo `--force`) + dropdown.
    sync    Scarica `LETTI` da Trix -> aggiorna `private/letti_full.csv` e `src/data/beds.json`.
    list    Stampa a terminale CHI va DOVE per struttura e notti.
    email   Genera e stampa la bozza email per Jasmin (`private/email_jasmin.md`).
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
from collections import defaultdict

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass

from crunch_csv import abbreviate_name

SHEET_ID = os.getenv("LETTI_SHEET_ID") or os.getenv("GOOGLE_SHEET_ID")
TAB_NAME = os.getenv("LETTI_TAB", "LETTI")
CREDENTIALS_FILE = "private/fomo-reader.json"
PRIVATE_CSV = "private/letti_full.csv"
EMAIL_DRAFT_FILE = "private/email_jasmin.md"
PUBLIC_JSON = "src/data/beds.json"

JASMIN_EMAIL = "ristoranteaidossi.filo@gmail.com"

HEADER = [
    "StanzaID",
    "Struttura",
    "NomeStanza",
    "Tipologia",
    "PostiMax",
    "Ospiti",
    "Soprannomi",
    "PostiOccupati",
    "CheckIn",
    "CheckOut",
    "Notti",
    "EmailContatto",
    "Stato",
    "Note",
]

STRUTTURE = [
    "Ristorante Ai Dossi",
    "B&B",
    "Garusiola",
    "Da Assegnare",
]

TIPOLOGIE = [
    "Quadrupla (4)",
    "Tripla (3)",
    "Matrimoniale (2)",
    "Doppia Letti Separati (2)",
    "Singola (1)",
]

STATI = {
    "conf": "🟢 CONFERMATO",
    "forse": "🟡 IN FORSE",
    "libera": "⚪ LIBERA",
}

DEFAULT_ROOMS: list[dict[str, str]] = [
    {
        "StanzaID": "DOSSI-1",
        "Struttura": "Ristorante Ai Dossi",
        "NomeStanza": "Quadrupla 1 • Famiglia Palladiana",
        "Tipologia": "Quadrupla (4)",
        "PostiMax": "4",
        "Ospiti": "Riccardo Carlesso, Kate, Ale, Seby",
        "Soprannomi": "Palladius",
        "PostiOccupati": "4",
        "CheckIn": "2026-12-29",
        "CheckOut": "2026-12-30",
        "Notti": "1",
        "EmailContatto": "palladiusbonton@gmail.com",
        "Stato": "🟢 CONFERMATO",
        "Note": "Famiglia festeggiato (Zurigo) — 1 email per famiglia",
    },
    {
        "StanzaID": "DOSSI-2",
        "Struttura": "Ristorante Ai Dossi",
        "NomeStanza": "Quadrupla 2 • Carovana Elvetica",
        "Tipologia": "Quadrupla (4)",
        "PostiMax": "4",
        "Ospiti": "Paolo Pizzorni, Diana Lupandina, Sofia Pizzorni (10), Patricia Pizzorni (8)",
        "Soprannomi": "",
        "PostiOccupati": "4",
        "CheckIn": "2026-12-29",
        "CheckOut": "2026-12-30",
        "Notti": "1",
        "EmailContatto": "p.pizzorni@gmail.com",
        "Stato": "🟢 CONFERMATO",
        "Note": "Oberbuchsiten (CH) — 1 email per famiglia",
    },
    {
        "StanzaID": "DOSSI-3",
        "Struttura": "Ristorante Ai Dossi",
        "NomeStanza": "Matrimoniale 1 • Vienna (dal 28)",
        "Tipologia": "Matrimoniale (2)",
        "PostiMax": "2",
        "Ospiti": "Victoria Anreiter, Simon Anreiter",
        "Soprannomi": "Vicky",
        "PostiOccupati": "2",
        "CheckIn": "2026-12-28",
        "CheckOut": "2026-12-30",
        "Notti": "2",
        "EmailContatto": "vmoser@gmail.com",
        "Stato": "🟢 CONFERMATO",
        "Note": "Arriva sera del 28/12 (2 notti: 28->30) — 1 email per coppia",
    },
    {
        "StanzaID": "DOSSI-4",
        "Struttura": "Ristorante Ai Dossi",
        "NomeStanza": "Doppia 1 • Burattino & Marche (dal 28)",
        "Tipologia": "Doppia Letti Separati (2)",
        "PostiMax": "2",
        "Ospiti": "Fabio Mattei (dal 28), Luca Ferroni (dal 29)",
        "Soprannomi": "Burattino",
        "PostiOccupati": "2",
        "CheckIn": "2026-12-28",
        "CheckOut": "2026-12-30",
        "Notti": "2",
        "EmailContatto": "burattino@gmail.com, elfero@gmail.com",
        "Stato": "🟢 CONFERMATO",
        "Note": "Fabio 2 notti (28->30, 28 solo), Luca 1 notte (29->30) — amici separati -> 2 email",
    },
    {
        "StanzaID": "BB-1",
        "Struttura": "B&B",
        "NomeStanza": "Quadrupla 3 • Famiglia Nicola + 3",
        "Tipologia": "Quadrupla (4)",
        "PostiMax": "4",
        "Ospiti": "Nicola, Familiare Nicola 2, Familiare Nicola 3, Familiare Nicola 4",
        "Soprannomi": "",
        "PostiOccupati": "4",
        "CheckIn": "2026-12-29",
        "CheckOut": "2026-12-30",
        "Notti": "1",
        "EmailContatto": "TODO_EMAIL_NICOLA",
        "Stato": "🟢 CONFERMATO",
        "Note": "Nicola + 3 famiglia. Chiedere a Jasmin se quadrupla è disponibile al Ristorante o B&B; mancano email + nomi dei 3",
    },
    {
        "StanzaID": "BB-2",
        "Struttura": "B&B",
        "NomeStanza": "Matrimoniale 2 • Zurigo / Fano",
        "Tipologia": "Matrimoniale (2)",
        "PostiMax": "2",
        "Ospiti": "Andrea Patrignani, Viktoriya Shablina",
        "Soprannomi": "",
        "PostiOccupati": "2",
        "CheckIn": "2026-12-29",
        "CheckOut": "2026-12-30",
        "Notti": "1",
        "EmailContatto": "apatrign@gmail.com",
        "Stato": "🟢 CONFERMATO",
        "Note": "Zurigo / Fano — 1 email per coppia",
    },
    {
        "StanzaID": "BB-3",
        "Struttura": "B&B",
        "NomeStanza": "Matrimoniale 3 • Carovana Sabauda",
        "Tipologia": "Matrimoniale (2)",
        "PostiMax": "2",
        "Ospiti": "Dario Verrecchia, Behidzhe Nezhdet Mustafa",
        "Soprannomi": "",
        "PostiOccupati": "2",
        "CheckIn": "2026-12-29",
        "CheckOut": "2026-12-30",
        "Notti": "1",
        "EmailContatto": "dario.verrecchia@gmail.com",
        "Stato": "🟢 CONFERMATO",
        "Note": "Torino — 1 email per coppia",
    },
    {
        "StanzaID": "GAR-1",
        "Struttura": "Garusiola",
        "NomeStanza": "Doppia 2 • Milano Express",
        "Tipologia": "Doppia Letti Separati (2)",
        "PostiMax": "2",
        "Ospiti": "Luca Fregoso, Ludovico Besana",
        "Soprannomi": "",
        "PostiOccupati": "2",
        "CheckIn": "2026-12-29",
        "CheckOut": "2026-12-30",
        "Notti": "1",
        "EmailContatto": "luca.fregoso@gmail.com, ludovicobesanaguide@gmail.com",
        "Stato": "🟢 CONFERMATO",
        "Note": "Entrambi da Milano — amici separati -> 2 email (Ludovico aveva papà in forse)",
    },
    {
        "StanzaID": "GAR-2",
        "Struttura": "Garusiola",
        "NomeStanza": "Singola 1 • Equipaggio Riviera",
        "Tipologia": "Singola (1)",
        "PostiMax": "1",
        "Ospiti": "Francesco Bullini",
        "Soprannomi": "",
        "PostiOccupati": "1",
        "CheckIn": "2026-12-29",
        "CheckOut": "2026-12-30",
        "Notti": "1",
        "EmailContatto": "fbullini@gmail.com",
        "Stato": "🟡 IN FORSE",
        "Note": "Parigi -> Rimini (inserito su richiesta; Guarino rimosso)",
    },
]


# ---------------------------------------------------------------------------
# Pure helpers (offline-testable)
# ---------------------------------------------------------------------------

def _to_int(val: str | int | None, default: int = 0) -> int:
    m = re.search(r"\d+", str(val or ""))
    return int(m.group()) if m else default


def rows_to_dicts(values: list[list[str]]) -> list[dict[str, str]]:
    if not values:
        return []
    header = [h.strip() for h in values[0]]
    if header != HEADER:
        raise ValueError(
            f"Il tab '{TAB_NAME}' ha header diverso dall'atteso.\n"
            f"  atteso: {HEADER}\n  trovato: {header}"
        )
    out = []
    for row in values[1:]:
        padded = (row + [""] * len(HEADER))[: len(HEADER)]
        if not any(v.strip() for v in padded):
            continue
        out.append({k: v.strip() for k, v in zip(HEADER, padded)})
    return out


def dicts_to_rows(rooms: list[dict[str, str]]) -> list[list[str]]:
    return [HEADER[:]] + [[str(r.get(k, "")).strip() for k in HEADER] for r in rooms]


def parse_occupants(
    raw_ospiti: str,
    raw_soprannomi: str,
    default_checkin: str,
    default_checkout: str,
    default_nights: int,
) -> list[dict]:
    """Parsa la stringa 'Ospiti' e produce la lista sanitizzata per il sito pubblico."""
    names = [p.strip() for p in re.split(r"[,;\n]+", raw_ospiti or "") if p.strip()]
    nicks = [p.strip() for p in re.split(r"[,;\n]+", raw_soprannomi or "") if p.strip()]
    occupants = []
    for idx, raw in enumerate(names):
        guest_checkin = default_checkin
        guest_nights = default_nights
        # Supporta annotazioni tipo "(dal 28)" o "(dal 29)"
        m_dal = re.search(r"\(dal\s*(\d{1,2})\)", raw, flags=re.IGNORECASE)
        if m_dal:
            day = int(m_dal.group(1))
            if day == 28:
                guest_checkin = "2026-12-28"
                guest_nights = 2
            elif day == 29:
                guest_checkin = "2026-12-29"
                guest_nights = 1
        cleaned = re.sub(r"\([^)]*\)", "", raw).strip()
        if cleaned.lower().startswith("familiare "):
            # Es. "Familiare Nicola 2" -> "Familiare N. #2"
            parts = cleaned.split()
            if len(parts) >= 2:
                display = f"Familiare {parts[1][0].upper()}."
            else:
                display = "Familiare"
        else:
            display = abbreviate_name(cleaned)

        nick = nicks[idx] if idx < len(nicks) else ""
        occupants.append({
            "display_name": display,
            "nickname": nick,
            "check_in": guest_checkin,
            "check_out": default_checkout,
            "nights": guest_nights,
        })
    return occupants


def _extract_surnames(rooms: list[dict[str, str]]) -> list[str]:
    """Estrae i cognomi dagli ospiti per proteggere anche NomeStanza da fughe involontarie."""
    surnames: set[str] = set()
    for r in rooms:
        raw_ospiti = r.get("Ospiti", "")
        for guest in re.split(r"[,;\n]+", raw_ospiti or ""):
            cleaned = re.sub(r"\([^)]*\)", "", guest).strip()
            cleaned = re.sub(r"\d+", "", cleaned).strip()
            parts = [p.strip() for p in cleaned.split() if p.strip()]
            if len(parts) >= 2 and parts[0].lower() != "familiare":
                for token in parts[1:]:
                    if len(token) >= 3:
                        surnames.add(token)
    return sorted(surnames, key=len, reverse=True)


def _redact_surnames(text: str, surnames: list[str]) -> str:
    out = text
    for sn in surnames:
        out = re.sub(rf"\b{re.escape(sn)}\b", f"{sn[0].upper()}.", out, flags=re.IGNORECASE)
    return out


def sanitize_rooms_for_public(rooms: list[dict[str, str]]) -> dict:
    """Costruisce src/data/beds.json (zero cognomi completi, zero email, zero note private)."""
    public_rooms = []
    by_structure: dict[str, dict] = {}
    confirmed_beds = 0
    maybe_beds = 0
    total_capacity = 0
    dec28_guests = 0
    dec29_guests = 0
    known_surnames = _extract_surnames(rooms)

    for r in rooms:
        stato = r.get("Stato", STATI["conf"]).strip()
        if "CONFERMAT" in stato.upper():
            status_code = "confirmed"
        elif "FORSE" in stato.upper():
            status_code = "maybe"
        else:
            status_code = "free"

        posti_max = _to_int(r.get("PostiMax"), 1)
        posti_occ = _to_int(r.get("PostiOccupati"), 0)
        checkin = (r.get("CheckIn") or "2026-12-29").strip()
        checkout = (r.get("CheckOut") or "2026-12-30").strip()
        nights = _to_int(r.get("Notti"), 2 if checkin.endswith("28") else 1)

        occupants = parse_occupants(
            r.get("Ospiti", ""),
            r.get("Soprannomi", ""),
            checkin,
            checkout,
            nights,
        )

        for occ in occupants:
            if status_code != "free":
                if occ["check_in"] == "2026-12-28":
                    dec28_guests += 1
                dec29_guests += 1

        total_capacity += posti_max
        if status_code == "confirmed":
            confirmed_beds += posti_occ
        elif status_code == "maybe":
            maybe_beds += posti_occ

        struttura = (r.get("Struttura") or "Da Assegnare").strip()
        if struttura not in by_structure:
            by_structure[struttura] = {
                "name": struttura,
                "rooms_count": 0,
                "capacity": 0,
                "occupied": 0,
                "confirmed": 0,
                "maybe": 0,
            }
        st_entry = by_structure[struttura]
        st_entry["rooms_count"] += 1
        st_entry["capacity"] += posti_max
        st_entry["occupied"] += posti_occ
        if status_code == "confirmed":
            st_entry["confirmed"] += posti_occ
        elif status_code == "maybe":
            st_entry["maybe"] += posti_occ

        has_early = any(o["check_in"] == "2026-12-28" for o in occupants) or checkin == "2026-12-28"
        safe_room_name = _redact_surnames(r.get("NomeStanza", "").strip(), known_surnames)
        public_rooms.append({
            "id": r.get("StanzaID", "").strip(),
            "structure": struttura,
            "room_name": safe_room_name,
            "room_type": r.get("Tipologia", "").strip(),
            "capacity": posti_max,
            "occupied": posti_occ,
            "status": status_code,
            "status_label": stato,
            "check_in": checkin,
            "check_out": checkout,
            "nights": nights,
            "has_early_arrival": has_early,
            "occupants": occupants,
        })

    return {
        "updated_at": dt.date.today().isoformat(),
        "summary": {
            "total_rooms": len(public_rooms),
            "total_capacity": total_capacity,
            "confirmed_beds": confirmed_beds,
            "maybe_beds": maybe_beds,
            "allocated_beds": confirmed_beds + maybe_beds,
            "dec28_guests": dec28_guests,
            "dec29_guests": dec29_guests,
            "structures": list(by_structure.values()),
        },
        "rooms": public_rooms,
    }


def validate_email_rule(room: dict[str, str]) -> list[str]:
    """Verifica la regola: 1 email per coppia/famiglia, 2 email per amici separati."""
    warnings = []
    emails = [e.strip() for e in re.split(r"[,;\s]+", room.get("EmailContatto", "")) if e.strip()]
    tip = room.get("Tipologia", "").lower()
    sid = room.get("StanzaID", "")
    occ = _to_int(room.get("PostiOccupati"), 0)

    if any("todo" in e.lower() or "@" not in e for e in emails) or not emails:
        if occ > 0:
            warnings.append(f"[{sid}] Email mancante/incompleta: {room.get('EmailContatto') or '(vuota)'}")
    elif "doppia letti separati" in tip and occ >= 2 and len(emails) < 2:
        warnings.append(f"[{sid}] Doppia separati ({room.get('Ospiti')}) ha solo {len(emails)} email (ne servono 2!).")
    elif ("matrimoniale" in tip or "quadrupla" in tip) and len(emails) > 1:
        warnings.append(f"[{sid}] Coppia/famiglia ha {len(emails)} email (ne basta 1!).")
    return warnings


def build_jasmin_email(rooms: list[dict[str, str]]) -> str:
    """Genera la bozza email pronta da mandare a Jasmin (ristoranteaidossi.filo@gmail.com)."""
    active_rooms = [r for r in rooms if _to_int(r.get("PostiOccupati"), 0) > 0]
    total_beds = sum(_to_int(r.get("PostiOccupati"), 0) for r in active_rooms)
    early_rooms = [r for r in active_rooms if (r.get("CheckIn") or "").endswith("28")]

    warnings = []
    for r in active_rooms:
        warnings.extend(validate_email_rule(r))

    by_struct: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in active_rooms:
        by_struct[r.get("Struttura", "Da Assegnare")].append(r)

    lines = [
        f"To: {JASMIN_EMAIL}",
        "Subject: Prenotazione camere 28-30 Dicembre 2026 - 50° Compleanno Riccardo Carlesso (Ai Dossi)",
        "",
        "Ciao Jasmin,",
        "",
        "come d'accordo su WhatsApp, ti mando l'elenco completo delle camere, degli ospiti e delle email di riferimento per la gestione nomi e documenti (notte del 29→30 Dicembre 2026, più gli arrivi anticipati dal 28/12).",
        "",
        f"Totale attuale: **{total_beds} posti letto** in **{len(active_rooms)} camere**.",
        "",
        "### 📅 Arrivi anticipati dal 28 Dicembre (2 notti: 28 → 30 Dicembre)",
    ]
    for r in early_rooms:
        lines.append(
            f"- **{r['NomeStanza']}** ({r['Tipologia']}): {r['Ospiti']} — Email: {r['EmailContatto']}"
            + (f" _({r['Note']})_" if r.get("Note") else "")
        )

    lines.extend([
        "",
        "### 🏨 Distribuzione Camere & Contatti (per struttura)",
        "_(Nota: se una famiglia da 4 pax ci sta direttamente al Ristorante Ai Dossi invece che al B&B, dimmi pure come preferisci incastrarle!)_",
        "",
    ])

    for struct_name, s_rooms in by_struct.items():
        s_beds = sum(_to_int(x.get("PostiOccupati"), 0) for x in s_rooms)
        lines.append(f"#### 📍 {struct_name} ({len(s_rooms)} camere, {s_beds} posti)")
        for r in s_rooms:
            status_tag = " [IN FORSE]" if "FORSE" in r.get("Stato", "").upper() else ""
            n_lbl = "notte" if str(r.get("Notti", "")).strip() == "1" else "notti"
            lines.append(
                f"- **{r['StanzaID']} — {r['Tipologia']}** ({r['PostiOccupati']} pax){status_tag}: "
                f"{r['Ospiti']} | Check-in `{r['CheckIn']}` → `{r['CheckOut']}` ({r['Notti']} {n_lbl}) | "
                f"Email: `{r['EmailContatto']}`"
            )
        lines.append("")

    lines.extend([
        "### ❓ Domande rapide per te",
        "1. Riesci a confermarci se abbiamo una **camera da 4 pax al Ristorante** (per la famiglia di Nicola + 3) o se va al B&B / Garusiola?",
        "2. Ti va bene questa suddivisione tra **Ristorante**, **B&B** e **Garusiola**?",
        "",
        "Appena ricevo email e nomi mancanti della famiglia di Nicola te li giro subito!",
        "",
        "Grazie mille,",
        "Riccardo Carlesso",
    ])

    if warnings:
        lines.extend([
            "",
            "---",
            "<!-- ⚠️ PROMEMORIA INTERNO PER RICCARDO (NON COPIARE NELLA MAIL) -->",
            "<!-- Dati mancanti/da verificare prima dell'invio:",
        ])
        for w in warnings:
            lines.append(f"  - {w}")
        lines.append("-->")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Google Sheets & Local I/O
# ---------------------------------------------------------------------------

def open_spreadsheet():
    import gspread

    if not SHEET_ID:
        sys.exit("Error: GOOGLE_SHEET_ID non trovato in .env")
    if not os.path.exists(CREDENTIALS_FILE):
        sys.exit(f"Error: {CREDENTIALS_FILE} non trovato. Lancia scripts/setup_service_account.sh")
    gc = gspread.service_account(filename=CREDENTIALS_FILE)
    return gc.open_by_key(SHEET_ID)


def get_or_create_worksheet(sh):
    import gspread

    try:
        return sh.worksheet(TAB_NAME), False
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=TAB_NAME, rows=100, cols=len(HEADER))
        return ws, True


def write_worksheet(sh, ws, rows: list[list[str]]) -> None:
    ws.clear()
    ws.update(range_name="A1", values=rows)
    ws.format("A1:N1", {"textFormat": {"bold": True}})
    ws.freeze(rows=1)

    validations = [
        (HEADER.index("Struttura"), STRUTTURE),
        (HEADER.index("Tipologia"), TIPOLOGIE),
        (HEADER.index("Stato"), list(STATI.values())),
    ]
    requests = [
        {
            "setDataValidation": {
                "range": {
                    "sheetId": ws.id,
                    "startRowIndex": 1,
                    "startColumnIndex": col_idx,
                    "endColumnIndex": col_idx + 1,
                },
                "rule": {
                    "condition": {
                        "type": "ONE_OF_LIST",
                        "values": [{"userEnteredValue": v} for v in opts],
                    },
                    "showCustomUi": True,
                    "strict": False,
                },
            }
        }
        for col_idx, opts in validations
    ]
    sh.batch_update({"requests": requests})


def save_outputs(rooms: list[dict[str, str]]) -> dict:
    os.makedirs(os.path.dirname(PRIVATE_CSV), exist_ok=True)
    with open(PRIVATE_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        w.writerows(rooms)

    public_data = sanitize_rooms_for_public(rooms)
    os.makedirs(os.path.dirname(PUBLIC_JSON), exist_ok=True)
    with open(PUBLIC_JSON, "w", encoding="utf-8") as f:
        json.dump(public_data, f, indent=2, ensure_ascii=False)

    email_txt = build_jasmin_email(rooms)
    with open(EMAIL_DRAFT_FILE, "w", encoding="utf-8") as f:
        f.write(email_txt)

    return public_data


def load_local_rooms() -> list[dict[str, str]]:
    if os.path.exists(PRIVATE_CSV):
        with open(PRIVATE_CSV, "r", encoding="utf-8", newline="") as f:
            return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]
    return [dict(r) for r in DEFAULT_ROOMS]


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_seed(args):
    import gspread

    rooms = DEFAULT_ROOMS
    trix_synced = False
    try:
        sh = open_spreadsheet()
        ws, created = get_or_create_worksheet(sh)
        existing = ws.get_all_values()
        if not created and len(existing) > 1 and not args.force:
            print(f"Tab '{TAB_NAME}' già popolato ({len(existing) - 1} righe). Usa --force per sovrascrivere.")
            rooms = rows_to_dicts(existing)
        else:
            write_worksheet(sh, ws, dicts_to_rows(rooms))
            print(f"✅ Tab '{TAB_NAME}' popolato su Trix con {len(rooms)} stanze!")
        trix_synced = True
    except gspread.exceptions.APIError as e:
        if "403" in str(e):
            sa_email = os.getenv("SA", "fomo-reader@...")
            print(
                f"⚠️  Accesso solo lettura/commento su Google Sheet '{SHEET_ID}' (HTTP 403).\n"
                f"   Per scrivere il tab '{TAB_NAME}' su Trix automaticamente:\n"
                f"   1) Dai accesso Editor a `{sa_email}` sul Google Sheet (oppure imposta `LETTI_SHEET_ID` in `.env`), poi rilancia `just letti-seed`;\n"
                f"   2) OPPURE importa manualmente `{PRIVATE_CSV}` in un nuovo tab chiamato `{TAB_NAME}` su Trix (File -> Importa -> Sostituisci foglio)."
            )
        else:
            raise

    pub = save_outputs(rooms)
    prefix = "💾 Aggiornati" if trix_synced else "💾 Generati comunque in locale"
    print(f"{prefix} {PRIVATE_CSV}, {PUBLIC_JSON} ({pub['summary']['allocated_beds']} posti) e {EMAIL_DRAFT_FILE}")


def cmd_sync(_args):
    import gspread

    sh = open_spreadsheet()
    source = f"Trix '{TAB_NAME}'"
    try:
        ws, created = get_or_create_worksheet(sh)
        values = ws.get_all_values()
        if created or len(values) <= 1:
            print(f"⚠️  Tab '{TAB_NAME}' vuoto: eseguo seed iniziale.")
            rooms = DEFAULT_ROOMS
            write_worksheet(sh, ws, dicts_to_rows(rooms))
        else:
            rooms = rows_to_dicts(values)
    except gspread.exceptions.APIError as e:
        if "403" in str(e):
            print(f"⚠️  Tab '{TAB_NAME}' non trovato su Trix e service account in sola lettura (HTTP 403). Uso i dati locali.")
            rooms = load_local_rooms()
            source = "locale (fallback)"
        else:
            raise
    pub = save_outputs(rooms)
    s = pub["summary"]
    print(
        f"✅ Synced {len(rooms)} stanze da {source}: "
        f"{s['confirmed_beds']} confermati + {s['maybe_beds']} in forse = {s['allocated_beds']} letti "
        f"(28/12: {s['dec28_guests']} pax, 29/12: {s['dec29_guests']} pax)."
    )


def cmd_list(_args):
    rooms = load_local_rooms()
    by_s: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in rooms:
        by_s[r.get("Struttura", "Da Assegnare")].append(r)

    total = 0
    for struct, s_rooms in by_s.items():
        beds = sum(_to_int(x.get("PostiOccupati"), 0) for x in s_rooms)
        total += beds
        print(f"\n🏨 {struct} ({len(s_rooms)} camere, {beds} posti)")
        for r in s_rooms:
            print(
                f"  - [{r['StanzaID']}] {r['NomeStanza']} ({r['Tipologia']}, {r['PostiOccupati']}/{r['PostiMax']}) "
                f"| {r['CheckIn']}->{r['CheckOut']} | {r['Ospiti']} | {r['EmailContatto']} | {r['Stato']}"
            )
            for w in validate_email_rule(r):
                print(f"      ⚠️  {w}")
    print(f"\nTotale posti allocati: {total}")


def cmd_email(_args):
    rooms = load_local_rooms()
    email_txt = build_jasmin_email(rooms)
    os.makedirs(os.path.dirname(EMAIL_DRAFT_FILE), exist_ok=True)
    with open(EMAIL_DRAFT_FILE, "w", encoding="utf-8") as f:
        f.write(email_txt)
    print(email_txt)
    print(f"\n💾 Salvata bozza in {EMAIL_DRAFT_FILE}")


def main(argv=None):
    p = argparse.ArgumentParser(description="Gestione Posti Letto (Trix + Planner + Email Jasmin)")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_seed = sub.add_parser("seed", help="Crea/popola il tab LETTI su Google Sheets (Trix)")
    p_seed.add_argument("--force", action="store_true", help="Sovrascrivi il tab LETTI esistente")
    p_seed.set_defaults(func=cmd_seed)

    p_sync = sub.add_parser("sync", help="Sincronizza da Trix LETTI -> private CSV + src/data/beds.json + email")
    p_sync.set_defaults(func=cmd_sync)

    p_list = sub.add_parser("list", help="Mostra riepilogo CHI va DOVE dai dati locali")
    p_list.set_defaults(func=cmd_list)

    p_email = sub.add_parser("email", help="Genera/mostra bozza email per Jasmin")
    p_email.set_defaults(func=cmd_email)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
