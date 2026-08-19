
# Translations

A lot of Italian insider jokes are here. When translating to English, try to translate the joke, if this is not possible, remove them. 
* Eg, do not translate "in odor di Toscana", just remove that!

## RSVP Strategy
*   We use an **Embedded Google Form** via iframe instead of an internal Firebase DB to preserve simplicity and the existing 10 responses.
*   The FOMO stats counter (confirmed guests, remaining beds) is hardcoded via `fomoStats` in `index.astro` and must be updated manually.
