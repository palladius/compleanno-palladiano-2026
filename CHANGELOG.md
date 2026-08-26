# Changelog 📝✨

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
