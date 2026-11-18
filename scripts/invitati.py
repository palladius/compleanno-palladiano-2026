# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "gspread",
#     "python-dotenv"
# ]
# ///
"""Gestione whitelist/blacklist invitati 🤌

Fonte di verità: il tab `CAFONAZZI` dello spreadsheet RSVP (live su Google Sheets).
Qui finiscono le persone che contattano Riccardo fuori dalla form ("io ci sono",
"io non ci sono") così si smette di rompergli le scatole.

Comandi:
    setup   Migra il tab allo schema nuovo (idempotente) + dropdown su Stato.
    add     Aggiunge/aggiorna una persona (upsert su Soprannome o Nome+Cognome).
    list    Stampa la lista raggruppata per Stato.
    dump    Esporta CSV sanitizzato (pubblico) + CSV completo (private/, gitignored).
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import sys
from collections import Counter, defaultdict

try:  # opzionale: i test offline non ne hanno bisogno
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass

DEFAULT_TRIX_MAGICO_ID = "1bJ5Ae1zAyR9NfkM9BUQIo6JBO8Pp0uxKGX0tiZlangM"
SHEET_ID = os.getenv("INVITATI_SHEET_ID") or os.getenv("TRIX_MAGICO_ID") or DEFAULT_TRIX_MAGICO_ID
TAB_NAME = os.getenv("INVITATI_TAB", "CAFONAZZI")
CREDENTIALS_FILE = "private/fomo-reader.json"
PUBLIC_CSV = "src/data/invitati.csv"
PRIVATE_CSV = "private/invitati_full.csv"

HEADER = [
    "Soprannome", "Nome", "Cognome", "Gruppo", "Stato", "Cardinalità",
    "Città", "Fonte", "Data", "Probabilità %", "Note",
]
LEGACY_HEADER = ["Nome", "Cognome", "Città", "Cardinalità", "Note", "Data", "Probabilità %"]

# Colonne che finiscono nel CSV pubblico su GitHub (niente cognomi, note o %).
PUBLIC_COLS = ["Soprannome", "Gruppo", "Stato", "Cardinalità", "Città"]

STATI = {
    "si": "✅ CI SONO",
    "no": "❌ NON CI SONO",
    "forse": "⏳ FORSE",
    "zitto": "🤐 NON CHIEDERE",
}
STATO_COL_INDEX = HEADER.index("Stato")


# ---------------------------------------------------------------------------
# Pure helpers (testabili senza rete)
# ---------------------------------------------------------------------------

def today() -> str:
    return dt.date.today().isoformat()


def parse_prob(raw: str) -> int | None:
    """'90%' -> 90, '0' -> 0, '' -> None."""
    s = str(raw or "").strip().rstrip("%").strip()
    if not s:
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def derive_stato(prob_raw: str, cardinalita_raw: str) -> str:
    """Euristica per le righe legacy senza colonna Stato."""
    prob = parse_prob(prob_raw)
    card = parse_prob(cardinalita_raw)
    if prob is None:
        return STATI["forse"]
    if prob <= 0 or card == 0:
        return STATI["no"]
    if prob >= 80:
        return STATI["si"]
    return STATI["forse"]


def migrate_legacy_rows(values: list[list[str]]) -> list[list[str]]:
    """Converte una griglia con LEGACY_HEADER in una con HEADER."""
    header = [h.strip() for h in values[0]]
    if header != LEGACY_HEADER:
        raise ValueError(f"Header inatteso: {header}")
    out = [HEADER[:]]
    for row in values[1:]:
        row = (row + [""] * len(LEGACY_HEADER))[: len(LEGACY_HEADER)]
        legacy = dict(zip(LEGACY_HEADER, row))
        if not any(v.strip() for v in row):
            continue
        out.append([
            "",                                   # Soprannome
            legacy["Nome"].strip(),
            legacy["Cognome"].strip(),
            "",                                   # Gruppo
            derive_stato(legacy["Probabilità %"], legacy["Cardinalità"]),
            legacy["Cardinalità"].strip(),
            legacy["Città"].strip(),
            "",                                   # Fonte
            legacy["Data"].strip(),
            legacy["Probabilità %"].strip(),
            legacy["Note"].strip(),
        ])
    return out


def rows_to_dicts(values: list[list[str]]) -> list[dict[str, str]]:
    header = [h.strip() for h in values[0]]
    if header != HEADER:
        raise ValueError(
            f"Il tab '{TAB_NAME}' non ha lo schema nuovo. Lancia prima `just invitati-setup`.\n"
            f"  atteso: {HEADER}\n  trovato: {header}"
        )
    dicts = []
    for row in values[1:]:
        row = (row + [""] * len(HEADER))[: len(HEADER)]
        if not any(v.strip() for v in row):
            continue
        dicts.append({k: v.strip() for k, v in zip(HEADER, row)})
    return dicts


def dicts_to_rows(dicts: list[dict[str, str]]) -> list[list[str]]:
    return [HEADER[:]] + [[d.get(k, "") for k in HEADER] for d in dicts]


def _norm(s: str) -> str:
    return " ".join(str(s or "").lower().split())


def find_match(people: list[dict[str, str]], person: dict[str, str]) -> int | None:
    """Indice della riga che matcha per Soprannome, oppure per Nome+Cognome."""
    nick = _norm(person.get("Soprannome"))
    full = (_norm(person.get("Nome")), _norm(person.get("Cognome")))
    for i, p in enumerate(people):
        if nick and _norm(p.get("Soprannome")) == nick:
            return i
        if all(full) and (_norm(p.get("Nome")), _norm(p.get("Cognome"))) == full:
            return i
    return None


def upsert(people: list[dict[str, str]], person: dict[str, str]) -> tuple[list[dict[str, str]], str]:
    """Aggiunge o aggiorna. Ritorna (lista, 'added'|'updated')."""
    idx = find_match(people, person)
    if idx is None:
        return people + [person], "added"
    merged = dict(people[idx])
    for k, v in person.items():
        if v:  # non sovrascrivere con vuoti
            merged[k] = v
    new = list(people)
    new[idx] = merged
    return new, "updated"


def public_label(p: dict[str, str]) -> str:
    """Etichetta pubblica: Soprannome se c'è, altrimenti `Nome C.` (iniziale del cognome)."""
    nick = p.get("Soprannome", "").strip()
    if nick:
        return nick
    nome = " ".join(p.get("Nome", "").split())
    cognome = " ".join(p.get("Cognome", "").split())
    if nome and cognome:
        return f"{nome} {cognome[0].upper()}."
    return nome or (f"{cognome[0].upper()}." if cognome else "")


def sanitize(people: list[dict[str, str]]) -> list[dict[str, str]]:
    """Versione pubblicabile: niente cognomi interi né note. Etichetta = Soprannome o `Nome C.`."""
    out = []
    for p in people:
        pub = {k: p.get(k, "") for k in PUBLIC_COLS}
        pub["Soprannome"] = public_label(p)
        out.append(pub)
    return out


def summarize(people: list[dict[str, str]]) -> dict:
    by_stato = Counter(p.get("Stato", "") or "(vuoto)" for p in people)
    by_gruppo = Counter(p.get("Gruppo", "") or "(nessuno)" for p in people)
    heads = sum(parse_prob(p.get("Cardinalità")) or 0 for p in people if p.get("Stato") == STATI["si"])
    return {"total": len(people), "by_stato": dict(by_stato), "by_gruppo": dict(by_gruppo), "confirmed_heads": heads}


# ---------------------------------------------------------------------------
# Google Sheets I/O
# ---------------------------------------------------------------------------

def open_worksheet():
    import gspread  # lazy: i test non ne hanno bisogno

    if not SHEET_ID:
        sys.exit("Error: GOOGLE_SHEET_ID non trovato in .env")
    if not os.path.exists(CREDENTIALS_FILE):
        sys.exit(f"Error: {CREDENTIALS_FILE} non trovato. Lancia scripts/setup_service_account.sh")
    gc = gspread.service_account(filename=CREDENTIALS_FILE)
    sh = gc.open_by_key(SHEET_ID)
    try:
        return sh, sh.worksheet(TAB_NAME)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=TAB_NAME, rows=100, cols=len(HEADER))
        return sh, ws


def write_all(sh, ws, rows: list[list[str]]) -> None:
    ws.clear()
    ws.update(range_name="A1", values=rows)
    ws.format("A1:K1", {"textFormat": {"bold": True}})
    ws.freeze(rows=1)
    sh.batch_update({"requests": [{
        "setDataValidation": {
            "range": {
                "sheetId": ws.id,
                "startRowIndex": 1,
                "startColumnIndex": STATO_COL_INDEX,
                "endColumnIndex": STATO_COL_INDEX + 1,
            },
            "rule": {
                "condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in STATI.values()]},
                "showCustomUi": True,
                "strict": False,
            },
        }
    }]})


def load_local_people() -> list[dict[str, str]]:
    if not os.path.exists(PRIVATE_CSV):
        return []
    with open(PRIVATE_CSV, "r", encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def save_local_csvs(people: list[dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(PRIVATE_CSV), exist_ok=True)
    with open(PRIVATE_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        w.writerows(people)

    os.makedirs(os.path.dirname(PUBLIC_CSV), exist_ok=True)
    with open(PUBLIC_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=PUBLIC_COLS)
        w.writeheader()
        w.writerows(sanitize(people))


def load_people(ws) -> list[dict[str, str]]:
    values = ws.get_all_values()
    if not values or not any(str(c).strip() for c in values[0]):
        remote = []
    else:
        header = [h.strip() for h in values[0]]
        if header == LEGACY_HEADER:
            print(f"⚠️  Tab '{TAB_NAME}' ancora in formato legacy: migro in memoria (lancia `just invitati-setup` per farlo sul foglio).")
            values = migrate_legacy_rows(values)
        remote = rows_to_dicts(values)
    # Merge eventuali righe già salvate in locale (se il Service Account è in sola lettura sul foglio)
    people = list(remote)
    for local_p in load_local_people():
        people, _ = upsert(people, local_p)
    return people


# ---------------------------------------------------------------------------
# Comandi
# ---------------------------------------------------------------------------

def cmd_setup(_args) -> None:
    sh, ws = open_worksheet()
    values = ws.get_all_values()
    header = [h.strip() for h in values[0]] if values else []
    if header == HEADER:
        print(f"✅ Tab '{TAB_NAME}' già allo schema nuovo ({len(values) - 1} righe). Riapplico formattazione/dropdown.")
        write_all(sh, ws, values)
        return
    if header == LEGACY_HEADER:
        rows = migrate_legacy_rows(values)
        print(f"🔄 Migro {len(rows) - 1} righe legacy → schema nuovo…")
    elif not values:
        rows = [HEADER[:]]
        print("🆕 Tab vuoto, scrivo solo l'header.")
    else:
        sys.exit(f"❌ Header sconosciuto, non tocco nulla: {header}")
    write_all(sh, ws, rows)
    print("✅ Fatto. Controlla a mano gli Stati derivati euristicamente:")
    for r in rows[1:]:
        print(f"   - {r[1]} {r[2]}: {r[4]}  (prob={r[9] or '-'}, card={r[5] or '-'})")


def cmd_add(args) -> None:
    sh, ws = open_worksheet()
    people = load_people(ws)
    person = {
        "Soprannome": args.soprannome or "",
        "Nome": args.nome or "",
        "Cognome": args.cognome or "",
        "Gruppo": args.gruppo or "",
        "Stato": STATI[args.stato],
        "Cardinalità": str(args.cardinalita) if args.cardinalita is not None else "",
        "Città": args.citta or "",
        "Fonte": args.fonte or "",
        "Data": today(),
        "Probabilità %": args.prob or "",
        "Note": args.note or "",
    }
    if not (person["Soprannome"] or (person["Nome"] and person["Cognome"])):
        sys.exit("❌ Serve almeno --soprannome oppure --nome e --cognome")
    people, action = upsert(people, person)
    save_local_csvs(people)
    try:
        write_all(sh, ws, dicts_to_rows(people))
    except Exception as exc:
        print(f"ℹ️  Foglio in sola lettura per il Service Account ({exc.__class__.__name__}); salvato in {PRIVATE_CSV} e {PUBLIC_CSV}.")
    label = person["Soprannome"] or f'{person["Nome"]} {person["Cognome"]}'
    print(f"{'➕' if action == 'added' else '✏️ '} {action}: {label} → {person['Stato']} [{person['Gruppo'] or '-'}]")


def cmd_list(_args) -> None:
    _sh, ws = open_worksheet()
    people = load_people(ws)
    groups = defaultdict(list)
    for p in people:
        groups[p.get("Stato") or "(vuoto)"].append(p)
    for stato in list(STATI.values()) + sorted(set(groups) - set(STATI.values())):
        if stato not in groups:
            continue
        print(f"\n{stato} ({len(groups[stato])})")
        for p in groups[stato]:
            label = p["Soprannome"] or f'{p["Nome"]} {p["Cognome"]}'.strip()
            real = f' ({p["Nome"]} {p["Cognome"]})'.rstrip() if p["Soprannome"] and (p["Nome"] or p["Cognome"]) else ""
            extra = " · ".join(x for x in [p["Gruppo"], p["Città"], p["Note"]] if x)
            print(f"  - {label}{real}  {('— ' + extra) if extra else ''}")
    s = summarize(people)
    print(f"\nTotale: {s['total']} persone, {s['confirmed_heads']} teste confermate ✅")


def cmd_dump(_args) -> None:
    sh, ws = open_worksheet()
    people = load_people(ws)
    save_local_csvs(people)
    try:
        write_all(sh, ws, dicts_to_rows(people))
    except Exception:
        pass

    s = summarize(people)
    print(f"📥 {s['total']} invitati dal tab '{TAB_NAME}'")
    for stato, n in s["by_stato"].items():
        print(f"   {stato}: {n}")
    print("👥 Gruppi: " + ", ".join(f"{g} ({n})" for g, n in s["by_gruppo"].items()))
    print(f"🔒 {PRIVATE_CSV} (completo, gitignored)")
    print(f"🌍 {PUBLIC_CSV} (sanitizzato, committabile)")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("setup", help="migra il tab allo schema nuovo").set_defaults(fn=cmd_setup)
    sub.add_parser("list", help="elenca per stato").set_defaults(fn=cmd_list)
    sub.add_parser("dump", help="esporta CSV pubblico + privato").set_defaults(fn=cmd_dump)

    a = sub.add_parser("add", help="aggiungi/aggiorna una persona")
    a.add_argument("--soprannome", "-s")
    a.add_argument("--nome", "-n")
    a.add_argument("--cognome", "-c")
    a.add_argument("--gruppo", "-g")
    a.add_argument("--stato", choices=STATI.keys(), required=True, help="si | no | forse | zitto")
    a.add_argument("--cardinalita", "-k", type=int, help="quante teste (tu + accompagnatori)")
    a.add_argument("--citta")
    a.add_argument("--fonte", "-f", help="WhatsApp | Telegram | voce | Form …")
    a.add_argument("--prob", "-p", help="es. 50%%")
    a.add_argument("--note")
    a.set_defaults(fn=cmd_add)

    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
