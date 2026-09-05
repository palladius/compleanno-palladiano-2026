# 🗺️ Pipeline di Approssimazione delle Provenienze (Geocoding & Aggregazione)

Questo documento descrive la logica e la pipeline di normalizzazione/approssimazione delle provenienze degli invitati al 50° Compleanno Palladiano.

---

## 🎯 Obiettivo & Rationale

Gli invitati compilano il modulo Google RSVP inserendo la loro provenienza in testo libero (es. *"Oberbuchsiten, CH"*, *"San marino RSM"*, *"Da Zurigo o da Fano"*, *"Arzenta"*, *"Castel guelfo di bologna"*).

Senza un'opportuna approssimazione:
- Le risposte si frammentano in decine di entità separate da 1 persona ciascuna.
- L'istogramma in `/stats` (che mostra le città con $> 1$ partecipante) non riflette i veri cluster e carovane.
- Il carpooling in `/map` non aggrega passeggeri della stessa direttrice.

### 📐 Regola di Granularità

1. **Fuori dall'Italia 🌍**: Approssimazione a livello di **Nazione** con punto geografico del capoluogo / hub principale.  
   *Es.* Tutta la Svizzera (Zurigo, Oberbuchsiten, Berna, Ginevra) convoglia in **"Svizzera"** con coordinate di riferimento su **Lugano (`[46.0037, 8.9511]`)** (ottimale per inquadratura e zoom sulla mappa del Nord Italia).
2. **In Italia 🇮🇹**: Approssimazione a livello di **Provincia / Città Metropolitana** con coordinate del capoluogo provinciale.  
   *Es.* 
   - *"Castel guelfo di bologna"*, *"Bulaggna"* $\rightarrow$ **Bologna** (`[44.4949, 11.3426]`)
   - *"Arzenta"*, *"Argenta"* $\rightarrow$ **Ferrara** (`[44.8381, 11.6198]`)
   - *"San marino RSM"*, *"San Marino"* $\rightarrow$ **Rimini** (`[44.0594, 12.5683]`) (stesso bacino / uscita autostradale A14)
   - *"Fabriano, IT"* $\rightarrow$ **Ancona** (`[43.6158, 13.5189]`)
   - *"Raiano"* $\rightarrow$ **L'Aquila** (`[42.3498, 13.3995]`)
   - *"Fano"* $\rightarrow$ **Pesaro e Urbino** (`[43.8406, 12.9142]`)

---

## 📁 Struttura Dati: `src/data/city_mappings.csv`

Il file di mapping include pattern, località normalizzata, coordinate (`lat`, `lng`) e note:

```csv
raw_pattern,normalized_location,lat,lng,notes
zurigo,Svizzera,47.3769,8.5417,Paese estero - hub Zurigo
oberbuchsiten,Svizzera,47.3769,8.5417,Paese estero (Canton Soletta) convoglia su hub Zurigo
ch,Svizzera,47.3769,8.5417,Sigla Svizzera convoglia su hub Zurigo
bologna,Bologna,44.4949,11.3426,Capoluogo / Città Metropolitana
castel guelfo,Bologna,44.4949,11.3426,Comune prov. BO convoglia su Bologna
san marino,Rimini,44.0594,12.5683,RSM convoglia sul bacino Rimini / Riviera
...
```

### Algoritmo di Matching:
1. `raw_city` viene convertito in minuscolo e pulito dagli spazi.
2. Viene cercata la prima sottostringa (`pattern in raw_city_lower`) nel mapping ordinato dal pattern più specifico al più generico.
3. Se trovato, restituisce il nome normalizzato e le coordinate geolocalizzate `[lat, lng]`.
4. Se nessun pattern corrisponde, viene usato un fallback pulito (`strip().title()`, senza coordinate predefinite).

---

## ⚙️ Script di Crunching & Sync

- **[`scripts/crunch_csv.py`](../scripts/crunch_csv.py)**:
  - `load_mappings(file_path)`: carica la tabella con pattern, nome normalizzato e coordinate geografiche.
  - `resolve_location(raw_text)`: mappa il testo libero alla coppia `(location, [lat, lng])`.
  - `normalize_city(raw_text)`: helper di retrocompatibilità che restituisce il solo nome.
  - Aggrega le provenienze e calcola le statistiche per `src/data/fomo.json`.

- **Comandi Justfile**:
  - `just sync`: Sincronizza dal Google Sheet live e rigenera `src/data/fomo.json` con la pipeline di approssimazione.
  - `just crunch`: Rigenera `src/data/fomo.json` dal file CSV locale.
  - `just test`: Esegue la suite di test pytest su `crunch_csv.py`.
