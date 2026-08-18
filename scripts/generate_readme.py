from pathlib import Path
from datetime import date
import re

ROOT = Path(__file__).resolve().parent.parent

PROJECT_FILE = ROOT / "dbt_project.yml"
MODELS_DIR = ROOT / "models"
SEEDS_DIR = ROOT / "seeds"
TESTS_DIR = ROOT / "tests"
README_FILE = ROOT / "README.md"


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

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

        model_matches = re.finditer(
            r"-\s+name:\s*([A-Za-z0-9_]+)(.*?)(?=\n\s*-\s+name:|\Z)",
            content,
            re.DOTALL,
        )

        for match in model_matches:
            model_name = match.group(1)
            block = match.group(2)

            description_match = re.search(
                r"description:\s*[\"']?(.*?)[\"']?\s*$",
                block,
                re.MULTILINE,
            )

            if description_match:
                descriptions[model_name] = (
                    description_match.group(1).strip()
                )

    return descriptions


# ---------------------------------------------------------
# Seeds
# ---------------------------------------------------------

def get_seeds():
    return find_files(SEEDS_DIR, {".csv", ".tsv"})


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------

def get_tests():
    return find_files(TESTS_DIR, {".sql"})


# ---------------------------------------------------------
# Model tables
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

        description = descriptions.get(
            name,
            "—",
        )

        rows.append(
            f"| `{name}` | `{materialization}` | {description} |"
        )

    return "\n".join(rows)


def generate_layer_section(models, layer, descriptions):
    layer_models = [
        model
        for model in models
        if get_model_layer(model) == layer
    ]

    if not layer_models:
        return ""

    table = generate_model_table(
        layer_models,
        descriptions,
    )

    return f"""
### {layer.title()}

{table}
"""


# ---------------------------------------------------------
# Seeds table
# ---------------------------------------------------------

def generate_seed_table(seeds):
    if not seeds:
        return "_No seeds found._"

    rows = [
        "| Seed |",
        "|---|",
    ]

    for seed in sorted(seeds):
        rows.append(
            f"| `{seed.stem}` |"
        )

    return "\n".join(rows)


# ---------------------------------------------------------
# Main README
# ---------------------------------------------------------

def generate_readme():

    project_name = get_project_name()

    models = get_models()
    seeds = get_seeds()
    tests = get_tests()

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

    readme = f"""# {project_name}

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
| SQL Tests | {len(tests)} |

---

## 🏗️ Architecture

```text
Raw Data
   │
   ▼
┌──────────────┐
│   Staging    │
│    Views     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│     Marts    │
│    Tables    │
└──────┬───────┘
       │
       ▼
 Analytics / BI