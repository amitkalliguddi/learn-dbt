# dbt_ecommerce

> dbt project for transforming raw e-commerce data into
> analytics-ready datasets.

---

## 📊 Project Overview

| Metric | Count |
|---|---:|
| Models | 7 |
| Staging Models | 4 |
| Mart Models | 3 |
| Seeds | 5 |
| Data Tests | 12 |

---

## 🏗️ Architecture

Raw Data → Staging → Marts → Analytics / BI

### Staging

Staging models clean and standardize raw source data.

### Marts

Mart models contain business-ready analytical datasets.

---

## 📦 Staging Models

| Model | Materialization | Description |
|---|---|---|
| `stg_customers` | `default` | — |
| `stg_orders` | `default` | — |
| `stg_payments` | `default` | — |
| `stg_products` | `default` | — |

---

## 📦 Mart Models

| Model | Materialization | Description |
|---|---|---|
| `dim_customers` | `default` | — |
| `dim_products` | `default` | — |
| `fct_orders` | `default` | — |



---

## 🌱 Seeds

| Seed |
|---|
| `order_status_mapping` |
| `raw_customers` |
| `raw_orders` |
| `raw_payments` |
| `raw_products` |

---

## 🧪 Data Quality

This project currently contains:

- **12 data tests**
- **11 tests defined in YAML**
- **1 custom SQL tests**

Tests help validate the quality and reliability of the
transformed datasets.

---

## 📁 Project Structure

- `models/` — dbt transformation models
- `models/staging/` — staging models
- `models/marts/` — analytical models
- `seeds/` — seed data
- `tests/` — custom data quality tests
- `macros/` — reusable SQL macros
- `snapshots/` — historical snapshots
- `analyses/` — analytical SQL
- `dbt_project.yml` — dbt project configuration

---

## 🚀 Running the Project

Build the complete project:

`dbt build`

Run models:

`dbt run`

Run tests:

`dbt test`

Compile the project and generate catalog metadata:

`dbt compile --write-catalog`

---

## 📚 Documentation

Model descriptions and other metadata are maintained in
the project's YAML files.

---

## 🔄 Maintenance

This README is automatically generated from the dbt project.

Do not manually edit generated sections.

---

_Generated automatically on 2026-08-18._
