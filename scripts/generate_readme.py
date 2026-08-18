from pathlib import Path
from datetime import date
import re

ROOT = Path(__file__).resolve().parent.parent

PROJECT_FILE = ROOT / "dbt_project.yml"
MODELS_DIR = ROOT / "models"
SEEDS_DIR = ROOT / "seeds"
TESTS_DIR = ROOT / "tests"
README_FILE = ROOT / "README.md"


def read_file(path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def find_files(directory, extensions):
    if not directory.exists():
        return []

    return [
        path
        for path in directory.rglob("*")
        if path.is_file() and path.suffix in extensions
    ]


# ---------------------------------------------------------
# Project
# ---------------------------------------------------------

def get_project_name():
    content = read_file(PROJECT_FILE)

    match = re.search(
        r"^name:\s*['\"]?([^'\"]+)['\"]?\s*$",
        content,
        re.MULTILINE,
    )

    return match.group(1) if match else "dbt Project"


# ---------------------------------------------------------
# Models
# ---------------------------------------------------------

def get_models():
    return find_files(MODELS_DIR, {".sql"})


def get_model_layer(path):
    try:
        relative = path.relative_to(MODELS_DIR)

        if len(relative.parts) > 1:
            return relative.parts[0]

    except ValueError:
        pass

    return "models"


def get_materialization(path):
    content = read_file(path)

    match = re.search(
        r"materialized\s*=\s*['\"]([^'\"]+)['\"]",
        content,
        re.IGNORECASE,
    )

    return match.group(1) if match else "default"


# ---------------------------------------------------------
# YAML metadata
# ---------------------------------------------------------

def get_yaml_files():
    return find_files(MODELS_DIR, {".yml", ".yaml"})


def get_model_descriptions():
    descriptions = {}

    for yaml_file in get_yaml_files():
        content = read_file(yaml_file)

        matches = re.finditer(
            r"-\s+name:\s*([A-Za-z0-9_]+)(.*?)(?=\n\s*-\s+name:|\Z)",
            content,
            re.DOTALL,
        )

        for match in matches:
            model_name = match.group(1)
            block = match.group(2)

            description_match = re.search(
                r"^\s*description:\s*[\"']?(.*?)[\"']?\s*$",
                block,
                re.MULTILINE,
            )

            if description_match:
                descriptions[model_name] = (
                    description_match.group(1).strip()
                )

    return descriptions


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------

def get_sql_tests():
    """
    Count custom SQL tests stored in the tests/ directory.
    """
    return find_files(TESTS_DIR, {".sql"})


def get_yaml_tests():
    """
    Count dbt tests defined in YAML files.

    This detects common generic tests such as:
      - unique
      - not_null
      - accepted_values
      - relationships

    It also counts custom test names.
    """

    test_count = 0

    test_types = {
        "unique",
        "not_null",
        "accepted_values",
        "relationships",
    }

    for yaml_file in get_yaml_files():
        content = read_file(yaml_file)

        # Find blocks beginning with "tests:"
        test_blocks = re.findall(
            r"(?:tests|data_tests):\s*(.*?)(?=\n\s{0,6}\w|\Z)",
            content,
            re.DOTALL,
        )

        for block in test_blocks:

            # Simple tests:
            #
            # tests:
            #   - unique
            #   - not_null
            #
            simple_tests = re.findall(
                r"^\s*-\s*([A-Za-z_][A-Za-z0-9_]*)\s*$",
                block,
                re.MULTILINE,
            )

            for test_name in simple_tests:
                if test_name in test_types:
                    test_count += 1

            # Configured tests:
            #
            # - accepted_values:
            #     values: [...]
            #
            # - relationships:
            #     to: ref(...)
            #
            configured_tests = re.findall(
                r"^\s*-\s*([A-Za-z_][A-Za-z0-9_]*):\s*$",
                block,
                re.MULTILINE,
            )

            for test_name in configured_tests:
                test_count += 1

    return test_count


def get_total_tests():
    """
    Return total tests detected by the repository.

    This includes:
      - YAML-defined dbt tests
      - Custom SQL tests
    """

    yaml_tests = get_yaml_tests()
    sql_tests = get_sql_tests()

    return yaml_tests + len(sql_tests)


# ---------------------------------------------------------
# Seeds
# ---------------------------------------------------------

def get_seeds():
    return find_files(SEEDS_DIR, {".csv", ".tsv"})


# ---------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------

def generate_model_table(models, descriptions):
    if not models:
        return "_No models found._"

    rows = [
        "| Model | Materialization | Description |",
        "|---|---|---|",
    ]

    for model in sorted(models):
        name = model.stem
        materialization = get_materialization(model)
        description = descriptions.get(name, "—")

        rows.append(
            f"| `{name}` | `{materialization}` | {description} |"
        )

    return "\n".join(rows)


def generate_seed_table(seeds):
    if not seeds:
        return "_No seeds found._"

    rows = [
        "| Seed |",
        "|---|",
    ]

    for seed in sorted(seeds):
        rows.append(f"| `{seed.stem}` |")

    return "\n".join(rows)


# ---------------------------------------------------------
# README
# ---------------------------------------------------------

def generate_readme():

    project_name = get_project_name()

    models = get_models()
    seeds = get_seeds()

    sql_tests = get_sql_tests()
    yaml_tests = get_yaml_tests()

    total_tests = len(sql_tests) + yaml_tests

    descriptions = get_model_descriptions()

    staging_models = [
        model
        for model in models
        if get_model_layer(model) == "staging"
    ]

    mart_models = [
        model
        for model in models
        if get_model_layer(model) == "marts"
    ]

    other_models = [
        model
        for model in models
        if get_model_layer(model)
        not in {"staging", "marts"}
    ]

    generated_date = date.today().isoformat()

    staging_section = generate_model_table(
        staging_models,
        descriptions,
    )

    marts_section = generate_model_table(
        mart_models,
        descriptions,
    )

    seeds_section = generate_seed_table(seeds)

    other_section = ""

    if other_models:
        other_section = (
            "\n## Other Models\n\n"
            + generate_model_table(
                other_models,
                descriptions,
            )
            + "\n"
        )

    readme = f"""
# {project_name}

> dbt project for transforming raw e-commerce data into
> analytics-ready datasets.

---

## 📊 Project Overview

| Metric | Count |
|---|---:|
| Models | {len(models)} |
| Staging Models | {len(staging_models)} |
| Mart Models | {len(mart_models)} |
| Seeds | {len(seeds)} |
| Data Tests | {total_tests} |

---

## 🏗️ Architecture

Raw Data → Staging → Marts → Analytics / BI

### Staging

Staging models clean and standardize raw source data.

### Marts

Mart models contain business-ready analytical datasets.

---

## 📦 Staging Models

{staging_section}

---

## 📦 Mart Models

{marts_section}

{other_section}

---

## 🌱 Seeds

{seeds_section}

---

## 🧪 Data Quality

This project currently contains:

- **{total_tests} data tests**
- **{yaml_tests} tests defined in YAML**
- **{len(sql_tests)} custom SQL tests**

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

_Generated automatically on {generated_date}._
"""

    README_FILE.write_text(
        readme.strip() + "\n",
        encoding="utf-8",
    )

    print(f"README generated successfully: {README_FILE}")
    print(f"Models: {len(models)}")
    print(f"Seeds: {len(seeds)}")
    print(f"YAML tests: {yaml_tests}")
    print(f"SQL tests: {len(sql_tests)}")
    print(f"Total tests: {total_tests}")


if __name__ == "__main__":
    generate_readme()