"""Test offline per scripts/letti.py (nessuna chiamata a Google Sheets)."""

import json
import letti


def test_parse_occupants_privacy_and_split_nights():
    occs = letti.parse_occupants(
        "Fabio Mattei (dal 28), Luca Ferroni (dal 29)",
        "Burattino",
        "2026-12-28",
        "2026-12-30",
        2,
    )
    assert len(occs) == 2
    assert occs[0]["display_name"] == "Fabio M."
    assert occs[0]["nickname"] == "Burattino"
    assert occs[0]["check_in"] == "2026-12-28"
    assert occs[0]["nights"] == 2

    assert occs[1]["display_name"] == "Luca F."
    assert occs[1]["nickname"] == ""
    assert occs[1]["check_in"] == "2026-12-29"
    assert occs[1]["nights"] == 1


def test_sanitize_rooms_strips_emails_and_full_surnames():
    pub = letti.sanitize_rooms_for_public(letti.DEFAULT_ROOMS)
    blob = json.dumps(pub, ensure_ascii=False)
    assert "@" not in blob
    assert "Carlesso" not in blob
    assert "Pizzorni" not in blob
    assert "Mattei" not in blob
    assert "Fregoso" not in blob
    assert "Guarino" not in blob

    s = pub["summary"]
    assert s["confirmed_beds"] == 22
    assert s["maybe_beds"] == 1
    assert s["allocated_beds"] == 23
    # Vicky + Simon (2) + Fabio (1) = 3 pax dal 28 Dicembre
    assert s["dec28_guests"] == 3
    assert s["dec29_guests"] == 23


def test_validate_email_rule():
    # Doppia separati con 1 sola email -> warning
    bad_doppia = {
        "StanzaID": "TEST-1",
        "Tipologia": "Doppia Letti Separati (2)",
        "PostiOccupati": "2",
        "Ospiti": "Luca Fregoso, Ludovico Besana",
        "EmailContatto": "luca.fregoso@gmail.com",
    }
    w1 = letti.validate_email_rule(bad_doppia)
    assert len(w1) == 1 and "ne servono 2" in w1[0]

    # Matrimoniale con 2 email -> warning (basta 1)
    bad_matr = {
        "StanzaID": "TEST-2",
        "Tipologia": "Matrimoniale (2)",
        "PostiOccupati": "2",
        "Ospiti": "Andrea Patrignani, Viktoriya Shablina",
        "EmailContatto": "a@example.com, b@example.com",
    }
    w2 = letti.validate_email_rule(bad_matr)
    assert len(w2) == 1 and "ne basta 1" in w2[0]

    # Doppia corretta (2 email) e Matrimoniale corretta (1 email) -> 0 warning
    assert letti.validate_email_rule(letti.DEFAULT_ROOMS[3]) == []
    assert letti.validate_email_rule(letti.DEFAULT_ROOMS[4]) == []
    assert letti.validate_email_rule(letti.DEFAULT_ROOMS[7]) == []


def test_build_jasmin_email_contains_key_sections():
    txt = letti.build_jasmin_email(letti.DEFAULT_ROOMS)
    assert "ristoranteaidossi.filo@gmail.com" in txt
    assert "23 posti letto" in txt
    assert "Victoria Anreiter, Simon Anreiter" in txt
    assert "Fabio Mattei (dal 28), Luca Ferroni (dal 29)" in txt
    assert "Luca Fregoso, Ludovico Besana" in txt
    assert "Francesco Bullini" in txt
    assert "Guarino" not in txt
    assert "TODO_EMAIL_NICOLA" in txt


def test_sanitize_redacts_surnames_in_room_name():
    dirty = [
        {
            "StanzaID": "X-1",
            "Struttura": "B&B",
            "NomeStanza": "Doppia Fregoso & Besana",
            "Tipologia": "Doppia Letti Separati (2)",
            "PostiMax": "2",
            "Ospiti": "Luca Fregoso, Ludovico Besana",
            "Soprannomi": "",
            "PostiOccupati": "2",
            "CheckIn": "2026-12-29",
            "CheckOut": "2026-12-30",
            "Notti": "1",
            "EmailContatto": "a@b.it, c@d.it",
            "Stato": "🟢 CONFERMATO",
            "Note": "",
        }
    ]
    pub = letti.sanitize_rooms_for_public(dirty)
    rname = pub["rooms"][0]["room_name"]
    assert "Fregoso" not in rname
    assert "Besana" not in rname
    assert rname == "Doppia F. & B."

