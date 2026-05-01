DUCK

python3 -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt

Tier A

./.venv/Scripts/python.exe -m workspace.generators.run --target sqlite --build tier-a --out verification/runs/tier_a_seed.sqlite

Tier B

./.venv/Scripts/python.exe -m workspace.generators.run --target sqlite --build tier-b --out verification/runs/tier_b_seed.sqlite

Tier C

./.venv/Scripts/python.exe -m workspace.generators.run --target sqlite --build tier-c --out verification/runs/tier_c_seed.sqlite --csv-dir verification/exports/tier_c_csv --schema-json-dir verification/schema/tier_c_json
