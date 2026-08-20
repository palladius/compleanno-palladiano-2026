sync:
	uv run scripts/sync_fomo.py

crunch:
	uv run scripts/crunch_csv.py

test:
	uvx pytest scripts/test_crunch_csv.py
	npx astro check

