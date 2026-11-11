# Changelog 📝✨

## [1.2.2] - 2026-10-15
### Added 🚀
- 📸🍻 **L'Annuncio Fotografico degli Amici «Cretini» (`/invitati#annuncio-cretini`)**:
  - Aggiunta la foto ufficiale (`public/images/amici_cretini_bologna.jpg`) con lightbox ingrandibile e mappa della tavolata divisa nei due lati:
    - **Lato Sinistro (da sx):** `1. «Cipolla»`, `2. «Paccorabanne»`, `3. «Levriero»`.
    - **Lato Destro (da dietro a dx):** `4. «Fraffo» (Maurizio G.)`, `5. «Naser»`, `6. «Aladano» (Andrea L.)`.
  - Aggiornati `src/data/nicknames.csv`, `src/data/verbal_guests.csv`, `src/data/invitati.csv`, `src/data/guests.json` e `Justfile` (`invitati-seed-goliardia`) con i nomi reali (`Maurizio Guerra` / `Andrea Lado`, abbreviati in `Maurizio G.` / `Andrea L.` sul sito pubblico) e il spelling `Paccorabanne`.
  - Aggiunta pillola rapida `📸🍻 L'Annuncio dei «Cretini»!` nel banner FOMO in Home Page.

## [1.2.1] - 2026-10-15
### Added 🚀
- 🚗 **Milano Express sulla Mappa (`/map`, `src/data/cars.json`, `src/data/macchine.csv`)**: Aggiunta macchina confermata (🟢) da **Milano** con **Ludovico B.** (+1 papà in forse, + **Luca F.** anche lui confermato da Milano).
- 🔍 **Riconciliazione Automatica Mappa Auto (`reconcile_cars` in `scripts/crunch_csv.py`)**: Ora `just sync` / `just crunch` incrocia automaticamente i dati del Form RSVP con `src/data/cars.json` e avvisa se ci sono invitati fuori provincia (o confermati come Dario da Torino) non ancora allineati sulla mappa `/map`.

## [1.2.0] - 2026-10-14
### Added 🚀
- 🥂 **Pagina FOMO «Chi c'è? Confermati & In Forse» (`/invitati`)**:
  - Nuova pagina interattiva divisa in 3 sezioni: **🟢 Confermati Ufficiali (da Form)**, **🟡 In Forse (da Form)** e **💬 Promessi su WhatsApp / Carovane (manca il Form!)** con monito goliardico di Ermete Bottazzi.
  - 🔒 **Privacy-First (`Nome C.` + `+1`)**: cognomi abbreviati automaticamente (`Riccardo C.`, `Barbara N.`, `Guido M.`) e nomi di morose/partner/figli nascosti dietro pillole `+1` / `+Famiglia`.
  - 🎭 **Soprannomi Goliardici (`src/data/nicknames.csv`)**: supporto per nickname ufficiali (`Palladius`, `Giua'`, `Fraffo`, `Burattino`, `Aladano`, `Naser`, `Levriero`, `Pacco Raban`, `Cipolla`, `Lord O`, `Sonanimalo`) con promozione automatica degli amici storici inseriti nel campo `+1` (es. `Stefano G. -> «Giua'»`).
  - 🔍 **Filtri & Ricerca Istantanea**: barra progresso FOMO, filtri per stato/nickname/+1 e ricerca live per nome, soprannome o città.
  - 🔗 Link aggiunto in Navbar, Mobile Drawer, Footer, Hero CTA, FOMO Banner in Home e pagina `/stats`.

## [1.1.0] - 2026-10-14
### Added 🚀
- 🤌 **Whitelist/Blacklist Invitati** (`scripts/invitati.py`): gestione di chi scrive fuori form ("io ci sono" / "io non ci sono") così si smette di chiederglielo. Fonte di verità: tab `CAFONAZZI` del Google Sheet RSVP (live), esteso con `Soprannome`, `Gruppo`, `Stato` (dropdown ✅/❌/⏳/🤐) e `Fonte`. Comandi `setup` (migra le righe legacy), `add` (upsert, no duplicati), `list`, `dump`.
- 📦 **`just dump`**: ora fa `sync` + `invitati-dump` → `src/data/invitati.csv` (pubblico, sanitizzato: niente cognomi/note) e `private/invitati_full.csv` (gitignored).
- 🍻 **`just invitati-seed-goliardia`**: seed idempotente dei 6 della *Goliardia Bologna* (Aladano, Naser, Fraffo/Maurizio Guerra, Levriero, Pacco Raban, Cipolla) come ⏳ FORSE.
- 🧪 14 test offline (`scripts/test_invitati.py`) su migrazione, upsert e sanitizzazione.

### Changed 🔄
- 🛠️ `Justfile`: prima recipe è `list` (così `just` mostra l'help), export `UV_INDEX_URL` per Derek.

## [1.0.14] - 2026-09-21
### Changed 🔄
- ✉️ **Pagina Contatti**: Rimossa la form email rotta. Ora la pagina mostra solo: 📢 WhatsApp (⭐ consigliato), ✈️ Telegram (backup), e ✍️ Form RSVP con avviso ⚠️ "il posto a tavola NON è garantito senza registrazione".

## [1.0.13] - 2026-09-15
### Changed 🔄
- 🛏️ **Letti Confermati vs In Forse**: Split dei posti letto in `confirmed_beds` (🟢) e `maybe_beds` (🟡) in base allo stato di partecipazione. La pagina `/stats` ora mostra il breakdown dettagliato. Il campo `need_accomodation` rimane come somma totale per backward compatibility.

## [1.0.12] - 2026-09-09
### Changed 🔄
- 🚗 **Mappa & Passaggi (`/map`)**: Sostituito il vecchio bottone contatti con i bottoni diretti della community *"Chiedi su WhatsApp"* e *"Chiedi su Telegram"* nel box di condivisione del viaggio.

## [1.0.11] - 2026-09-08
### Added 🚀
- 🎶 **Musica & Playlist**: Added YouTube playlist link for "Ric al Piano" with hover tooltip to homepage hero subtitle and evening program timeline.
- 🚴 **Triathlon & Strava**: Linked triathlon in hero subtitle to Riccardo's official Strava athlete profile (`athletes/4774708`).
- 🍕 **Scelte Gastronomiche**: Linked avant-garde culinary experiments directly to "I renounce my Italian citizenship" video and cleaned up redundant callout card.
- ⏰ **Programma Compatto**: Ridisegnata la timeline della serata in un formato bullet point compatto ed essenziale a partire dalle 18:00 (HH:MM con descrizione snella in mezza pagina).

## [1.0.10] - 2026-09-05
### Changed 🔄
- 🇨🇭 **Coordinate Svizzera su Lugano**: Spostato il punto di riferimento svizzero su Lugano (`[46.0037, 8.9511]`) permettendo alla mappa di aumentare di 1 livello lo zoom mantenendo visibili tutti i punti da Torino, Abruzzo e Svizzera.
- 🔗 **Promozione Mappa in Home Page**:
  - Aggiunto bottone dorato prominente *"Mappa Auto & Carovane 🚗🗺️"* tra le CTA dell'Hero header.
  - Aggiunta pillola interattiva con link alla mappa nel banner FOMO sopra il modulo RSVP.

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
