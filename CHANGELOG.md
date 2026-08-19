# Changelog 📝✨

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
