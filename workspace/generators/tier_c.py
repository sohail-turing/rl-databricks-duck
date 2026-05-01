"""Tier C generators for the Meridian Trust milestone slice."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .milestone import GeneratedTable, load_pool_json
from .tier_b import build_tier_b


CAMPAIGN_POOLS = load_pool_json("campaign_pools.json")

ANNOUNCEMENT_TYPES = tuple(CAMPAIGN_POOLS["announcement_types"])
GL_ACCOUNT_CODES = load_pool_json("gl_account_codes.json")


def build_tier_c(
    seed: int,
    scale: float = 1.0,
    users_pool_path: str | Path | None = None,
) -> list[GeneratedTable]:
    if scale <= 0:
        raise ValueError("scale must be greater than zero")

    tier_b_tables = build_tier_b(seed=seed, scale=scale, users_pool_path=users_pool_path)
    table_map = {table.local_name: table.dataframe.copy() for table in tier_b_tables}
    rng = np.random.default_rng(seed + 211)

    periods = table_map["certified.calendar_periods"]
    channels = table_map["certified.channels"]
    employees = table_map["certified.employees"].merge(
        table_map["hr_people.employee_directory"][["employee_id", "role_title", "employment_status"]],
        on="employee_id",
        how="left",
    )
    campaigns = table_map["marketing_campaigns.campaigns"]
    branch_incidents = table_map["ops_branch.branch_incidents"]
    accounts = table_map["certified.accounts"]
    fee_revenue = table_map["finance_core.fee_revenue"]

    campaign_announcements = generate_campaign_announcements(campaigns, channels, periods, rng)
    employee_changes = generate_employee_changes(employees, periods, branch_incidents, rng, scale)
    gl_entries = generate_gl_entries(branch_incidents, accounts, fee_revenue, periods, rng)

    return tier_b_tables + [
        GeneratedTable(
            "main.communication_threads.campaign_announcements",
            "communication_threads",
            "campaign_announcements",
            campaign_announcements,
        ),
        GeneratedTable(
            "main.hr_people.employee_changes",
            "hr_people",
            "employee_changes",
            employee_changes,
        ),
        GeneratedTable("main.finance_gl.gl_entries", "finance_gl", "gl_entries", gl_entries),
    ]


def generate_campaign_announcements(
    campaigns: pd.DataFrame,
    channels: pd.DataFrame,
    periods: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    period_lookup = periods.set_index("period_id")[["start_date", "end_date"]].to_dict("index")
    channel_ids = channels[channels["channel_name"].isin(["Email", "Operations Bridge"])]["channel_id"].tolist()
    if not channel_ids:
        channel_ids = channels["channel_id"].tolist()

    rows: list[dict[str, object]] = []
    for campaign in campaigns.sort_values(["period_id", "campaign_id"]).to_dict("records"):
        period = period_lookup[str(campaign["period_id"])]
        base_ts = pd.Timestamp(period["start_date"]) + pd.Timedelta(days=int(rng.integers(1, 6)), hours=9)

        for offset, announcement_type in enumerate(ANNOUNCEMENT_TYPES[:2] if rng.random() < 0.45 else ANNOUNCEMENT_TYPES):
            rows.append(
                {
                    "campaign_id": campaign["campaign_id"],
                    "channel_id": channel_ids[offset % len(channel_ids)],
                    "period_id": campaign["period_id"],
                    "announcement_ts": base_ts + pd.Timedelta(days=offset * int(rng.integers(2, 7))),
                    "owner_employee_id": campaign["owner_employee_id"],
                    "announcement_type": announcement_type,
                }
            )

    return pd.DataFrame(rows)


def generate_employee_changes(
    employees: pd.DataFrame,
    periods: pd.DataFrame,
    branch_incidents: pd.DataFrame,
    rng: np.random.Generator,
    scale: float,
) -> pd.DataFrame:
    monthly_periods = periods[periods["period_type"] == "month"].sort_values("start_date").tail(12).reset_index(drop=True)
    incident_pressure = branch_incidents.groupby(["branch_id", "period_id"], as_index=False).size()
    pressure_lookup = {
        (row["branch_id"], row["period_id"]): int(row["size"])
        for row in incident_pressure.to_dict("records")
    }

    candidate_employees = employees[
        employees["role_title"].isin(["Operations Analyst", "Service Lead", "Branch Manager", "Relationship Banker"])
    ].copy()
    candidate_employees = candidate_employees.sort_values(["branch_id", "employee_id"]).reset_index(drop=True)

    rows: list[dict[str, object]] = []
    change_counter = max(14, int(round(18 * scale)))
    candidate_records = candidate_employees.to_dict("records")
    departments = ["Operations", "Retail Banking", "Finance", "Marketing", "HR"]

    for index in range(change_counter):
        employee = candidate_records[index % len(candidate_records)]
        weighted_periods = []
        weights = []
        for period in monthly_periods.to_dict("records"):
            weighted_periods.append(period)
            weights.append(1.0 + (0.8 * pressure_lookup.get((employee["branch_id"], period["period_id"]), 0)))

        period = weighted_periods[int(rng.choice(np.arange(len(weighted_periods)), p=_normalize(weights)))]
        old_department = str(employee["department"])
        if old_department == "Operations":
            new_department = str(rng.choice(["Retail Banking", "Operations", "Finance"], p=[0.35, 0.2, 0.45]))
            change_type = "reassignment"
        elif old_department == "Retail Banking":
            new_department = str(rng.choice(["Operations", "Retail Banking", "Marketing"], p=[0.5, 0.15, 0.35]))
            change_type = "temporary_backfill"
        else:
            new_department = str(rng.choice([dept for dept in departments if dept != old_department]))
            change_type = "department_transfer"

        effective_date = pd.Timestamp(period["start_date"]) + pd.Timedelta(days=int(rng.integers(2, 24)))
        rows.append(
            {
                "employee_id": employee["employee_id"],
                "period_id": period["period_id"],
                "branch_id": employee["branch_id"],
                "change_type": change_type,
                "old_department": old_department,
                "new_department": new_department,
                "effective_date": effective_date,
            }
        )

    employee_changes = pd.DataFrame(rows)
    employee_changes = employee_changes.drop_duplicates(["employee_id", "period_id", "change_type"]).reset_index(drop=True)
    return employee_changes


def generate_gl_entries(
    branch_incidents: pd.DataFrame,
    accounts: pd.DataFrame,
    fee_revenue: pd.DataFrame,
    periods: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    monthly_periods = periods[periods["period_type"] == "month"].sort_values("start_date").reset_index(drop=True)
    fee_by_branch_period = fee_revenue.groupby(["branch_id", "period_id"], as_index=False)["fee_amount_usd"].sum()
    fee_lookup = {
        (row["branch_id"], row["period_id"]): float(row["fee_amount_usd"])
        for row in fee_by_branch_period.to_dict("records")
    }
    account_lookup = accounts.groupby("branch_id")["account_id"].apply(list).to_dict()

    rows: list[dict[str, object]] = []
    entry_counter = 1

    for incident in branch_incidents.sort_values(["period_id", "branch_id", "incident_id"]).to_dict("records"):
        branch_accounts = account_lookup.get(str(incident["branch_id"]), [])
        if not branch_accounts:
            continue

        severity_multiplier = {
            "low": 0.004,
            "medium": 0.009,
            "high": 0.017,
            "critical": 0.031,
        }[str(incident["severity"])]
        fee_total = fee_lookup.get((incident["branch_id"], incident["period_id"]), 0.0)
        base_amount = max(150.0, round(fee_total * severity_multiplier * (1.0 + float(rng.normal(0.0, 0.12))), 2))
        account_id = str(rng.choice(branch_accounts))

        debit_rows = [
            {
                "gl_account_code": GL_ACCOUNT_CODES["service_recovery_expense"],
                "amount_usd": round(base_amount * 0.62, 2),
                "entry_type": "debit",
            },
            {
                "gl_account_code": GL_ACCOUNT_CODES["branch_overtime_expense"],
                "amount_usd": round(base_amount * 0.38, 2),
                "entry_type": "debit",
            },
            {
                "gl_account_code": GL_ACCOUNT_CODES["customer_remediation_reserve"],
                "amount_usd": round(base_amount, 2),
                "entry_type": "credit",
            },
        ]

        for entry in debit_rows:
            rows.append(
                {
                    "period_id": incident["period_id"],
                    "branch_id": incident["branch_id"],
                    "account_id": account_id,
                    "gl_account_code": entry["gl_account_code"],
                    "amount_usd": entry["amount_usd"],
                    "entry_type": entry["entry_type"],
                    "entry_id": f"GLE-{entry_counter:06d}",
                }
            )
            entry_counter += 1

    gl_entries = pd.DataFrame(rows)
    return gl_entries[["period_id", "branch_id", "account_id", "gl_account_code", "amount_usd", "entry_type"]]


def _normalize(weights: list[float]) -> np.ndarray:
    values = np.array(weights, dtype=float)
    values = values / values.sum()
    return values
