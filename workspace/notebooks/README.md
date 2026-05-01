# Source Notebooks

This folder contains the current milestone support notebooks used for local discovery and task authoring.

## Current notebooks

| File | Typical use |
| --- | --- |
| `marketing/campaign_launch_timeline.py` | campaign timing, launch windows, and conversion context |
| `operations/incident_service_recovery.py` | incident volume, branch disruption, and service recovery analysis |
| `hr/staffing_change_watch.py` | staffing shifts, payroll context, and branch workforce analysis |

Each notebook should have a matching manifest entry in `workspace/manifests/notebooks.yaml`.

## Working rule

Only reference a notebook in a task's `expected_assets` when the gold path really depends on it.
