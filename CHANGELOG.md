# Changelog 📝✨

## [1.0.9] - 2026-09-05
### Changed 🔄
- 🍷 **Venue Pin "Ai Dossi" ad alta visibilità**: Ridelineato e ingrandito il marker della venue sulla mappa (da 36px a 52px, glow radiale aumentato da 44px a 72px) con icona bicchiere di vino 🍷, badge dorato "50" e pill identificativo chiaro "🏰 Ai Dossi (Conselice)".

## [1.0.8] - 2026-09-05
### Added 🚀
- 🗺️ **Pipeline Approssimazione Città & Coordinate**: Introdotto `src/data/city_mappings.csv` e documentazione `docs/LOCATION_APPROXIMATION.md` per normalizzare gli input liberi a livello di provincia (Italia) e nazione (estero) con relative coordinate.
- 🧪 **Test Suite per Crunching**: Aggiornati i test in `scripts/test_crunch_csv.py` per validare l'approssimazione delle coordinate geografiche e l'aggregazione dei partecipanti.
- 💬 **Canali Community**: Aggiunti link diretti al Canale Annunci WhatsApp e al Gruppo Community Telegram nella navbar, nel footer e nella pagina contatti.

### Changed 🔄
- 🚗 **Mappa delle Macchine (`/map`)**:
  - Semplificata la convenzione colori in binario: 🟢 **Verde (Sicuro / Confermato)** e 🟡 **Giallo (In Forse / In Definizione)**.
  - Aggiornato il cluster **Svizzera (Zurigo)** a 9 persone confermate (equipaggio Palladius + Pizzorni + Patrignani).
  - Creato il cluster **Rimini** aggregando Andrea Degli Angeli (San Marino) e Francesco Bullini ("Parigi -> Rimini -> Conselice").
- 📊 **FOMO Stats Sync**: Sincronizzati nuovi dati partecipanti via Google Sheets (15 risposte, 22 ospiti confermati, 13 posti letto).

## [1.0.7] - 2026-08-27
### Changed 🔄
- 🗺️ **Cartografia Google Maps**: Aggiornato il layer della mappa con le tessere e lo stile ufficiale di **Google Maps** (Roadmap) per una perfetta resa estetica Noogler-approved! 🗺️✨

## [1.0.6] - 2026-08-26
### Added 🚀
- 🇨🇭 **Equipaggio Svizzera (Zurigo)**: Aggiunta macchina da 4 persone in partenza da Zurigo via San Gottardo / Chiasso / A1.
- 🗺️ **Mappa e Tile Layer**: Integrato layer OpenStreetMap ufficiale (senza watermark/API key) con inquadratura dinamica `fitBounds` estesa per abbracciare l'intero arco alpino fino a Zurigo e Ginevra.

## [1.0.5] - 2026-08-26
### Changed 🔄
- 🗺️ **Mappa Carpooling (`/map`)**: Semplificato il layout rimuovendo la sezione con l'elenco verboso delle schede dettagli, mantenendo la mappa interattiva a tutto schermo, indicatori KPI e CTA RSVP.

## [1.0.4] - 2026-08-26
### Added 🚀
- 🗺️ **Mappa Carpooling & Carovane (`/map`)**: Aggiunto nuovo endpoint interattivo con mappa Leaflet del Nord & Centro Italia focalizzata sulla venue *Ai Dossi* (Conselice).
- 🚗 **Marker Auto & Equipaggi**:
  - 🟢 **Bologna**: Auto confermata con tooltip "Naser e Karaoke 🎤🚗".
  - 🟡 **Torino**: Badge multiplo (`2 🚗`) per le 2 auto dell'equipaggio sabaudo.
  - 🟡 **Perugia**: 1 auto in organizzazione per la risalita via E45.
  - 👑 **Venue**: Pin dorato animato pulsante su Ai Dossi.
- 📦 **Dati Statici (`src/data/cars.json`)**: Struttura JSON estendibile per sincronizzazione futura con database/fogli.
- 🌐 Supporto multilingua completo (IT/EN) e schede interattive con zoom automatico sulla mappa.

## [1.0.3] - 2026-08-26
### Changed 🔄
- 📊 **FOMO Stats Sync**: Sincronizzati nuovi partecipanti da Google Sheets (12 risposte, 20 confermati, 10 posti letto).

## [1.0.2] - 2026-08-19
### Added 🚀
- 📊 **Dashboard & Stats**: Built a standalone `/stats` page rendering real-time capacity and RSVP form responses.
- 🐍 **Data Pipeline**: Added a Python script (`crunch_csv.py`) and a `just crunch` target to calculate and synchronize Google Forms CSV exports into the UI.
- 🔒 **Security**: Hardened credentials and secrets by utilizing `.env` and `private/` folder instead of hardcoded strings.

## [1.0.1] - 2026-08-19
### Added 🚀
- ✨ Embedded Google Form directly into `index.astro` so users can RSVP without leaving the site.
- 📊 Added a FOMO statistics banner above the RSVP form showing confirmed guests and remaining beds.
- ✉️ Added a contact prompt section linking to `/contatti` for users with questions.
