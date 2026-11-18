"""Test offline per scripts/invitati.py (nessuna chiamata a Google Sheets)."""

import invitati as inv


def test_derive_stato_from_legacy():
    assert inv.derive_stato("90%", "1") == inv.STATI["si"]
    assert inv.derive_stato("50%", "1") == inv.STATI["forse"]
    assert inv.derive_stato("0%", "1") == inv.STATI["no"]
    assert inv.derive_stato("0", "0") == inv.STATI["no"]
    assert inv.derive_stato("", "1") == inv.STATI["forse"]


def test_migrate_legacy_rows_keeps_data_and_derives_stato():
    legacy = [
        inv.LEGACY_HEADER,
        ["Antonella", "Travasoni", "Argenta", "1", "test JOIN", "2026-09-10", "90%"],
        ["Matteo", "Atti", "Argenta / Londra", "0", "in montagna", "2026-09-10", "0%"],
        ["", "", "", "", "", "", ""],  # riga vuota da scartare
    ]
    rows = inv.migrate_legacy_rows(legacy)
    assert rows[0] == inv.HEADER
    assert len(rows) == 3
    antonella = dict(zip(inv.HEADER, rows[1]))
    assert antonella["Nome"] == "Antonella"
    assert antonella["Stato"] == inv.STATI["si"]
    assert antonella["Note"] == "test JOIN"
    assert antonella["Soprannome"] == "" and antonella["Gruppo"] == ""
    matteo = dict(zip(inv.HEADER, rows[2]))
    assert matteo["Stato"] == inv.STATI["no"]


def test_rows_to_dicts_rejects_legacy_header():
    import pytest
    with pytest.raises(ValueError):
        inv.rows_to_dicts([inv.LEGACY_HEADER])


def _p(**kw):
    base = {k: "" for k in inv.HEADER}
    base.update(kw)
    return base


def test_upsert_adds_new_person():
    people, action = inv.upsert([], _p(Soprannome="Cipolla", Stato=inv.STATI["forse"]))
    assert action == "added" and len(people) == 1


def test_upsert_matches_by_nickname_case_insensitive_and_merges():
    existing = [_p(Soprannome="Fraffo", Nome="Maurizio", Cognome="Guerra", Note="vecchia nota")]
    people, action = inv.upsert(existing, _p(Soprannome="fraffo", Stato=inv.STATI["si"], Gruppo="Goliardia Bologna"))
    assert action == "updated" and len(people) == 1
    assert people[0]["Stato"] == inv.STATI["si"]
    assert people[0]["Gruppo"] == "Goliardia Bologna"
    assert people[0]["Note"] == "vecchia nota"  # i vuoti non sovrascrivono
    assert people[0]["Cognome"] == "Guerra"


def test_upsert_matches_by_full_name():
    existing = [_p(Nome="Maurizio", Cognome="Guerra")]
    people, action = inv.upsert(existing, _p(Nome="maurizio ", Cognome="GUERRA", Soprannome="Fraffo"))
    assert action == "updated"
    assert people[0]["Soprannome"] == "Fraffo"


def test_sanitize_drops_private_columns_and_uses_nome_iniziale():
    people = [
        _p(Soprannome="Naser", Nome="X", Cognome="Y", Gruppo="Goliardia Bologna", Stato="⏳ FORSE", Note="segreto"),
        _p(Nome="Andrea", Cognome="Mosca", Stato="✅ CI SONO", Note="delicata"),
        _p(Nome="Andrea", Cognome="degli Angeli"),
        _p(Nome="Solo"),
    ]
    pub = inv.sanitize(people)
    assert list(pub[0].keys()) == inv.PUBLIC_COLS
    assert "Note" not in pub[0] and "Cognome" not in pub[0]
    assert pub[0]["Soprannome"] == "Naser"       # il soprannome vince
    assert pub[1]["Soprannome"] == "Andrea M."   # Nome C., mai il cognome intero
    assert pub[2]["Soprannome"] == "Andrea D."   # iniziale maiuscola anche se minuscola
    assert pub[3]["Soprannome"] == "Solo"        # senza cognome: solo il nome


def test_public_label_edge_cases():
    assert inv.public_label(_p(Nome="  Maurizio ", Cognome=" Guerra ")) == "Maurizio G."
    assert inv.public_label(_p(Cognome="Guerra")) == "G."
    assert inv.public_label(_p()) == ""


def test_summarize_counts_confirmed_heads():
    people = [
        _p(Stato=inv.STATI["si"], **{"Cardinalità": "2"}),
        _p(Stato=inv.STATI["si"], **{"Cardinalità": "1"}),
        _p(Stato=inv.STATI["forse"], **{"Cardinalità": "5"}),
    ]
    s = inv.summarize(people)
    assert s["total"] == 3
    assert s["confirmed_heads"] == 3
    assert s["by_stato"][inv.STATI["forse"]] == 1
