"""Milestone-focused synthetic generators for the Meridian Trust Tier A slice."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import calendar
import json
import math
from pathlib import Path
import re
import sqlite3

import numpy as np
import pandas as pd


FOOTPRINT_STATES = ("NC", "SC", "GA", "FL")
BANK_DOMAIN = "meridiantrust.bank"

BRANCH_SPECS = [
    {
        "branch_id": "BR-001",
        "branch_name": "Charlotte Uptown",
        "region_name": "Carolinas",
        "state_code": "NC",
        "market_name": "Charlotte",
    },
    {
        "branch_id": "BR-002",
        "branch_name": "Raleigh North Hills",
        "region_name": "Carolinas",
        "state_code": "NC",
        "market_name": "Raleigh",
    },
    {
        "branch_id": "BR-003",
        "branch_name": "Asheville River Arts",
        "region_name": "Carolinas",
        "state_code": "NC",
        "market_name": "Asheville",
    },
    {
        "branch_id": "BR-004",
        "branch_name": "Columbia Vista",
        "region_name": "Carolinas",
        "state_code": "SC",
        "market_name": "Columbia",
    },
    {
        "branch_id": "BR-005",
        "branch_name": "Greenville Eastside",
        "region_name": "Carolinas",
        "state_code": "SC",
        "market_name": "Greenville",
    },
    {
        "branch_id": "BR-006",
        "branch_name": "Charleston Harbor",
        "region_name": "Carolinas",
        "state_code": "SC",
        "market_name": "Charleston",
    },
    {
        "branch_id": "BR-007",
        "branch_name": "Atlanta Midtown",
        "region_name": "Georgia",
        "state_code": "GA",
        "market_name": "Atlanta",
    },
    {
        "branch_id": "BR-008",
        "branch_name": "Savannah Historic",
        "region_name": "Georgia",
        "state_code": "GA",
        "market_name": "Savannah",
    },
    {
        "branch_id": "BR-009",
        "branch_name": "Macon Riverside",
        "region_name": "Georgia",
        "state_code": "GA",
        "market_name": "Macon",
    },
    {
        "branch_id": "BR-010",
        "branch_name": "Jacksonville Southpoint",
        "region_name": "Florida",
        "state_code": "FL",
        "market_name": "Jacksonville",
    },
    {
        "branch_id": "BR-011",
        "branch_name": "Orlando Lake Nona",
        "region_name": "Florida",
        "state_code": "FL",
        "market_name": "Orlando",
    },
    {
        "branch_id": "BR-012",
        "branch_name": "Tampa Channelside",
        "region_name": "Florida",
        "state_code": "FL",
        "market_name": "Tampa",
    },
]

PRODUCT_SPECS = [
    {
        "product_id": "PRD-001",
        "product_name": "Meridian Everyday Checking",
        "product_family": "retail checking",
        "product_group": "deposits",
    },
    {
        "product_id": "PRD-002",
        "product_name": "Meridian High-Yield Savings",
        "product_family": "high-yield savings",
        "product_group": "deposits",
    },
    {
        "product_id": "PRD-003",
        "product_name": "Meridian Business Advantage Checking",
        "product_family": "small-business checking",
        "product_group": "deposits",
    },
    {
        "product_id": "PRD-004",
        "product_name": "Meridian Rewards Card",
        "product_family": "consumer credit card",
        "product_group": "cards",
    },
    {
        "product_id": "PRD-005",
        "product_name": "Meridian Auto Loan",
        "product_family": "auto loan",
        "product_group": "lending",
    },
    {
        "product_id": "PRD-006",
        "product_name": "Meridian Personal Loan",
        "product_family": "personal loan",
        "product_group": "lending",
    },
]

CHANNEL_SPECS = [
    {
        "channel_id": "CH-001",
        "channel_name": "Branch Network",
        "channel_type": "customer",
        "business_owner": "Retail Banking",
    },
    {
        "channel_id": "CH-002",
        "channel_name": "Online Banking",
        "channel_type": "digital",
        "business_owner": "Digital Banking",
    },
    {
        "channel_id": "CH-003",
        "channel_name": "Mobile App",
        "channel_type": "digital",
        "business_owner": "Digital Banking",
    },
    {
        "channel_id": "CH-004",
        "channel_name": "Email",
        "channel_type": "campaign",
        "business_owner": "Marketing",
    },
    {
        "channel_id": "CH-005",
        "channel_name": "SMS",
        "channel_type": "campaign",
        "business_owner": "Marketing",
    },
    {
        "channel_id": "CH-006",
        "channel_name": "Call Center",
        "channel_type": "service",
        "business_owner": "Service Recovery",
    },
    {
        "channel_id": "CH-007",
        "channel_name": "Operations Bridge",
        "channel_type": "internal",
        "business_owner": "Operations",
    },
    {
        "channel_id": "CH-008",
        "channel_name": "Incident Hotline",
        "channel_type": "internal",
        "business_owner": "Operations",
    },
]

CUSTOMER_PRODUCT_WEIGHTS = np.array([0.29, 0.18, 0.14, 0.16, 0.11, 0.12], dtype=float)
CUSTOMER_PRODUCT_WEIGHTS = CUSTOMER_PRODUCT_WEIGHTS / CUSTOMER_PRODUCT_WEIGHTS.sum()

FEE_BASE_AMOUNTS = {
    "retail checking": 5_200.0,
    "high-yield savings": 2_150.0,
    "small-business checking": 7_800.0,
    "consumer credit card": 9_400.0,
    "auto loan": 6_300.0,
    "personal loan": 5_900.0,
}

FEE_TYPES = {
    "retail checking": "maintenance_fee",
    "high-yield savings": "service_fee",
    "small-business checking": "treasury_service_fee",
    "consumer credit card": "interchange_fee",
    "auto loan": "servicing_fee",
    "personal loan": "origination_fee",
}

CAMPAIGN_CHANNELS = {
    "deposits": ["Email", "SMS", "Online Banking"],
    "cards": ["Email", "Mobile App", "SMS"],
    "lending": ["Email", "Mobile App", "Branch Network"],
}

CAMPAIGN_THEMES = {
    "retail checking": ["Checking Refresh", "Everyday Banking Bonus", "Switch and Save"],
    "high-yield savings": ["Savings Lift", "Summer Savings Boost", "Reserve Growth"],
    "small-business checking": ["Business Cashflow Drive", "Business Momentum", "Owner Advantage"],
    "consumer credit card": ["Rewards Launch", "Tap to Earn", "Everyday Spend Bonus"],
    "auto loan": ["Drive Forward", "Dealer Fast Track", "Refi Ready"],
    "personal loan": ["Flex Credit", "Personal Loan Reset", "Seasonal Cash Support"],
}


@dataclass(frozen=True)
class GeneratedTable:
    canonical_name: str
    schema_name: str
    table_name: str
    dataframe: pd.DataFrame

    @property
    def local_name(self) -> str:
        return f"{self.schema_name}.{self.table_name}"

    @property
    def sqlite_name(self) -> str:
        return f"{self.schema_name}__{self.table_name}"


def default_users_pool_path() -> Path:
    return Path(__file__).resolve().parents[2] / "users_pool.json"


def build_tier_a(
    seed: int,
    scale: float = 1.0,
    users_pool_path: str | Path | None = None,
) -> list[GeneratedTable]:
    if scale <= 0:
        raise ValueError("scale must be greater than zero")

    rng = np.random.default_rng(seed)
    people_pool = _load_people_pool(Path(users_pool_path) if users_pool_path else default_users_pool_path())

    periods = generate_calendar_periods()
    branches = pd.DataFrame(BRANCH_SPECS)
    products = pd.DataFrame(PRODUCT_SPECS)
    channels = pd.DataFrame(CHANNEL_SPECS)
    employees = generate_employees(people_pool, branches, rng, scale)
    customers = generate_customers(people_pool, branches, products, rng, scale, set(employees["source_key"]))
    accounts = generate_accounts(customers, products, rng)
    fee_revenue = generate_fee_revenue(branches, products, periods, rng)
    employee_directory = generate_employee_directory(employees)
    campaigns = generate_campaigns(products, periods, employees, rng, scale)

    employees_output = employees[
        [
            "employee_id",
            "employee_name",
            "branch_id",
            "department",
            "manager_id",
            "hire_date",
            "employment_type",
            "email",
        ]
    ].copy()

    customers_output = customers[
        [
            "customer_id",
            "customer_name",
            "branch_id",
            "product_id",
            "signup_date",
            "segment",
            "state_code",
        ]
    ].copy()

    return [
        GeneratedTable("main.certified.calendar_periods", "certified", "calendar_periods", periods),
        GeneratedTable("main.certified.branches", "certified", "branches", branches),
        GeneratedTable("main.certified.products", "certified", "products", products),
        GeneratedTable("main.certified.channels", "certified", "channels", channels),
        GeneratedTable("main.certified.employees", "certified", "employees", employees_output),
        GeneratedTable("main.certified.customers", "certified", "customers", customers_output),
        GeneratedTable("main.certified.accounts", "certified", "accounts", accounts),
        GeneratedTable("main.finance_core.fee_revenue", "finance_core", "fee_revenue", fee_revenue),
        GeneratedTable("main.hr_people.employee_directory", "hr_people", "employee_directory", employee_directory),
        GeneratedTable("main.marketing_campaigns.campaigns", "marketing_campaigns", "campaigns", campaigns),
    ]


def generate_calendar_periods() -> pd.DataFrame:
    current_year = date.today().year
    rows: list[dict[str, object]] = []

    for year in (current_year - 1, current_year):
        for month in range(1, 13):
            start_date = date(year, month, 1)
            end_date = date(year, month, calendar.monthrange(year, month)[1])
            rows.append(
                {
                    "period_id": f"{year}-M{month:02d}",
                    "period_type": "month",
                    "start_date": start_date,
                    "end_date": end_date,
                    "fiscal_year": year,
                }
            )

        for quarter in range(1, 5):
            start_month = ((quarter - 1) * 3) + 1
            end_month = start_month + 2
            start_date = date(year, start_month, 1)
            end_date = date(year, end_month, calendar.monthrange(year, end_month)[1])
            rows.append(
                {
                    "period_id": f"{year}-Q{quarter}",
                    "period_type": "quarter",
                    "start_date": start_date,
                    "end_date": end_date,
                    "fiscal_year": year,
                }
            )

    periods = pd.DataFrame(rows).sort_values(["start_date", "period_type", "period_id"]).reset_index(drop=True)
    periods["start_date"] = pd.to_datetime(periods["start_date"])
    periods["end_date"] = pd.to_datetime(periods["end_date"])
    return periods


def generate_employees(
    people_pool: pd.DataFrame,
    branches: pd.DataFrame,
    rng: np.random.Generator,
    scale: float,
) -> pd.DataFrame:
    branch_staff_target = max(5, int(round(6 * scale)))
    selected_people = _take_people(people_pool, len(branches) * branch_staff_target, rng, set())
    rows: list[dict[str, object]] = []
    counter = 1
    pool_rows = selected_people.to_dict("records")
    current_date = date.today()

    for branch_index, branch in enumerate(branches.to_dict("records")):
        branch_manager_id: str | None = None
        for role_index, role in enumerate(_branch_role_blueprint(branch_index, branch_staff_target)):
            person = pool_rows[(branch_index * branch_staff_target) + role_index]
            employee_id = f"EMP-{counter:06d}"
            employee_name = f"{person['first_name']} {person['last_name']}"

            if role_index == 0:
                branch_manager_id = employee_id

            rows.append(
                {
                    "employee_id": employee_id,
                    "employee_name": employee_name,
                    "branch_id": branch["branch_id"],
                    "department": role["department"],
                    "manager_id": None if role_index == 0 else branch_manager_id,
                    "hire_date": _random_date(rng, date(current_date.year - 8, 1, 1), date(current_date.year - 1, 12, 31)),
                    "employment_type": role["employment_type"],
                    "email": _bank_email(person["first_name"], person["last_name"], employee_id),
                    "role_title": role["role_title"],
                    "employment_status": "Active",
                    "source_key": person["source_key"],
                }
            )
            counter += 1

    employees = pd.DataFrame(rows)
    employees["hire_date"] = pd.to_datetime(employees["hire_date"])
    return employees


def generate_customers(
    people_pool: pd.DataFrame,
    branches: pd.DataFrame,
    products: pd.DataFrame,
    rng: np.random.Generator,
    scale: float,
    used_keys: set[str],
) -> pd.DataFrame:
    customer_count = max(240, int(round(360 * scale)))
    selected_people = _take_people(people_pool, customer_count, rng, used_keys)
    products_lookup = {row["product_id"]: row for row in products.to_dict("records")}
    product_ids = np.array(list(products_lookup))
    branches_by_state = {
        state: group.to_dict("records") for state, group in branches.groupby("state_code", sort=False)
    }
    all_branches = branches.to_dict("records")
    start_window = date(date.today().year - 2, 1, 1)
    end_window = date(date.today().year, 9, 30)
    rows: list[dict[str, object]] = []

    for index, person in enumerate(selected_people.to_dict("records"), start=1):
        branch_candidates = branches_by_state.get(person["state_code"], all_branches)
        branch = branch_candidates[int(rng.integers(0, len(branch_candidates)))]
        product_id = str(rng.choice(product_ids, p=CUSTOMER_PRODUCT_WEIGHTS))
        product = products_lookup[product_id]

        rows.append(
            {
                "customer_id": f"CUST-{index:06d}",
                "customer_name": f"{person['first_name']} {person['last_name']}",
                "branch_id": branch["branch_id"],
                "product_id": product_id,
                "signup_date": _random_date(rng, start_window, end_window),
                "segment": _segment_for_product(product["product_family"], rng),
                "state_code": branch["state_code"],
            }
        )

    customers = pd.DataFrame(rows)
    customers["signup_date"] = pd.to_datetime(customers["signup_date"])
    return customers


def generate_accounts(
    customers: pd.DataFrame,
    products: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    products_lookup = products.set_index("product_id")[["product_family", "product_group"]].to_dict("index")
    rows: list[dict[str, object]] = []

    for index, customer in enumerate(customers.to_dict("records"), start=1):
        product = products_lookup[customer["product_id"]]
        rows.append(
            {
                "account_id": f"ACCT-{index:06d}",
                "customer_id": customer["customer_id"],
                "branch_id": customer["branch_id"],
                "product_id": customer["product_id"],
                "account_open_date": customer["signup_date"] + pd.to_timedelta(int(rng.integers(0, 15)), unit="D"),
                "account_status": _account_status_for_group(product["product_group"], rng),
                "current_balance_usd": _balance_for_product(product["product_family"], rng),
            }
        )

    accounts = pd.DataFrame(rows)
    accounts["account_open_date"] = pd.to_datetime(accounts["account_open_date"])
    return accounts


def generate_fee_revenue(
    branches: pd.DataFrame,
    products: pd.DataFrame,
    periods: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    monthly_periods = periods[periods["period_type"] == "month"].reset_index(drop=True)
    branch_multiplier = {
        branch["branch_id"]: 0.92 + (index * 0.035)
        for index, branch in enumerate(branches.to_dict("records"))
    }
    rows: list[dict[str, object]] = []
    min_year = int(monthly_periods["fiscal_year"].min())

    for branch in branches.to_dict("records"):
        for product in products.to_dict("records"):
            base_amount = FEE_BASE_AMOUNTS[product["product_family"]]
            fee_type = FEE_TYPES[product["product_family"]]
            for period in monthly_periods.to_dict("records"):
                month_number = int(str(period["period_id"]).split("M")[-1])
                seasonality = 1.0 + (0.08 * math.sin((month_number / 12.0) * 2.0 * math.pi))
                trend = 1.0 + (0.04 * (int(period["fiscal_year"]) - min_year))
                noise = 1.0 + float(rng.normal(0.0, 0.05))
                amount = max(250.0, round(base_amount * branch_multiplier[branch["branch_id"]] * seasonality * trend * noise, 2))
                rows.append(
                    {
                        "branch_id": branch["branch_id"],
                        "product_id": product["product_id"],
                        "period_id": period["period_id"],
                        "fee_type": fee_type,
                        "fee_amount_usd": amount,
                    }
                )

    return pd.DataFrame(rows)


def generate_employee_directory(employees: pd.DataFrame) -> pd.DataFrame:
    directory = employees[
        ["employee_id", "branch_id", "department", "role_title", "manager_id", "employment_status"]
    ].copy()
    return directory


def generate_campaigns(
    products: pd.DataFrame,
    periods: pd.DataFrame,
    employees: pd.DataFrame,
    rng: np.random.Generator,
    scale: float,
) -> pd.DataFrame:
    launch_periods = periods[periods["period_type"] == "month"].sort_values("start_date").reset_index(drop=True)
    launch_periods = launch_periods.tail(12).reset_index(drop=True)
    product_rows = products.to_dict("records")
    marketing_owners = employees[employees["department"] == "Marketing"]["employee_id"].tolist()
    if not marketing_owners:
        marketing_owners = employees[employees["role_title"] == "Branch Manager"]["employee_id"].tolist()

    campaign_count = max(9, int(round(12 * scale)))
    rows: list[dict[str, object]] = []

    for index in range(campaign_count):
        product = product_rows[index % len(product_rows)]
        period = launch_periods.iloc[index % len(launch_periods)]
        owner_employee_id = marketing_owners[index % len(marketing_owners)]
        channel_name = CAMPAIGN_CHANNELS[product["product_group"]][index % len(CAMPAIGN_CHANNELS[product["product_group"]])]
        theme = CAMPAIGN_THEMES[product["product_family"]][index % len(CAMPAIGN_THEMES[product["product_family"]])]
        budget_base = 65_000.0 if product["product_group"] == "cards" else 48_000.0
        if product["product_group"] == "lending":
            budget_base = 58_000.0

        rows.append(
            {
                "campaign_id": f"CMP-{index + 1:04d}",
                "product_id": product["product_id"],
                "period_id": period["period_id"],
                "campaign_name": f"{_season_label(period['start_date'])} {theme}",
                "campaign_channel": channel_name,
                "budget_usd": round(budget_base * (1.0 + ((index % 4) * 0.08)) * (1.0 + float(rng.normal(0.0, 0.03))), 2),
                "owner_employee_id": owner_employee_id,
            }
        )

    return pd.DataFrame(rows)


def write_sqlite(tables: list[GeneratedTable], output_path: str | Path) -> Path:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        destination.unlink()

    connection = sqlite3.connect(str(destination))

    try:
        manifest_rows: list[dict[str, object]] = []
        for table in tables:
            export_frame = _prepare_frame_for_file_exports(table.dataframe)
            export_frame.to_sql(table.sqlite_name, connection, if_exists="replace", index=False)
            manifest_rows.append(
                {
                    "canonical_name": table.canonical_name,
                    "local_name": table.local_name,
                    "sqlite_name": table.sqlite_name,
                    "row_count": len(table.dataframe),
                }
            )

        pd.DataFrame(manifest_rows).to_sql("generation_manifest", connection, if_exists="replace", index=False)
    finally:
        connection.close()

    return destination


def write_csvs(tables: list[GeneratedTable], output_dir: str | Path) -> Path:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    manifest_rows: list[dict[str, object]] = []
    for table in tables:
        schema_dir = destination / table.schema_name
        schema_dir.mkdir(parents=True, exist_ok=True)

        csv_path = schema_dir / f"{table.table_name}.csv"
        table.dataframe.to_csv(csv_path, index=False)
        manifest_rows.append(
            {
                "canonical_name": table.canonical_name,
                "local_name": table.local_name,
                "row_count": len(table.dataframe),
                "csv_path": str(csv_path.relative_to(destination)),
            }
        )

    manifest = pd.DataFrame(manifest_rows)
    manifest.to_csv(destination / "generation_manifest.csv", index=False)
    return destination


def write_json_schemas(tables: list[GeneratedTable], output_dir: str | Path) -> Path:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    manifest_rows: list[dict[str, object]] = []
    for table in tables:
        schema_dir = destination / table.schema_name
        schema_dir.mkdir(parents=True, exist_ok=True)

        schema_path = schema_dir / f"{table.table_name}.schema.json"
        payload = _build_json_schema_payload(table)
        schema_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        manifest_rows.append(
            {
                "canonical_name": table.canonical_name,
                "local_name": table.local_name,
                "sqlite_name": table.sqlite_name,
                "row_count": len(table.dataframe),
                "schema_path": str(schema_path.relative_to(destination)),
            }
        )

    manifest_path = destination / "generation_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "version": 1,
                "table_count": len(tables),
                "tables": manifest_rows,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return destination


def _load_people_pool(path: Path) -> pd.DataFrame:
    with path.open("r", encoding="utf-8") as handle:
        raw_people = json.load(handle)

    rows = []
    for index, raw_person in enumerate(raw_people):
        address = raw_person.get("address") or {}
        rows.append(
            {
                "source_key": f"POOL-{index:05d}",
                "first_name": str(raw_person.get("first_name") or "Alex").strip(),
                "last_name": str(raw_person.get("last_name") or f"Seed{index}").strip(),
                "state_code": str(address.get("state") or "").upper(),
                "country_code": str(address.get("country") or "").upper(),
            }
        )

    return pd.DataFrame(rows)


def _take_people(
    people_pool: pd.DataFrame,
    count: int,
    rng: np.random.Generator,
    used_keys: set[str],
) -> pd.DataFrame:
    if count <= 0:
        return people_pool.iloc[0:0].copy()

    available = people_pool[~people_pool["source_key"].isin(used_keys)].copy()
    if len(available) < count:
        raise ValueError(f"users_pool.json does not have enough unique rows for {count} requested people")

    southeastern = available[
        (available["country_code"] == "US") & (available["state_code"].isin(FOOTPRINT_STATES))
    ]
    domestic = available[
        (available["country_code"] == "US") & (~available["state_code"].isin(FOOTPRINT_STATES))
    ]
    global_rows = available[available["country_code"] != "US"]

    selections: list[pd.DataFrame] = []
    remaining = count
    for frame in (southeastern, domestic, global_rows):
        if remaining == 0 or frame.empty:
            continue

        take_count = min(remaining, len(frame))
        chosen_index = rng.choice(frame.index.to_numpy(), size=take_count, replace=False)
        chosen = frame.loc[chosen_index]
        selections.append(chosen)
        used_keys.update(chosen["source_key"])
        remaining -= take_count

    selected = pd.concat(selections, ignore_index=True)
    return selected.sample(frac=1.0, random_state=int(rng.integers(0, 2**32 - 1))).reset_index(drop=True)


def _branch_role_blueprint(branch_index: int, branch_staff_target: int) -> list[dict[str, str]]:
    roles = [
        {"department": "Retail Banking", "role_title": "Branch Manager", "employment_type": "Full-time"},
        {"department": "Retail Banking", "role_title": "Relationship Banker", "employment_type": "Full-time"},
        {"department": "Operations", "role_title": "Operations Analyst", "employment_type": "Full-time"},
        {"department": "Operations", "role_title": "Service Lead", "employment_type": "Full-time"},
        {"department": "Retail Banking", "role_title": "Universal Banker", "employment_type": "Part-time"},
    ]

    specialists = [
        {"department": "Marketing", "role_title": "Campaign Manager", "employment_type": "Full-time"},
        {"department": "HR", "role_title": "Payroll Specialist", "employment_type": "Full-time"},
        {"department": "Finance", "role_title": "Finance Analyst", "employment_type": "Full-time"},
        {"department": "Retail Banking", "role_title": "Small Business Banker", "employment_type": "Full-time"},
    ]
    extras = [
        {"department": "Operations", "role_title": "Branch Operations Specialist", "employment_type": "Full-time"},
        {"department": "Retail Banking", "role_title": "Teller", "employment_type": "Part-time"},
        {"department": "Operations", "role_title": "Fraud Resolution Analyst", "employment_type": "Full-time"},
    ]

    if branch_staff_target > len(roles):
        roles.append(specialists[branch_index % len(specialists)])

    while len(roles) < branch_staff_target:
        roles.append(extras[(branch_index + len(roles)) % len(extras)])

    return roles[:branch_staff_target]


def _bank_email(first_name: str, last_name: str, employee_id: str) -> str:
    local_part = f"{_normalize_name_part(first_name)}.{_normalize_name_part(last_name)}"
    local_part = local_part.strip(".") or employee_id.lower().replace("-", "")
    return f"{local_part}.{employee_id[-3:].lower()}@{BANK_DOMAIN}"


def _normalize_name_part(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "", value.lower())
    return normalized or "user"


def _random_date(rng: np.random.Generator, start_date: date, end_date: date) -> date:
    if end_date < start_date:
        raise ValueError("end_date must be on or after start_date")

    day_offset = int(rng.integers(0, (end_date - start_date).days + 1))
    return start_date + timedelta(days=day_offset)


def _segment_for_product(product_family: str, rng: np.random.Generator) -> str:
    if product_family == "small-business checking":
        return "Small Business"
    if product_family == "high-yield savings":
        return str(rng.choice(["Mass Retail", "Mass Affluent"], p=[0.38, 0.62]))
    if product_family in {"auto loan", "personal loan"}:
        return str(rng.choice(["Emerging", "Mass Retail", "Mass Affluent"], p=[0.18, 0.61, 0.21]))
    return str(rng.choice(["Mass Retail", "Affluent", "Growth"], p=[0.58, 0.24, 0.18]))


def _balance_for_product(product_family: str, rng: np.random.Generator) -> float:
    balance_ranges = {
        "retail checking": (350.0, 14_500.0),
        "high-yield savings": (4_000.0, 60_000.0),
        "small-business checking": (3_200.0, 95_000.0),
        "consumer credit card": (250.0, 8_500.0),
        "auto loan": (2_400.0, 31_000.0),
        "personal loan": (1_200.0, 18_500.0),
    }
    lower, upper = balance_ranges[product_family]
    return round(float(rng.uniform(lower, upper)), 2)


def _account_status_for_group(product_group: str, rng: np.random.Generator) -> str:
    if product_group == "lending":
        return str(rng.choice(["Active", "Active", "Active", "Delinquent", "Closed"]))
    if product_group == "cards":
        return str(rng.choice(["Active", "Active", "Active", "Restricted", "Dormant"]))
    return str(rng.choice(["Active", "Active", "Active", "Active", "Dormant"]))


def _season_label(start_date: pd.Timestamp) -> str:
    month = int(pd.Timestamp(start_date).month)
    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Spring"
    if month in (6, 7, 8):
        return "Summer"
    return "Fall"


def _quote_ident(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _qualified_name(schema_name: str, table_name: str) -> str:
    return f"{_quote_ident(schema_name)}.{_quote_ident(table_name)}"


def _prepare_frame_for_file_exports(frame: pd.DataFrame) -> pd.DataFrame:
    export_frame = frame.copy()
    for column_name in export_frame.columns:
        series = export_frame[column_name]
        if pd.api.types.is_datetime64_any_dtype(series):
            if column_name.endswith("_date") or column_name in {"start_date", "end_date", "effective_date"}:
                export_frame[column_name] = series.dt.strftime("%Y-%m-%d")
            else:
                export_frame[column_name] = series.dt.strftime("%Y-%m-%dT%H:%M:%S")
    return export_frame


def _build_json_schema_payload(table: GeneratedTable) -> dict[str, object]:
    properties: dict[str, object] = {}
    required: list[str] = []
    column_descriptors: list[dict[str, object]] = []

    for column_name in table.dataframe.columns:
        series = table.dataframe[column_name]
        column_schema = _json_schema_for_series(column_name, series)
        properties[column_name] = column_schema
        if not bool(series.isna().any()):
            required.append(column_name)
        column_descriptors.append(
            {
                "name": column_name,
                "pandas_dtype": str(series.dtype),
                "nullable": bool(series.isna().any()),
            }
        )

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": table.canonical_name,
        "type": "array",
        "items": {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        },
        "x-canonical-name": table.canonical_name,
        "x-local-name": table.local_name,
        "x-sqlite-name": table.sqlite_name,
        "x-row-count": len(table.dataframe),
        "x-columns": column_descriptors,
    }


def _json_schema_for_series(column_name: str, series: pd.Series) -> dict[str, object]:
    base_schema: dict[str, object]
    if pd.api.types.is_bool_dtype(series):
        base_schema = {"type": "boolean"}
    elif pd.api.types.is_integer_dtype(series):
        base_schema = {"type": "integer"}
    elif pd.api.types.is_float_dtype(series):
        base_schema = {"type": "number"}
    elif pd.api.types.is_datetime64_any_dtype(series):
        schema_format = "date" if column_name.endswith("_date") or column_name in {"start_date", "end_date", "effective_date"} else "date-time"
        base_schema = {"type": "string", "format": schema_format}
    else:
        base_schema = {"type": "string"}

    if bool(series.isna().any()):
        nullable_schema = dict(base_schema)
        nullable_schema["type"] = [base_schema["type"], "null"]
        return nullable_schema
    return base_schema