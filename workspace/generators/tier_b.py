"""Tier B generators for the Meridian Trust milestone slice."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .milestone import GeneratedTable, build_tier_a


INTERNAL_CHANNEL_IDS = ("CH-004", "CH-007", "CH-008")
INCIDENT_TYPE_CHOICES = (
    "atm_outage",
    "cash_reconciliation_delay",
    "branch_network_latency",
    "statement_delivery_issue",
    "card_dispute_queue",
)
SEVERITY_LEVELS = ("low", "medium", "high", "critical")
SEVERITY_WEIGHTS = {"low": 1.0, "medium": 1.8, "high": 2.6, "critical": 3.8}
ROLE_BASE_PAY = {
    "Branch Manager": 8_900.0,
    "Relationship Banker": 4_950.0,
    "Operations Analyst": 5_450.0,
    "Service Lead": 5_250.0,
    "Universal Banker": 3_100.0,
    "Campaign Manager": 6_450.0,
    "Payroll Specialist": 5_850.0,
    "Finance Analyst": 6_200.0,
    "Small Business Banker": 5_900.0,
    "Branch Operations Specialist": 5_050.0,
    "Teller": 2_650.0,
    "Fraud Resolution Analyst": 5_650.0,
}
ROLE_BONUS_RATE = {
    "Branch Manager": 0.12,
    "Relationship Banker": 0.05,
    "Operations Analyst": 0.03,
    "Service Lead": 0.04,
    "Universal Banker": 0.02,
    "Campaign Manager": 0.09,
    "Payroll Specialist": 0.02,
    "Finance Analyst": 0.05,
    "Small Business Banker": 0.07,
    "Branch Operations Specialist": 0.03,
    "Teller": 0.01,
    "Fraud Resolution Analyst": 0.04,
}
MESSAGE_TYPES_BY_DEPARTMENT = {
    "Retail Banking": ("team_announcement", "branch_update", "service_alert"),
    "Operations": ("incident_followup", "service_alert", "branch_update"),
    "Marketing": ("campaign_launch", "campaign_update", "team_announcement"),
    "HR": ("onboarding_update", "policy_update", "team_announcement"),
    "Finance": ("performance_update", "policy_update", "team_announcement"),
}
MESSAGE_CHANNEL_BY_TYPE = {
    "team_announcement": "CH-004",
    "branch_update": "CH-007",
    "service_alert": "CH-008",
    "incident_followup": "CH-008",
    "campaign_launch": "CH-004",
    "campaign_update": "CH-004",
    "onboarding_update": "CH-004",
    "policy_update": "CH-007",
    "performance_update": "CH-007",
}
SLA_THRESHOLDS = {
    "low": {"response": 90, "resolution": 720},
    "medium": {"response": 60, "resolution": 480},
    "high": {"response": 40, "resolution": 300},
    "critical": {"response": 25, "resolution": 180},
}
CONVERSION_REVENUE = {"deposits": 190.0, "cards": 335.0, "lending": 980.0}
DEPOSIT_BALANCE_FACTOR = {
    "retail checking": 0.86,
    "high-yield savings": 0.93,
    "small-business checking": 0.89,
}


def build_tier_b(
    seed: int,
    scale: float = 1.0,
    users_pool_path: str | Path | None = None,
) -> list[GeneratedTable]:
    if scale <= 0:
        raise ValueError("scale must be greater than zero")

    tier_a_tables = build_tier_a(seed=seed, scale=scale, users_pool_path=users_pool_path)
    table_map = {table.local_name: table.dataframe.copy() for table in tier_a_tables}
    rng = np.random.default_rng(seed + 101)

    periods = table_map["certified.calendar_periods"]
    branches = table_map["certified.branches"]
    products = table_map["certified.products"]
    channels = table_map["certified.channels"]
    employees = table_map["certified.employees"].merge(
        table_map["hr_people.employee_directory"][
            ["employee_id", "role_title", "employment_status"]
        ],
        on="employee_id",
        how="left",
    )
    accounts = table_map["certified.accounts"]
    campaigns = table_map["marketing_campaigns.campaigns"]

    branch_incidents = generate_branch_incidents(branches, periods, rng, scale)
    payroll_runs = generate_payroll_runs(employees, periods, rng)
    incident_threads = generate_incident_threads(branch_incidents, rng)
    channel_messages = generate_channel_messages(employees, periods, channels, rng, scale)
    deposit_balances = generate_deposit_balances(accounts, products, periods, branch_incidents, rng)
    lead_conversions = generate_lead_conversions(campaigns, accounts, products, periods, rng, scale)
    service_sla_events = generate_service_sla_events(branch_incidents, rng)

    return tier_a_tables + [
        GeneratedTable("main.hr_payroll.payroll_runs", "hr_payroll", "payroll_runs", payroll_runs),
        GeneratedTable(
            "main.marketing_attribution.lead_conversions",
            "marketing_attribution",
            "lead_conversions",
            lead_conversions,
        ),
        GeneratedTable(
            "main.communication_threads.incident_threads",
            "communication_threads",
            "incident_threads",
            incident_threads,
        ),
        GeneratedTable("main.ops_branch.branch_incidents", "ops_branch", "branch_incidents", branch_incidents),
        GeneratedTable(
            "main.communication_threads.channel_messages",
            "communication_threads",
            "channel_messages",
            channel_messages,
        ),
        GeneratedTable(
            "main.finance_core.deposit_balances",
            "finance_core",
            "deposit_balances",
            deposit_balances,
        ),
        GeneratedTable(
            "main.ops_branch.service_sla_events",
            "ops_branch",
            "service_sla_events",
            service_sla_events,
        ),
    ]


def generate_payroll_runs(
    employees: pd.DataFrame,
    periods: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    monthly_periods = periods[periods["period_type"] == "month"].sort_values("start_date").reset_index(drop=True)
    branch_ids = sorted(employees["branch_id"].dropna().unique())
    branch_factor = {branch_id: 0.97 + (index * 0.018) for index, branch_id in enumerate(branch_ids)}
    rows: list[dict[str, object]] = []

    for employee in employees.to_dict("records"):
        hire_date = pd.Timestamp(employee["hire_date"])
        eligible_periods = monthly_periods[monthly_periods["end_date"] >= hire_date]
        base_pay_anchor = ROLE_BASE_PAY.get(str(employee["role_title"]), 4_900.0)
        if employee["employment_type"] == "Part-time":
            base_pay_anchor *= 0.62

        for period in eligible_periods.to_dict("records"):
            period_start = pd.Timestamp(period["start_date"])
            months_tenure = max(0, _months_between(hire_date, period_start))
            growth = 1.0 + (0.0025 * min(months_tenure, 36))
            seasonal = 1.02 if int(period_start.month) in (3, 6, 9, 12) else 1.0
            noise = 1.0 + float(rng.normal(0.0, 0.015))
            base_pay = round(
                base_pay_anchor * branch_factor[str(employee["branch_id"])] * growth * seasonal * noise,
                2,
            )

            base_bonus_rate = ROLE_BONUS_RATE.get(str(employee["role_title"]), 0.02)
            quarter_multiplier = 1.4 if int(period_start.month) in (3, 6, 9, 12) else 0.35
            bonus_pay = round(base_pay * base_bonus_rate * quarter_multiplier * max(0.2, 1.0 + float(rng.normal(0.0, 0.18))), 2)

            rows.append(
                {
                    "employee_id": employee["employee_id"],
                    "period_id": period["period_id"],
                    "branch_id": employee["branch_id"],
                    "base_pay_usd": base_pay,
                    "bonus_pay_usd": bonus_pay,
                    "total_pay_usd": round(base_pay + bonus_pay, 2),
                }
            )

    return pd.DataFrame(rows)


def generate_branch_incidents(
    branches: pd.DataFrame,
    periods: pd.DataFrame,
    rng: np.random.Generator,
    scale: float,
) -> pd.DataFrame:
    monthly_periods = periods[periods["period_type"] == "month"].sort_values("start_date").tail(12).reset_index(drop=True)
    rows: list[dict[str, object]] = []
    incident_counter = 1

    for branch in branches.to_dict("records"):
        branch_number = int(str(branch["branch_id"]).split("-")[-1])
        for period in monthly_periods.to_dict("records"):
            period_start = pd.Timestamp(period["start_date"])
            base_lambda = 0.42 + (0.05 * (branch_number % 4))
            if branch["state_code"] == "FL" and int(period_start.month) in (8, 9, 10):
                base_lambda += 0.45
            if branch["state_code"] == "GA" and int(period_start.month) in (7, 8, 9):
                base_lambda += 0.18
            if branch["state_code"] == "SC" and int(period_start.month) in (1, 2):
                base_lambda += 0.12

            incident_count = int(rng.poisson(base_lambda * max(0.85, scale)))
            if incident_count == 0 and rng.random() < 0.14:
                incident_count = 1

            for _ in range(incident_count):
                severity = _incident_severity(branch["state_code"], int(period_start.month), rng)
                opened_ts = _random_timestamp_in_period(period["start_date"], period["end_date"], rng)
                resolution_minutes = int(rng.integers(*_resolution_window_for_severity(severity)))
                rows.append(
                    {
                        "incident_id": f"INC-{incident_counter:06d}",
                        "branch_id": branch["branch_id"],
                        "period_id": period["period_id"],
                        "channel_id": str(rng.choice(["CH-007", "CH-008"])),
                        "incident_type": str(rng.choice(INCIDENT_TYPE_CHOICES)),
                        "severity": severity,
                        "opened_ts": opened_ts,
                        "resolved_ts": opened_ts + pd.Timedelta(minutes=resolution_minutes),
                    }
                )
                incident_counter += 1

    return pd.DataFrame(rows)


def generate_incident_threads(
    branch_incidents: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for incident in branch_incidents.to_dict("records"):
        severity = str(incident["severity"])
        message_floor = {"low": 8, "medium": 16, "high": 28, "critical": 42}[severity]
        message_ceiling = {"low": 18, "medium": 32, "high": 56, "critical": 82}[severity]
        rows.append(
            {
                "channel_id": incident["channel_id"],
                "branch_id": incident["branch_id"],
                "period_id": incident["period_id"],
                "incident_id": incident["incident_id"],
                "thread_ts": pd.Timestamp(incident["opened_ts"]) + pd.Timedelta(minutes=int(rng.integers(5, 95))),
                "severity": severity,
                "message_count": int(rng.integers(message_floor, message_ceiling)),
            }
        )

    return pd.DataFrame(rows)


def generate_channel_messages(
    employees: pd.DataFrame,
    periods: pd.DataFrame,
    channels: pd.DataFrame,
    rng: np.random.Generator,
    scale: float,
) -> pd.DataFrame:
    monthly_periods = periods[periods["period_type"] == "month"].sort_values("start_date").tail(12).reset_index(drop=True)
    valid_channels = set(channels["channel_id"].tolist())
    rows: list[dict[str, object]] = []

    for employee in employees.to_dict("records"):
        hire_date = pd.Timestamp(employee["hire_date"])
        eligible_periods = monthly_periods[monthly_periods["end_date"] >= hire_date]
        if eligible_periods.empty:
            continue

        for period in eligible_periods.to_dict("records"):
            period_start = pd.Timestamp(period["start_date"])
            message_lambda = 1.0
            if employee["department"] == "Operations":
                message_lambda = 1.9
            elif employee["department"] == "Marketing":
                message_lambda = 1.6
            elif employee["department"] == "HR":
                message_lambda = 1.35
            elif employee["role_title"] == "Branch Manager":
                message_lambda = 1.55

            if 0 <= (period_start - hire_date).days <= 180:
                message_lambda += 0.75

            message_count = max(1, int(rng.poisson(message_lambda * max(0.9, scale))))
            for _ in range(min(message_count, 4)):
                message_type = _pick_message_type(employee, period_start, hire_date, rng)
                channel_id = MESSAGE_CHANNEL_BY_TYPE.get(message_type, "CH-007")
                if channel_id not in valid_channels:
                    channel_id = str(rng.choice(INTERNAL_CHANNEL_IDS))

                rows.append(
                    {
                        "channel_id": channel_id,
                        "employee_id": employee["employee_id"],
                        "period_id": period["period_id"],
                        "message_ts": _random_timestamp_in_period(period["start_date"], period["end_date"], rng),
                        "message_type": message_type,
                        "engagement_count": _engagement_count_for_message(message_type, employee["department"], rng),
                    }
                )

    return pd.DataFrame(rows)


def generate_deposit_balances(
    accounts: pd.DataFrame,
    products: pd.DataFrame,
    periods: pd.DataFrame,
    branch_incidents: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    monthly_periods = periods[periods["period_type"] == "month"].sort_values("start_date").reset_index(drop=True)
    products_lookup = products.set_index("product_id")[["product_family", "product_group"]].to_dict("index")
    severity_score = branch_incidents.assign(
        severity_score=branch_incidents["severity"].map(SEVERITY_WEIGHTS)
    )
    incident_pressure = severity_score.groupby(["branch_id", "period_id"], as_index=False)["severity_score"].sum()
    pressure_lookup = {
        (row["branch_id"], row["period_id"]): float(row["severity_score"])
        for row in incident_pressure.to_dict("records")
    }

    rows: list[dict[str, object]] = []
    for account in accounts.to_dict("records"):
        product = products_lookup[str(account["product_id"])]
        if product["product_group"] != "deposits":
            continue

        open_date = pd.Timestamp(account["account_open_date"])
        eligible_periods = monthly_periods[monthly_periods["end_date"] >= open_date]
        base_balance = float(account["current_balance_usd"])
        growth_anchor = DEPOSIT_BALANCE_FACTOR[product["product_family"]]

        for period in eligible_periods.to_dict("records"):
            period_start = pd.Timestamp(period["start_date"])
            months_open = max(0, _months_between(open_date, period_start))
            growth = growth_anchor + (0.010 * min(months_open, 18))
            seasonal = 1.0 + (0.03 * np.sin((int(period_start.month) / 12.0) * 2.0 * np.pi))
            incident_drag = 1.0 - min(0.14, pressure_lookup.get((account["branch_id"], period["period_id"]), 0.0) * 0.012)
            noise = 1.0 + float(rng.normal(0.0, 0.025))
            ending_balance = max(250.0, round(base_balance * growth * seasonal * incident_drag * noise, 2))
            average_balance = round(ending_balance * (0.91 + (0.06 * float(rng.random()))), 2)

            rows.append(
                {
                    "account_id": account["account_id"],
                    "customer_id": account["customer_id"],
                    "branch_id": account["branch_id"],
                    "period_id": period["period_id"],
                    "ending_balance_usd": ending_balance,
                    "average_balance_usd": average_balance,
                }
            )

    return pd.DataFrame(rows)


def generate_lead_conversions(
    campaigns: pd.DataFrame,
    accounts: pd.DataFrame,
    products: pd.DataFrame,
    periods: pd.DataFrame,
    rng: np.random.Generator,
    scale: float,
) -> pd.DataFrame:
    products_lookup = products.set_index("product_id")[["product_group"]].to_dict("index")
    periods_lookup = periods[periods["period_type"] == "month"].set_index("period_id")[["start_date", "end_date"]].to_dict("index")
    account_pool = accounts.copy()
    account_pool["account_open_date"] = pd.to_datetime(account_pool["account_open_date"])
    used_accounts: set[str] = set()
    rows: list[dict[str, object]] = []

    for campaign in campaigns.sort_values(["period_id", "campaign_id"]).to_dict("records"):
        campaign_period = periods_lookup[str(campaign["period_id"])]
        window_start = pd.Timestamp(campaign_period["start_date"])
        window_end = pd.Timestamp(campaign_period["end_date"]) + pd.Timedelta(days=45)
        eligible = account_pool[
            (account_pool["product_id"] == campaign["product_id"])
            & (~account_pool["account_id"].isin(used_accounts))
        ]
        timely = eligible[
            (eligible["account_open_date"] >= window_start)
            & (eligible["account_open_date"] <= window_end)
        ]
        if timely.empty:
            timely = eligible
        if timely.empty:
            continue

        desired_count = max(12, int(round((16 + int(rng.integers(0, 8))) * scale)))
        selected_index = rng.choice(timely.index.to_numpy(), size=min(desired_count, len(timely)), replace=False)
        selected_accounts = timely.loc[selected_index].sort_values("account_open_date")

        for account in selected_accounts.to_dict("records"):
            open_date = pd.Timestamp(account["account_open_date"])
            conversion_ts = max(open_date, window_start) + pd.Timedelta(
                days=int(rng.integers(0, 7)),
                hours=int(rng.integers(8, 18)),
                minutes=int(rng.integers(0, 60)),
            )
            conversion_status = str(rng.choice(["converted", "nurturing", "closed_lost"], p=[0.68, 0.19, 0.13]))
            product_group = products_lookup[str(account["product_id"])] ["product_group"]
            booked_revenue = 0.0
            if conversion_status == "converted":
                booked_revenue = round(CONVERSION_REVENUE[product_group] * (1.0 + float(rng.normal(0.0, 0.08))), 2)

            period_id = _month_period_id(conversion_ts)
            if period_id not in periods_lookup:
                period_id = str(campaign["period_id"])

            rows.append(
                {
                    "campaign_id": campaign["campaign_id"],
                    "customer_id": account["customer_id"],
                    "account_id": account["account_id"],
                    "period_id": period_id,
                    "conversion_status": conversion_status,
                    "conversion_ts": conversion_ts,
                    "booked_revenue_usd": booked_revenue,
                }
            )
            used_accounts.add(str(account["account_id"]))

    return pd.DataFrame(rows)


def generate_service_sla_events(
    branch_incidents: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for index, incident in enumerate(branch_incidents.to_dict("records"), start=1):
        severity = str(incident["severity"])
        thresholds = SLA_THRESHOLDS[severity]
        total_resolution_minutes = max(
            30,
            int((pd.Timestamp(incident["resolved_ts"]) - pd.Timestamp(incident["opened_ts"])).total_seconds() // 60),
        )
        response_minutes = int(max(5, total_resolution_minutes * float(rng.uniform(0.08, 0.24))))
        resolution_minutes = int(max(response_minutes + 20, total_resolution_minutes * float(rng.uniform(0.88, 1.08))))
        rows.append(
            {
                "sla_event_id": f"SLA-{index:06d}",
                "branch_id": incident["branch_id"],
                "period_id": incident["period_id"],
                "incident_id": incident["incident_id"],
                "response_minutes": response_minutes,
                "resolution_minutes": resolution_minutes,
                "sla_breached_flag": bool(
                    response_minutes > thresholds["response"] or resolution_minutes > thresholds["resolution"]
                ),
            }
        )

    return pd.DataFrame(rows)


def _incident_severity(state_code: str, month_number: int, rng: np.random.Generator) -> str:
    weights = np.array([0.36, 0.38, 0.19, 0.07], dtype=float)
    if state_code == "FL" and month_number in (8, 9, 10):
        weights = np.array([0.24, 0.36, 0.28, 0.12], dtype=float)
    elif month_number in (11, 12):
        weights = np.array([0.31, 0.41, 0.20, 0.08], dtype=float)
    weights = weights / weights.sum()
    return str(rng.choice(SEVERITY_LEVELS, p=weights))


def _resolution_window_for_severity(severity: str) -> tuple[int, int]:
    windows = {
        "low": (90, 720),
        "medium": (180, 1_440),
        "high": (480, 2_880),
        "critical": (720, 4_320),
    }
    return windows[severity]


def _pick_message_type(
    employee: dict[str, object],
    period_start: pd.Timestamp,
    hire_date: pd.Timestamp,
    rng: np.random.Generator,
) -> str:
    department = str(employee["department"])
    default_types = MESSAGE_TYPES_BY_DEPARTMENT.get(department, ("team_announcement", "branch_update", "policy_update"))
    if 0 <= (period_start - hire_date).days <= 180 and rng.random() < 0.42:
        return "onboarding_update"
    return str(rng.choice(default_types))


def _engagement_count_for_message(message_type: str, department: str, rng: np.random.Generator) -> int:
    base = {
        "onboarding_update": 20,
        "campaign_launch": 28,
        "campaign_update": 18,
        "incident_followup": 24,
        "service_alert": 22,
        "branch_update": 16,
        "policy_update": 14,
        "performance_update": 12,
        "team_announcement": 10,
    }.get(message_type, 10)
    if department == "Operations":
        base += 4
    if department == "Marketing" and message_type.startswith("campaign"):
        base += 6
    return int(max(1, round(base * float(rng.uniform(0.65, 1.55)))))


def _random_timestamp_in_period(start_date: object, end_date: object, rng: np.random.Generator) -> pd.Timestamp:
    start_ts = pd.Timestamp(start_date) + pd.Timedelta(hours=8)
    end_ts = pd.Timestamp(end_date) + pd.Timedelta(hours=18)
    span_minutes = max(1, int((end_ts - start_ts).total_seconds() // 60))
    return start_ts + pd.Timedelta(minutes=int(rng.integers(0, span_minutes)))


def _months_between(start_date: pd.Timestamp, end_date: pd.Timestamp) -> int:
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)
    return (end_ts.year - start_ts.year) * 12 + (end_ts.month - start_ts.month)


def _month_period_id(timestamp: pd.Timestamp) -> str:
    ts = pd.Timestamp(timestamp)
    return f"{ts.year}-M{ts.month:02d}"