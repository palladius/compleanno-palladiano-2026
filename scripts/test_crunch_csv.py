import pytest
from crunch_csv import crunch_data, normalize_city, resolve_location, load_mappings, abbreviate_name, build_guests_data, reconcile_cars

def test_load_mappings_fallback():
    mappings = load_mappings("non_existent_file.csv")
    assert len(mappings) > 0
    # Verifica che pattern più specifici siano ordinati prima
    assert any(m["pattern"] == "castel guelfo" for m in mappings)

def test_resolve_location():
    loc, coords = resolve_location("Zurigo")
    assert loc == "Svizzera"
    assert coords == [46.0037, 8.9511]

    loc, coords = resolve_location("San marino RSM")
    assert loc == "Rimini"
    assert coords == [44.0594, 12.5683]

    loc, coords = resolve_location("Posto Sconosciuto")
    assert loc == "Posto Sconosciuto"
    assert coords is None

def test_normalize_city():
    mappings = [
        {"pattern": "castel guelfo", "location": "Bologna", "lat": 44.4949, "lng": 11.3426},
        {"pattern": "bologna", "location": "Bologna", "lat": 44.4949, "lng": 11.3426},
        {"pattern": "zurigo", "location": "Svizzera", "lat": 47.3769, "lng": 8.5417},
        {"pattern": "san marino", "location": "Rimini", "lat": 44.0594, "lng": 12.5683},
        {"pattern": "argenta", "location": "Ferrara", "lat": 44.8381, "lng": 11.6198},
    ]
    assert normalize_city("Castel guelfo di bologna", mappings) == "Bologna"
    assert normalize_city("Bologna ", mappings) == "Bologna"
    assert normalize_city("Oberbuchsiten, CH", [{"pattern": "ch", "location": "Svizzera"}]) == "Svizzera"
    assert normalize_city("San marino RSM", mappings) == "Rimini"
    assert normalize_city("Posto Sconosciuto", mappings) == "Posto Sconosciuto"
    assert normalize_city("", mappings) == ""

def test_crunch_data_empty():
    rows = []
    data = crunch_data(rows)
    assert data["respondents"] == 0
    assert data["confirmed"] == 0
    assert data["maybe"] == 0
    assert data["need_accomodation"] == 0
    assert data["rompicoglioni"] == 0
    assert data["cities"] == {}

def test_crunch_data_location_aggregation():
    rows = [
        {
            "Ci sarai martedi 29 Dicembre 2026?": "Sì",
            "Quante persone sarete in totale (tu + accompagnatori)?": "4",
            "Da dove vieni/viaggi?": "Zurigo"
        },
        {
            "Ci sarai martedi 29 Dicembre 2026?": "Sì",
            "Quante persone sarete in totale (tu + accompagnatori)?": "3",
            "Da dove vieni/viaggi?": "Oberbuchsiten, CH"
        },
        {
            "Ci sarai martedi 29 Dicembre 2026?": "Sì",
            "Quante persone sarete in totale (tu + accompagnatori)?": "1",
            "Da dove vieni/viaggi?": "Bologna"
        },
        {
            "Ci sarai martedi 29 Dicembre 2026?": "Sì",
            "Quante persone sarete in totale (tu + accompagnatori)?": "2",
            "Da dove vieni/viaggi?": "Castel guelfo di bologna"
        },
        {
            "Ci sarai martedi 29 Dicembre 2026?": "Forse",
            "Quante persone sarete in totale (tu + accompagnatori)?": "1",
            "Da dove vieni/viaggi?": "San marino RSM"
        }
    ]
    data = crunch_data(rows)
    # Svizzera (2 risposte) e Bologna (2 risposte) superano la soglia > 1
    assert data["cities"].get("Svizzera") == 2
    assert data["cities"].get("Bologna") == 2
    # San Marino è Rimini (1 risposta sola, quindi non appare in cities > 1)
    assert "Rimini" not in data["cities"]

def test_crunch_data_dietary_restrictions():
    rows = [
        {
            "Ci sarai martedi 29 Dicembre 2026?": "Sì",
            "Quante persone sarete in totale (tu + accompagnatori)?": "1",
            "Servono posti letto? Se si', quanti?": "1",
            "Intolleranze alimentari, allergie o diete particolari": "Vegano"
        },
        {
            "Ci sarai martedi 29 Dicembre 2026?": "Sì",
            "Quante persone sarete in totale (tu + accompagnatori)?": "1",
            "Servono posti letto? Se si', quanti?": "1 letto per favore",
            "Intolleranze alimentari, allergie o diete particolari": "Celiaco"
        },
        {
            "Ci sarai martedi 29 Dicembre 2026?": "Forse",
            "Quante persone sarete in totale (tu + accompagnatori)?": "2",
            "Servono posti letto? Se si', quanti?": "2",
            "Intolleranze alimentari, allergie o diete particolari": "Allergia alle arachidi"
        }
    ]
    data = crunch_data(rows)
    assert data["confirmed"] == 2
    assert data["maybe"] == 2
    assert data["confirmed_beds"] == 2
    assert data["maybe_beds"] == 2
    assert data["need_accomodation"] == 4
    assert data["rompicoglioni"] == 3
    assert data["dietary_breakdown"]["vegani"] == 1
    assert data["dietary_breakdown"]["celiaci"] == 1
    assert data["dietary_breakdown"]["altro"] == 1


def test_abbreviate_name_privacy():
    assert abbreviate_name("Riccardo Carlesso") == "Riccardo C."
    assert abbreviate_name("Stefano Gialli") == "Stefano G."
    assert abbreviate_name("Emiliano Della Casa") == "Emiliano D. C."
    assert abbreviate_name("Andrea Degli Angeli") == "Andrea D. A."
    assert abbreviate_name("Sofia Rossi 10") == "Sofia R."
    assert abbreviate_name("") == ""


def test_build_guests_data_privacy_and_nicknames():
    rows = [
        {
            "Nome e Cognome": "Riccardo Brambilla",
            "Ci sarai martedi 29 Dicembre 2026?": "Si, ci saro assolutamente! 🎉",
            "Quante persone sarete in totale (tu + accompagnatori)?": "2 (Io + 1)",
            "Nomi degli eventuali accompagnatori (+1 e/o figli)": "Maria Rossi",
            "Da dove vieni/viaggi?": "Bologna",
        },
        {
            "Nome e Cognome": "Barbara Nava",
            "Ci sarai martedi 29 Dicembre 2026?": "Si, ci saro assolutamente! 🎉",
            "Quante persone sarete in totale (tu + accompagnatori)?": "2 (Io + 1)",
            "Nomi degli eventuali accompagnatori (+1 e/o figli)": "Stefano Gialli",
            "Da dove vieni/viaggi?": "",
        },
        {
            "Nome e Cognome": "Maurizio Grandi",
            "Ci sarai martedi 29 Dicembre 2026?": "In forse / Ti confermo piu avanti ⏳",
            "Quante persone sarete in totale (tu + accompagnatori)?": "1 (Solo io)",
            "Nomi degli eventuali accompagnatori (+1 e/o figli)": "",
            "Da dove vieni/viaggi?": "Bologna",
        },
    ]
    res = build_guests_data(rows)
    # Verifica che il +1 della morosa sia anonimizzato come '+1' e non esponga il nome
    riccardo_b = next(g for g in res["confirmed"] if g["name"] == "Riccardo B.")
    assert riccardo_b["plus_ones"] == 1
    assert riccardo_b["plus_label_it"] == "+1"
    assert "Maria" not in str(res)
    assert "Brambilla" not in str(res)

    # Verifica che Stefano G. nel +1 di Barbara N. diventi Stefano G. «Giua'»
    giua = next(g for g in res["confirmed"] if g["name"] == "Stefano G.")
    assert giua["nickname"] == "Giua'"
    assert giua["partner_friend"] == "con Barbara N."

    # Verifica che Maurizio G. in forse abbia il nickname Fraffo e non venga duplicato nei verbali
    fraffo = next(g for g in res["maybe_form"] if g["name"] == "Maurizio G.")
    assert fraffo["nickname"] == "Fraffo"
    assert not any(v["nickname"] == "Fraffo" for v in res["maybe_verbal"])


def test_reconcile_cars_milano_covered():
    guests_data = {
        "confirmed": [
            {"name": "Ludovico B.", "nickname": "", "status": "confirmed", "city": "Milano", "region": "Milano", "party_size": 1},
            {"name": "Emiliano D. C.", "nickname": "", "status": "confirmed", "city": "Modena", "region": "Modena, Mo", "party_size": 1},
        ],
        "maybe_form": [],
    }
    warnings = reconcile_cars(guests_data)
    assert not any("Milano" in w for w in warnings)
    assert any("Modena" in w for w in warnings)


