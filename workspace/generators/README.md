# Data generators

One module per canonical entity. Each module exposes:

```python
def generate(seed: int, scale: float = 1.0) -> pyarrow.Table | pandas.DataFrame:
    ...
```

The generators are **target-agnostic**: they produce dataframes that can be written to Delta (Databricks) or to local DuckDB / Parquet for offline development (WS-0).

## Layout

```
generators/
  __init__.py
  run.py                # CLI entrypoint
  customers.py
  accounts.py
  products.py
  campaigns.py
  transactions.py
  financial_periods.py
  cost_centers.py
  fx_rates.py
  employees.py
  it_assets.py
  noise.py              # generators for distractor/noise tables
```

## CLI (target stub)

```
python -m workspace.generators.run --target duckdb --out ./local.duckdb
python -m workspace.generators.run --target databricks --catalog main
```
