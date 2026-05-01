"""Tier B generators for the Meridian Trust milestone slice."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from .milestone import GeneratedTable, build_tier_a, load_pool_json


INCIDENT_POOLS = load_pool_json("incident_pools.json")
PAYROLL_ROLE_POOLS = load_pool_json("payroll_role_pools.json")
COMMUNICATION_POOLS = load_pool_json("communication_pools.json")
PRODUCT_FINANCIALS = load_pool_json("product_financials.json")
HR_ANALYTICS_POOLS = load_pool_json("hr_analytics_pools.json")

INTERNAL_CHANNEL_IDS = tuple(INCIDENT_POOLS["internal_channel_ids"])
INCIDENT_TYPE_CHOICES = tuple(INCIDENT_POOLS["incident_type_choices"])
SEVERITY_LEVELS = tuple(INCIDENT_POOLS["severity_levels"])
SEVERITY_WEIGHTS = INCIDENT_POOLS["severity_weights"]
SLA_THRESHOLDS = INCIDENT_POOLS["sla_thresholds"]

ROLE_BASE_PAY = PAYROLL_ROLE_POOLS["role_base_pay"]
ROLE_BONUS_RATE = PAYROLL_ROLE_POOLS["role_bonus_rate"]
ROLE_JOB_FAMILY = {
    role_title: tuple(job_family)
    for role_title, job_family in PAYROLL_ROLE_POOLS["role_job_family"].items()
}

MESSAGE_TYPES_BY_DEPARTMENT = {
    department: tuple(message_types)
    for department, message_types in COMMUNICATION_POOLS["message_types_by_department"].items()
}
MESSAGE_CHANNEL_BY_TYPE = COMMUNICATION_POOLS["message_channel_by_type"]

CONVERSION_REVENUE = PRODUCT_FINANCIALS["conversion_revenue"]
DEPOSIT_BALANCE_FACTOR = PRODUCT_FINANCIALS["deposit_balance_factor"]
DEPARTMENT_FUNCTION_GROUP = HR_ANALYTICS_POOLS["department_function_group"]
BENEFIT_PLAN_SPECS = load_pool_json("benefit_plan_specs.json")


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

    hr_rng = np.random.default_rng(seed + 157)
    departments = generate_departments(employees)
    job_roles = generate_job_roles(employees, departments)
    employee_assignments = generate_employee_assignments(employees, departments, job_roles, hr_rng)
    reporting_lines = generate_reporting_lines(employee_assignments)
    compensation_history = generate_employee_compensation_history(payroll_runs, employees, departments, job_roles)
    benefit_plans = generate_benefit_plans()
    benefit_enrollments = generate_benefit_enrollments(employees, benefit_plans, hr_rng)
    time_off_requests = generate_time_off_requests(employees, periods, branch_incidents, hr_rng, scale)
    performance_reviews = generate_performance_reviews(employees, periods, payroll_runs, branch_incidents, hr_rng)
    onboarding_cases = generate_onboarding_cases(employees, periods, hr_rng, scale)

    return tier_a_tables + [
        GeneratedTable("main.hr_people.departments", "hr_people", "departments", departments),
        GeneratedTable("main.hr_people.job_roles", "hr_people", "job_roles", job_roles),
        GeneratedTable(
            "main.hr_people.employee_assignments",
            "hr_people",
            "employee_assignments",
            employee_assignments,
        ),
        GeneratedTable("main.hr_people.reporting_lines", "hr_people", "reporting_lines", reporting_lines),
        GeneratedTable(
            "main.hr_people.time_off_requests",
            "hr_people",
            "time_off_requests",
            time_off_requests,
        ),
        GeneratedTable(
            "main.hr_people.performance_reviews",
            "hr_people",
            "performance_reviews",
            performance_reviews,
        ),
        GeneratedTable("main.hr_people.onboarding_cases", "hr_people", "onboarding_cases", onboarding_cases),
        GeneratedTable(
            "main.hr_payroll.employee_compensation_history",
            "hr_payroll",
            "employee_compensation_history",
            compensation_history,
        ),
        GeneratedTable("main.hr_payroll.payroll_runs", "hr_payroll", "payroll_runs", payroll_runs),
        GeneratedTable("main.hr_benefits.benefit_plans", "hr_benefits", "benefit_plans", benefit_plans),
        GeneratedTable(
            "main.hr_benefits.benefit_enrollments",
            "hr_benefits",
            "benefit_enrollments",
            benefit_enrollments,
        ),
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


def generate_departments(employees: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for index, department_name in enumerate(sorted(employees["department"].dropna().unique()), start=1):
        department_employees = employees[employees["department"] == department_name]
        branch_managers = department_employees[department_employees["role_title"] == "Branch Manager"]
        owner_pool = branch_managers if not branch_managers.empty else department_employees
        owner_employee_id = str(owner_pool.sort_values("employee_id").iloc[0]["employee_id"])
        rows.append(
            {
                "department_id": f"DPT-{index:03d}",
                "department_name": department_name,
                "function_group": DEPARTMENT_FUNCTION_GROUP.get(str(department_name), "corporate"),
                "executive_owner_employee_id": owner_employee_id,
                "active_flag": True,
            }
        )

    return pd.DataFrame(rows)


def generate_job_roles(employees: pd.DataFrame, departments: pd.DataFrame) -> pd.DataFrame:
    department_lookup = departments.set_index("department_name")["department_id"].to_dict()
    rows: list[dict[str, object]] = []
    unique_roles = employees[["department", "role_title", "employment_type"]].drop_duplicates()
    unique_roles = unique_roles.sort_values(["department", "role_title"]).reset_index(drop=True)

    for index, role in enumerate(unique_roles.to_dict("records"), start=1):
        role_title = str(role["role_title"])
        job_family, job_level = ROLE_JOB_FAMILY.get(role_title, ("branch_operations", "P2"))
        monthly_base = ROLE_BASE_PAY.get(role_title, 4_900.0)
        rows.append(
            {
                "role_id": f"ROLE-{index:03d}",
                "department_id": department_lookup[str(role["department"])],
                "role_title": role_title,
                "job_family": job_family,
                "job_level": job_level,
                "exempt_flag": role["employment_type"] == "Full-time" and monthly_base >= 4_800.0,
                "annual_salary_min_usd": round(monthly_base * 12 * 0.82, 2),
                "annual_salary_mid_usd": round(monthly_base * 12, 2),
                "annual_salary_max_usd": round(monthly_base * 12 * 1.23, 2),
            }
        )

    return pd.DataFrame(rows)


def generate_employee_assignments(
    employees: pd.DataFrame,
    departments: pd.DataFrame,
    job_roles: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    department_lookup = departments.set_index("department_name")["department_id"].to_dict()
    role_lookup = {
        (row["department_id"], row["role_title"]): row["role_id"]
        for row in job_roles.to_dict("records")
    }
    rows: list[dict[str, object]] = []

    for index, employee in enumerate(employees.sort_values("employee_id").to_dict("records"), start=1):
        department_id = department_lookup[str(employee["department"])]
        role_id = role_lookup[(department_id, str(employee["role_title"]))]
        fte = 1.0 if employee["employment_type"] == "Full-time" else round(float(rng.uniform(0.45, 0.65)), 2)
        work_location_type = "branch" if str(employee["department"]) in {"Retail Banking", "Operations"} else str(
            rng.choice(["branch", "hybrid", "remote"], p=[0.52, 0.35, 0.13])
        )

        rows.append(
            {
                "assignment_id": f"ASN-{index:06d}",
                "employee_id": employee["employee_id"],
                "branch_id": employee["branch_id"],
                "department_id": department_id,
                "role_id": role_id,
                "manager_id": employee["manager_id"],
                "cost_center_id": _cost_center_id(employee["branch_id"], department_id),
                "fte": fte,
                "work_location_type": work_location_type,
                "effective_start_date": employee["hire_date"],
                "effective_end_date": pd.NaT,
                "assignment_status": "active",
            }
        )

    return pd.DataFrame(rows)


def generate_reporting_lines(employee_assignments: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for index, assignment in enumerate(
        employee_assignments[employee_assignments["manager_id"].notna()].sort_values("employee_id").to_dict("records"),
        start=1,
    ):
        rows.append(
            {
                "reporting_line_id": f"RPT-{index:06d}",
                "employee_id": assignment["employee_id"],
                "manager_employee_id": assignment["manager_id"],
                "branch_id": assignment["branch_id"],
                "effective_start_date": assignment["effective_start_date"],
                "effective_end_date": pd.NaT,
                "reporting_type": "direct",
            }
        )

    return pd.DataFrame(rows)


def generate_employee_compensation_history(
    payroll_runs: pd.DataFrame,
    employees: pd.DataFrame,
    departments: pd.DataFrame,
    job_roles: pd.DataFrame,
) -> pd.DataFrame:
    employee_roles = employees[["employee_id", "department", "role_title", "employment_type"]].copy()
    role_lookup = {
        (row["department_id"], row["role_title"]): row
        for row in job_roles.to_dict("records")
    }
    department_id_by_name = departments.set_index("department_name")["department_id"].to_dict()

    rows: list[dict[str, object]] = []
    employee_lookup = employee_roles.set_index("employee_id").to_dict("index")
    for index, payroll in enumerate(payroll_runs.sort_values(["employee_id", "period_id"]).to_dict("records"), start=1):
        employee = employee_lookup[str(payroll["employee_id"])]
        department_id = department_id_by_name[str(employee["department"])]
        role = role_lookup[(department_id, str(employee["role_title"]))]
        fte = 1.0 if employee["employment_type"] == "Full-time" else 0.55
        annualized = round(float(payroll["base_pay_usd"]) * 12 / max(fte, 0.01), 2)
        rows.append(
            {
                "compensation_snapshot_id": f"COMP-{index:07d}",
                "employee_id": payroll["employee_id"],
                "period_id": payroll["period_id"],
                "branch_id": payroll["branch_id"],
                "department_id": department_id,
                "role_id": role["role_id"],
                "cost_center_id": _cost_center_id(payroll["branch_id"], department_id),
                "pay_type": "salary" if employee["employment_type"] == "Full-time" else "hourly",
                "annualized_base_pay_usd": annualized,
                "monthly_base_pay_usd": payroll["base_pay_usd"],
                "monthly_bonus_pay_usd": payroll["bonus_pay_usd"],
                "salary_band_position_pct": round(
                    min(
                        1.0,
                        max(
                            0.0,
                            (annualized - float(role["annual_salary_min_usd"]))
                            / (float(role["annual_salary_max_usd"]) - float(role["annual_salary_min_usd"])),
                        ),
                    ),
                    4,
                ),
            }
        )

    return pd.DataFrame(rows)


def generate_benefit_plans() -> pd.DataFrame:
    return pd.DataFrame(BENEFIT_PLAN_SPECS)


def generate_benefit_enrollments(
    employees: pd.DataFrame,
    benefit_plans: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    plan_rows = benefit_plans.to_dict("records")
    medical_plan_ids = [plan["benefit_plan_id"] for plan in plan_rows if plan["plan_type"] == "medical"]
    fixed_plan_ids = [plan["benefit_plan_id"] for plan in plan_rows if plan["plan_type"] != "medical"]
    plan_lookup = benefit_plans.set_index("benefit_plan_id").to_dict("index")
    counter = 1

    for employee in employees.sort_values("employee_id").to_dict("records"):
        enrolled_plan_ids = [str(rng.choice(medical_plan_ids))] + fixed_plan_ids
        for plan_id in enrolled_plan_ids:
            plan = plan_lookup[plan_id]
            coverage_tier = "employee_only"
            if plan["plan_type"] in {"medical", "dental"}:
                coverage_tier = str(rng.choice(["employee_only", "employee_spouse", "family"], p=[0.54, 0.2, 0.26]))
            multiplier = {"employee_only": 1.0, "employee_spouse": 1.7, "family": 2.45}[coverage_tier]
            employee_cost = 0.0
            if plan["plan_type"] in {"medical", "dental", "vision"}:
                employee_cost = round(float(plan["employer_monthly_cost_usd"]) * multiplier * float(rng.uniform(0.22, 0.36)), 2)
            elif plan["plan_type"] == "retirement":
                employee_cost = round(float(rng.choice([0.03, 0.04, 0.05, 0.06])), 2)

            rows.append(
                {
                    "benefit_enrollment_id": f"BENENR-{counter:07d}",
                    "employee_id": employee["employee_id"],
                    "benefit_plan_id": plan_id,
                    "coverage_tier": coverage_tier,
                    "enrollment_status": "active" if employee["employment_status"] == "Active" else "inactive",
                    "effective_date": pd.Timestamp(employee["hire_date"]) + pd.Timedelta(days=30),
                    "employee_monthly_contribution_usd": employee_cost,
                }
            )
            counter += 1

    return pd.DataFrame(rows)


def generate_time_off_requests(
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
    rows: list[dict[str, object]] = []
    counter = 1

    for employee in employees.sort_values("employee_id").to_dict("records"):
        request_count = int(rng.poisson(1.6 * max(0.85, scale)))
        if rng.random() < 0.28:
            request_count += 1
        for _ in range(min(request_count, 5)):
            period = monthly_periods.iloc[int(rng.integers(0, len(monthly_periods)))]
            pressure = pressure_lookup.get((employee["branch_id"], period["period_id"]), 0)
            request_type = str(rng.choice(["vacation", "sick", "personal", "bereavement", "jury_duty"], p=[0.47, 0.29, 0.18, 0.03, 0.03]))
            duration_days = int(rng.choice([1, 1, 2, 3, 5], p=[0.34, 0.24, 0.22, 0.13, 0.07]))
            start_date = pd.Timestamp(period["start_date"]) + pd.Timedelta(days=int(rng.integers(0, 23)))
            status_weights = np.array([0.78, 0.12, 0.1], dtype=float)
            if pressure >= 2 and request_type == "vacation":
                status_weights = np.array([0.62, 0.25, 0.13], dtype=float)
            status = str(rng.choice(["approved", "denied", "withdrawn"], p=status_weights / status_weights.sum()))
            rows.append(
                {
                    "time_off_request_id": f"TO-{counter:07d}",
                    "employee_id": employee["employee_id"],
                    "manager_id": employee["manager_id"],
                    "branch_id": employee["branch_id"],
                    "period_id": period["period_id"],
                    "request_type": request_type,
                    "request_status": status,
                    "requested_start_date": start_date,
                    "requested_end_date": start_date + pd.Timedelta(days=duration_days - 1),
                    "requested_hours": round(duration_days * 8.0 * (0.55 if employee["employment_type"] == "Part-time" else 1.0), 2),
                    "submitted_ts": start_date - pd.Timedelta(days=int(rng.integers(7, 45)), hours=int(rng.integers(1, 8))),
                }
            )
            counter += 1

    return pd.DataFrame(rows)


def generate_performance_reviews(
    employees: pd.DataFrame,
    periods: pd.DataFrame,
    payroll_runs: pd.DataFrame,
    branch_incidents: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    quarter_periods = periods[periods["period_type"] == "quarter"].sort_values("start_date").tail(4).reset_index(drop=True)
    bonus_by_employee = payroll_runs.groupby("employee_id", as_index=False)["bonus_pay_usd"].mean()
    bonus_lookup = bonus_by_employee.set_index("employee_id")["bonus_pay_usd"].to_dict()
    severity_score = branch_incidents.assign(severity_score=branch_incidents["severity"].map(SEVERITY_WEIGHTS))
    pressure_lookup = severity_score.groupby("branch_id")["severity_score"].mean().to_dict()
    rows: list[dict[str, object]] = []
    counter = 1

    for employee in employees.sort_values("employee_id").to_dict("records"):
        if pd.Timestamp(employee["hire_date"]) > pd.Timestamp(quarter_periods.iloc[-1]["end_date"]):
            continue
        review_periods = quarter_periods.tail(2 if rng.random() < 0.4 else 1)
        for period in review_periods.to_dict("records"):
            bonus_signal = min(1.0, float(bonus_lookup.get(str(employee["employee_id"]), 0.0)) / 900.0)
            pressure_penalty = min(0.45, float(pressure_lookup.get(str(employee["branch_id"]), 0.0)) / 12.0)
            rating_raw = 3.15 + bonus_signal - pressure_penalty + float(rng.normal(0.0, 0.45))
            rating = int(min(5, max(1, round(rating_raw))))
            rows.append(
                {
                    "review_id": f"REV-{counter:07d}",
                    "employee_id": employee["employee_id"],
                    "manager_id": employee["manager_id"],
                    "branch_id": employee["branch_id"],
                    "review_period_id": period["period_id"],
                    "performance_rating": rating,
                    "potential_rating": int(min(5, max(1, rating + int(rng.choice([-1, 0, 0, 1]))))),
                    "goals_met_pct": round(float(min(1.25, max(0.55, rng.normal(0.86 + (rating - 3) * 0.08, 0.09)))), 4),
                    "review_status": str(rng.choice(["completed", "calibrated", "pending_acknowledgement"], p=[0.78, 0.16, 0.06])),
                }
            )
            counter += 1

    return pd.DataFrame(rows)


def generate_onboarding_cases(
    employees: pd.DataFrame,
    periods: pd.DataFrame,
    rng: np.random.Generator,
    scale: float,
) -> pd.DataFrame:
    monthly_periods = periods[periods["period_type"] == "month"].sort_values("start_date")
    period_lookup = [
        (pd.Timestamp(row["start_date"]), pd.Timestamp(row["end_date"]), row["period_id"])
        for row in monthly_periods.to_dict("records")
    ]
    hr_partners = employees[employees["department"] == "HR"]["employee_id"].tolist()
    if not hr_partners:
        hr_partners = employees[employees["role_title"] == "Branch Manager"]["employee_id"].tolist()

    rows: list[dict[str, object]] = []
    counter = 1
    recent_cutoff = pd.Timestamp(date.today()) - pd.Timedelta(days=900)
    for employee in employees.sort_values("hire_date").to_dict("records"):
        hire_date = pd.Timestamp(employee["hire_date"])
        if hire_date < recent_cutoff and rng.random() > min(0.35, 0.2 * scale):
            continue
        target_period = _period_id_for_date(hire_date, period_lookup)
        completion_pct = round(float(rng.uniform(0.88, 1.0)), 4)
        status = "complete"
        if hire_date > pd.Timestamp(date.today()) - pd.Timedelta(days=75):
            status = str(rng.choice(["in_progress", "blocked", "complete"], p=[0.48, 0.08, 0.44]))
            completion_pct = round(float(rng.uniform(0.35, 0.92)), 4)
        rows.append(
            {
                "onboarding_case_id": f"ONB-{counter:07d}",
                "employee_id": employee["employee_id"],
                "branch_id": employee["branch_id"],
                "period_id": target_period,
                "hr_partner_employee_id": hr_partners[(counter - 1) % len(hr_partners)],
                "manager_id": employee["manager_id"],
                "case_status": status,
                "case_opened_date": hire_date - pd.Timedelta(days=int(rng.integers(10, 24))),
                "target_completion_date": hire_date + pd.Timedelta(days=30),
                "actual_completion_date": hire_date + pd.Timedelta(days=int(rng.integers(12, 46))) if status == "complete" else pd.NaT,
                "completion_pct": completion_pct,
            }
        )
        counter += 1

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


def _cost_center_id(branch_id: object, department_id: object) -> str:
    return f"CC-{str(branch_id).split('-')[-1]}-{str(department_id).split('-')[-1]}"


def _period_id_for_date(target_date: pd.Timestamp, period_lookup: list[tuple[pd.Timestamp, pd.Timestamp, str]]) -> str:
    for start_date, end_date, period_id in period_lookup:
        if start_date <= target_date <= end_date:
            return str(period_id)
    nearest = min(period_lookup, key=lambda row: abs((row[0] - target_date).days))
    return str(nearest[2])
