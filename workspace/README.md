# Workspace Source

This folder is the repo-side source of truth for assets that support the Meridian Trust milestone and, later, Databricks workspace loading.

## Current subfolders

| Subfolder | Current role |
| --- | --- |
| `manifests/` | YAML manifests for the current tables, notebooks, and drive docs |
| `generators/` | Active SQLite-first synthetic data generators |
| `notebooks/` | Current support notebooks used in local discovery and task authoring |
| `dashboards/` | Reserved for dashboard source files; not populated for the current milestone |
| `drive/` | Current support documents for narrative grounding and later MCP loading |

## Current milestone status

1. generator code is active
2. notebook assets are active
3. drive-doc assets are active
4. dashboard source files are still a placeholder area

## Working rule

Every asset that matters for the milestone should have a corresponding manifest entry so the workspace story stays auditable and reusable later.
