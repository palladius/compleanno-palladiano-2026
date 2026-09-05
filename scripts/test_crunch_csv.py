import pytest
from crunch_csv import crunch_data, normalize_city, resolve_location, load_mappings

def test_load_mappings_fallback():
    mappings = load_mappings("non_existent_file.csv")
    assert len(mappings) > 0
    # Verifica che pattern più specifici siano ordinati prima
    assert any(m["pattern"] == "castel guelfo" for m in mappings)

def test_resolve_location():
    loc, coords = resolve_location("Zurigo")
    assert loc == "Svizzera"
    assert coords == [47.3769, 8.5417]

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
    assert data["need_accomodation"] == 4
    assert data["rompicoglioni"] == 3
    assert data["dietary_breakdown"]["vegani"] == 1
    assert data["dietary_breakdown"]["celiaci"] == 1
    assert data["dietary_breakdown"]["altro"] == 1
