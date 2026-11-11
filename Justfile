# Compleanno Palladiano 2026 🎂 — `just` mostra questa lista
export UV_INDEX_URL := "https://pypi.org/simple"
export PYTHONPATH := "scripts"

list:
	@just --list

# Sincronizza le FOMO stats dalla form RSVP (Google Sheet → src/data/fomo.json)
sync:
	uv run scripts/sync_fomo.py

# Crunch del CSV locale delle risposte (offline)
crunch:
	uv run scripts/crunch_csv.py

# Dump completo: FOMO stats + whitelist/blacklist invitati
dump: sync invitati-dump

# 🤌 Invitati (tab CAFONAZZI): whitelist/blacklist di chi ti ha già risposto fuori form
# Una tantum: migra il tab allo schema nuovo + dropdown Stato
invitati-setup:
	uv run scripts/invitati.py setup

# Elenca gli invitati raggruppati per stato
invitati:
	uv run scripts/invitati.py list

# Esporta src/data/invitati.csv (pubblico, sanitizzato) + private/invitati_full.csv
invitati-dump:
	uv run scripts/invitati.py dump

# Aggiungi/aggiorna: just invitati-add -s Cipolla -g "Goliardia Bologna" --stato forse
invitati-add *ARGS:
	uv run scripts/invitati.py add {{ARGS}}

# Seed 2026-10-10: i 6 amici Cretini (Goliardia Bologna) dalla foto-annuncio (idempotente)
invitati-seed-goliardia:
	uv run scripts/invitati.py add -s Cipolla      -g "Cretini (Goliardia Bologna)" --stato forse --citta Bologna -f "Foto WhatsApp"
	uv run scripts/invitati.py add -s Paccorabanne -g "Cretini (Goliardia Bologna)" --stato forse --citta Bologna -f "Foto WhatsApp"
	uv run scripts/invitati.py add -s Levriero     -g "Cretini (Goliardia Bologna)" --stato forse --citta Bologna -f "Foto WhatsApp"
	uv run scripts/invitati.py add -s Fraffo -n Maurizio -c Guerra -g "Cretini (Goliardia Bologna)" --stato forse --citta Bologna -f "Foto WhatsApp" --note "Già nella Form RSVP (In forse)"
	uv run scripts/invitati.py add -s Naser        -g "Cretini (Goliardia Bologna)" --stato forse --citta Bologna -f "Foto WhatsApp"
	uv run scripts/invitati.py add -s Aladano -n Andrea -c Lado -g "Cretini (Goliardia Bologna)" --stato forse --citta Bologna -f "Foto WhatsApp"

test:
	uv run --with pytest pytest scripts/test_crunch_csv.py scripts/test_invitati.py
	npx astro check

# Avvia il server di sviluppo Astro in locale (http://localhost:4321/compleanno-palladiano-2026/invitati)
dev:
	npm run dev

# Build statica del sito in dist/
build:
	npm run build
