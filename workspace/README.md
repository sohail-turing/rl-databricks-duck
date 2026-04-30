# Workspace

Source-of-truth for everything that gets loaded into the Databricks workspace.

| Subfolder        | What it holds                                                              |
| ---------------- | -------------------------------------------------------------------------- |
| `manifests/`     | YAML manifests — every asset is enumerated here with its taxonomy tag.     |
| `generators/`    | Python data generators (one per canonical entity).                         |
| `notebooks/`     | Source notebooks (.ipynb / .py).                                           |
| `dashboards/`    | Dashboard definitions (JSON / YAML).                                       |
| `drive/`         | Source files for Google Drive — interview notes, briefs, memos.            |

## Manifest contract

Every asset in the workspace must appear in exactly one manifest, tagged with one of:
- `gold` — authoritative for at least one task.
- `distractor:<taxonomy_id>` — see `validator.md` §2.1.
- `anchor:<taxonomy_id>` — see `validator.md` §2.2.
- `noise` — generic noise that isn't claimed by any task.

The manifest is the input to:
1. The loader that creates the assets in the workspace.
2. The coverage-matrix tool that confirms every taxonomy element is exercised.
