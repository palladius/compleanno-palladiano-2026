# Investigation: Firebase vs Google Forms per l'RSVP

**Data:** 2026-08-19
**Autore:** Antigravity

## Problema
Sostituire o migliorare l'attuale meccanismo di RSVP basato su Google Form, integrando un form direttamente sul sito web e mostrando in tempo reale statistiche come "Persone che hanno già risposto" e "Posti letto rimanenti".

## Opzioni Valutate

### Opzione A: Firebase Firestore
*   **Pro:** Interfaccia 100% integrata nel design del sito, contatori realmente in tempo reale, nessuna dipendenza visibile da piattaforme esterne. Sicuro grazie alle Firebase Security Rules (che impediscono la lettura/scrittura non autorizzata anche se le API keys sono pubbliche).
*   **Contro:** Richiede configurazione lato backend (regole di sicurezza), implementazione JavaScript per leggere/scrivere dati e migrazione dei 10 RSVP già esistenti dal Google Form al nuovo database Firestore.

### Opzione B: Embedded Google Form (Scelta Finale)
*   **Pro:** Semplice e immediato. Preserva le 10 risposte già esistenti e il workflow attuale del festeggiato (che già usa Google Forms). Integrato via `<iframe>` direttamente in `index.astro` in modo che gli utenti non debbano uscire dal sito.
*   **Contro:** L'estetica del form all'interno dell'iframe è legata a Google Forms. Il counter della FOMO non è automaticamente sincronizzato (le variabili `fomoStats` in `index.astro` devono essere aggiornate manualmente).

## Risoluzione
Si è proceduto con l'**Opzione B** per mantenere la semplicità e preservare le risposte esistenti, incorporando l'iframe del Google Form in `index.astro` e aggiungendo le statistiche FOMO aggiornabili manualmente. L'utente ha espresso preoccupazione per la sicurezza delle password di Firebase in un repository pubblico GitHub, che è stata chiarita documentando il funzionamento delle Firebase Security Rules.
