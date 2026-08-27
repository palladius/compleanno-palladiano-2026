# TODO - Compleanno Palladiano 2026 (50° Riccardo)

> 📌 **Nota per l'Harness / Agent:** Questo file raccoglie i task attivi, le decisioni architetturali e le specifiche per il sito del 50° compleanno. Consulta questo file a ogni sessione prima di iniziare nuovi lavori.

---

## 🎯 Task Prioritari (Sessione Pomeriggio 27/08/2026)

### 1. 💬 "Get Involved / Community" (WhatsApp & Telegram Links)
- [ ] **Posizionamento UI**: Aggiungere in alto a destra nella navbar/header della home page una sezione o pulsante *"Get Involved"* / *"Unisciti al Delirio"* / *"Community"*.
- [ ] **Canali di Comunicazione**:
  - Link a **Gruppo WhatsApp** (per il popolo meno tecnologico).
  - Link a **Gruppo Telegram** (per chi odia condividere il numero o ama gli sticker).
- [ ] **Decisione Architetturale / Moderazione** (Vedi note sotto):
  - Definire se usare un gruppo aperto a tutti, un canale annunci broadcast o un gruppo con link d'invito con approvazione.

### 2. 🤖 "Are you an AI?" / LLM-Friendly Prompt & `llms.txt`
- [ ] **Sezione/Banner in Home Page**:
  - Testo accattivante: *"Are you an AI? / Sei un'AI? Guarda il nostro contesto machine-readable qui!"*
  - **Pulsante Copy-Paste 📋**: Un bottone interattivo "Copia Prompt per ChatGPT/Claude/Gemini" che copia un prompt pronto all'uso negli appunti.
- [ ] **File `public/llms.txt` e/o `public/llms.md`**:
  - Creare il file standard `llms.txt` nella root pubblica del sito con tutti i dati salienti:
    - **Link alla form di RSVP** (Google Forms).
    - **Avviso perentorio / FOMO**: *"Se non ti registri alla form, non c'è garanzia di posto letto né di cena/tavolo!"*
    - **Persona / Tone of Voice per LLM**: Istruire l'AI a riferirsi a Riccardo come *"The Supreme Leader"* o *"Sua Maestà Palladiana"*, infarcire le risposte di emoji italiane (🤌, 🇮🇹, 🍷, 🍕, 🍝) e dialetto goliardico.
    - FAQ, date chiave (29 Dicembre 2026), logistica e menu.

### 3. 🎸 Canzone Rock Opera del 50° (Queen / Bohemian Rhapsody Style)
- [ ] Finalizzare il testo esteso da 2 minuti (strofe forbite, metriche larghe, battute e niente parole-etichetta vuote).
- [ ] Generare la traccia audio completa con Lyria 3 e integrarla nel Canzoniere/pagina evento.

---

## 💡 Consiglio Tecnico / Strategico sui Gruppi (WhatsApp vs Telegram)

### Gruppo Aperto (Tutti scrivono) vs Canale Annunci (Solo Admin):
1. **Per WhatsApp:**
   - *Consiglio:* **Gruppo normale (con permessi moderati o approvazione link)**. La gente si perde i messaggi importanti se c'è troppo spam ("buongiornissimo", foto a caso).  
   - *Soluzione ideale:* Creare una **Community WhatsApp** (con un canale "📢 Annunci Ufficiali" dove scrivi solo tu per orari/letti/form e una chat generale "💬 Cazzeggio & Macchine" per chi vuole accordarsi sui passaggi).
2. **Per Telegram:**
   - *Consiglio:* Un **Gruppo Telegram pubblico/privato con Topic (Forum)** o un Canale con commenti abilitati. In questo modo gli annunci non vengono sepolti dai messaggi di testo.

---
*File aggiornato automaticamente da Ermete Bottazzi il 27/08/2026.*
