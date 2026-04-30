# Naming Conventions

> Naming patterns for tables, columns, comments, tags, notebooks, dashboards, and Drive docs.
> Used both for authentic gold assets and for deliberately noisy distractors.

## Tables

### Authoritative
- Lowercase snake_case.
- Singular for dimensions (`customer`, `product`), plural for facts (`orders`, `transactions`).
- Live in Tier 1 (`main.certified.*`) or Tier 2 (`main.metric_store.*`).

### Distractor patterns (each maps to a `D.T.*` taxonomy ID — see `validator.md` §2.1)

| Pattern                                | Example                                                        | Taxonomy ID   |
| -------------------------------------- | -------------------------------------------------------------- | ------------- |
| Dated suffix                           | `accounts_oct15`                                               | `D.T.NAME`    |
| Versioned with `_FINAL`                | `accounts_FINAL_v3`                                            | `D.T.NAME`    |
| `_old`                                 | `accounts_old`                                                 | `D.T.NAME`    |
| Materialization backing                | `fct__accounts__a8f3b2c1`                                      | `D.T.NAME`    |
| Wrong catalog                          | `users.jane_doe.accounts`                                      | `D.T.CAT`     |
| Wrong schema                           | `main.tmp.accounts`                                            | `D.T.SCH`     |
| Deprecated                             | comment starts with `**DEPRECATED**`                           | `D.T.WCM`     |
| No comment                             | no `COMMENT ON TABLE`                                          | `D.T.NOC`     |
| Carries `deprecated` / `obsolete` tag  | tag list contains `deprecated`                                 | `D.T.TAG+`    |

## Columns

### Authoritative columns
- Lowercase snake_case.
- Suffix conventions:
  - `*_id` for identifiers
  - `*_date` for dates (DATE type)
  - `*_ts` for timestamps
  - `m_*` for metric columns in `metric_store.*`
  - `dim_*` for dimension columns in `metric_store.*`

### Distractor column patterns
- Abbreviations (`dt`, `cc`, `tot`, `amt`).
- Misleading suffix (`request_date` vs the canonical `provisioned_date`).

## Comments

### Table-comment template (authoritative)

```
# Table: <table_name>
**Owner:** <team>
**Slack Channel:** #<channel>
**Emails:** <list>
**SLA:** <duration>
Source: [<config_path>](<repo_link>)
# Description
<paragraph>
UPDATE <YYYY-MM-DD>: <change-log entry>
```

### Column-comment template (authoritative)

```
Description: <one line>
Examples: <comma-separated examples>
Synonyms: <alternative names the user might use>
Instructions: <directive guidance>
```

### Distractor comment patterns
- Empty comment.
- Generic AI-generated description ("This table contains data about...").
- `Created by file upload UI`.
- `**DEPRECATED** — use <other_table>. Data stopped refreshing <date>.`

## Tags

| Tag           | Meaning                          | Tier   |
| ------------- | -------------------------------- | ------ |
| `certified`   | Gold standard                    | 1      |
| `prod`        | Production-grade                 | 1, 2   |
| `gold`        | Marketing tier                   | 1      |
| `silver`      | Maintained but not gold          | 2      |
| `bronze`      | Raw                              | 3      |
| `deprecated`  | Don't use                        | any    |
| `obsolete`    | Don't use                        | any    |
| `archived`    | Historical only                  | any    |

## Notebooks

| Pattern                                              | Example                                       |
| ---------------------------------------------------- | --------------------------------------------- |
| Authoritative                                        | `/Workspace/Shared/<domain>/<metric>.ipynb`   |
| Half-finished scratch                                | `/Workspace/Users/<person>/scratch_<date>.ipynb` |
| Wrong-query distractor                               | `/Workspace/Shared/<domain>/<metric>_v2.ipynb` |
| Buggy non-authoritative                              | `/Workspace/Users/<person>/<metric>_analysis.ipynb` |
| Points-to-deprecated                                 | `/Workspace/Shared/<domain>/<old_metric>.ipynb` |

## Dashboards

Same trust pattern as notebooks; named `<domain>_<metric>` for gold and `<person>_<thing>` for noise.

## Drive docs

- `/Companies/<domain>/<sub-domain>/<topic>.gdoc`
- Authoritative briefs reference fully-qualified table names.
- Non-authoritative scratch docs may reference table names by short name only.
