import pytest
from crunch_csv import crunch_data

def test_crunch_data_empty():
    rows = []
    data = crunch_data(rows)
    assert data["respondents"] == 0
    assert data["confirmed"] == 0
    assert data["maybe"] == 0
    assert data["need_accomodation"] == 0
    assert data["rompicoglioni"] == 0

def test_crunch_data_basic_attendance():
    rows = [
        {
            "Ci sarai martedi 29 Dicembre 2026?": "Sì",
            "Quante persone sarete in totale (tu + accompagnatori)?": "2 persone",
            "Servono posti letto? Se si', quanti?": "0",
            "Intolleranze alimentari, allergie o diete particolari": "Nessuna"
        },
        {
            "Ci sarai martedi 29 Dicembre 2026?": "Forse",
            "Quante persone sarete in totale (tu + accompagnatori)?": "1",
            "Servono posti letto? Se si', quanti?": "0",
            "Intolleranze alimentari, allergie o diete particolari": ""
        }
    ]
    data = crunch_data(rows)
    assert data["respondents"] == 1
    assert data["confirmed"] == 2
    assert data["maybe_respondents"] == 1
    assert data["maybe"] == 1
    assert data["rompicoglioni"] == 0

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
