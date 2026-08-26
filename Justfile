sync:
	uv run scripts/sync_fomo.py

crunch:
	uv run scripts/crunch_csv.py

test:
	uv run --with pytest pytest scripts/test_crunch_csv.py
	npx astro check

