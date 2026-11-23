# Lease Generation Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create an automated Antigravity skill that creates new residential lease Google Docs from a master template derived from the Maria Versaci lease.

**Architecture:** A one-time setup duplicates the Maria Versaci lease into a clean Google Doc template with `{{KEY}}` placeholders for all variable fields. A Python CLI helper script wraps `gdocs mutate create-from-template` with parameter validation, sane defaults, and error handling. An Antigravity skill (`generate-lease`) documents the workflow for the agent to prompt for tenant details, run the helper, and present the formatted Google Doc link.

**Tech Stack:** Python 3, `gdocs` CLI (`cl/986250228`), Google Drive API, Antigravity Customization System (Skills).

**Spec:** [docs/superpowers/specs/2026-11-22-lease-generation-skill-design.md](../../specs/2026-11-22-lease-generation-skill-design.md)

## Global Constraints
- Target template source document ID: `1k7bN5RUz1z__B7TRsWooZrg-AKf6G0cHGbNNleO-9xM` ("Maria Versaci Lease").
- Must not modify or delete the original Maria Versaci lease document.
- Must substitute all 8 occurrences of tenant name across agreement headers, signatures, and rule acknowledgments.
- Skill must live at `.agents/skills/generate-lease/SKILL.md` with valid YAML frontmatter.
- All documents created must retain default private/owner permissions (no public sharing).

## Review Focus
1. Tenant name appearing with surrounding underscores: verify regex/replacements do not leave orphaned underscores or cut off name boundaries.
2. Missing non-required fields (e.g. chore, parking, payment method): ensure defaults gracefully apply rather than leaving raw `{{KEY}}` tokens in the generated document.
3. Date formatting: ensure dates in different formats (e.g. `2026-08-01` or `8/1/2026`) match the document style.
4. Quoted or special characters in tenant names (e.g., apostrophes, hyphens): ensure CLI escaping does not break `gdocs mutate create-from-template`.
5. Empty response or network error from `gdocs`: helper script catches failures and emits clear error messaging.

---

### Task 1: Create Master Template Google Doc

**Files:**
- Create: `scripts/setup_master_template.py`
- Test: `tests/test_template_setup.py`

**Interfaces:**
- Consumes: Document `1k7bN5RUz1z__B7TRsWooZrg-AKf6G0cHGbNNleO-9xM` via `gdocs` CLI
- Produces: `MASTER_TEMPLATE_DOC_ID` stored in `template_config.json` containing `{{TENANT_NAME}}`, `{{START_DATE}}`, `{{END_DATE}}`, `{{EFFECTIVE_DATE}}`, `{{RENT_AMOUNT}}`, `{{SECURITY_DEPOSIT}}`, `{{PAYMENT_METHOD}}`, `{{HOUSEHOLD_CHORE}}`.

- [ ] **Step 1: Write test for template configuration and substitution detection**

```python
# tests/test_template_setup.py
import json, os

def test_template_config_structure():
    config_path = "template_config.json"
    assert os.path.exists(config_path), "template_config.json must exist"
    with open(config_path) as f:
        config = json.load(f)
    assert "template_doc_id" in config
    assert len(config["template_doc_id"]) > 10
    assert "source_doc_id" in config
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_template_setup.py`
Expected: FAIL with `AssertionError: template_config.json must exist`

- [ ] **Step 3: Implement `scripts/setup_master_template.py`**

Approach:
1. Run `gdocs mutate copy 1k7bN5RUz1z__B7TRsWooZrg-AKf6G0cHGbNNleO-9xM "Residential Lease Master Template" --json` to create the new copy.
2. Extract the new document ID.
3. Perform substitutions using `gdocs mutate sed` or `gdocs mutate replace`:
   - Replace "Maria Versaci" -> `{{TENANT_NAME}}`
   - Replace "7/1/2026" -> `{{START_DATE}}` (and effective date)
   - Replace "6/30/2027" -> `{{END_DATE}}`
   - Replace "$800.00" -> `{{SECURITY_DEPOSIT}}`
   - Replace "$800" -> `{{RENT_AMOUNT}}`
4. Verify document content via `gdocs readonly read <NEW_ID>` to confirm placeholders.
5. Save `{"template_doc_id": "<NEW_ID>", "source_doc_id": "1k7bN5RUz1z__B7TRsWooZrg-AKf6G0cHGbNNleO-9xM"}` to `template_config.json`.

- [ ] **Step 4: Execute `python3 scripts/setup_master_template.py` and run tests**

Run: `python3 scripts/setup_master_template.py && pytest tests/test_template_setup.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add template_config.json scripts/setup_master_template.py tests/test_template_setup.py
git commit -m "feat: setup master lease template document in Google Docs"
```

---

### Task 2: Implement Lease Generation CLI Helper Script

**Files:**
- Create: `scripts/create_lease.py`
- Test: `tests/test_create_lease.py`

**Interfaces:**
- Consumes: `template_config.json` (`template_doc_id`), user parameters
- Produces: `create_lease(tenant_name, start_date, end_date, rent, deposit, chore, dry_run=False) -> dict` returning `{"doc_id": str, "url": str, "title": str}`

- [ ] **Step 1: Write unit tests for `create_lease.py` argument parsing and validation**

```python
# tests/test_create_lease.py
import pytest
from scripts.create_lease import validate_lease_args, build_template_vars

def test_validate_lease_args():
    # Missing required tenant_name should raise ValueError
    with pytest.raises(ValueError, match="tenant_name is required"):
        validate_lease_args("", "7/1/2026", "6/30/2027")
    
    # Defaults applied
    args = validate_lease_args("Jane Doe", "7/1/2026", "6/30/2027")
    assert args["rent"] == "$800"
    assert args["deposit"] == "$800.00"

def test_build_template_vars():
    args = {
        "tenant_name": "Jane Doe",
        "start_date": "7/1/2026",
        "end_date": "6/30/2027",
        "rent": "$800",
        "deposit": "$800.00",
        "chore": "standard chore"
    }
    vars_list = build_template_vars(args)
    assert "TENANT_NAME=Jane Doe" in vars_list
    assert "START_DATE=7/1/2026" in vars_list
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_create_lease.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.create_lease'`

- [ ] **Step 3: Implement `scripts/create_lease.py`**

Functions:
- `validate_lease_args(tenant_name, start_date, end_date, rent=None, deposit=None, chore=None) -> dict`
- `build_template_vars(args: dict) -> list[str]`
- `generate_lease(tenant_name, start_date, end_date, rent=None, deposit=None, chore=None, dry_run=False) -> dict`
- CLI `main()` with `argparse`.

- [ ] **Step 4: Run unit tests to verify they pass**

Run: `pytest tests/test_create_lease.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/create_lease.py tests/test_create_lease.py
git commit -m "feat: implement lease generation script with validation and defaults"
```

---

### Task 3: Author the `generate-lease` Skill

**Files:**
- Create: `.agents/skills/generate-lease/SKILL.md`
- Create: `.agents/skills/generate-lease/scripts/create_lease.py` (or symlink/copy)
- Test: `tests/test_skill_format.py`

**Interfaces:**
- Consumes: `generate_lease` workflow, `template_config.json`
- Produces: Antigravity skill ready for model invocation

- [ ] **Step 1: Write test for skill frontmatter and required sections**

```python
# tests/test_skill_format.py
import os, yaml

def test_skill_frontmatter():
    skill_path = ".agents/skills/generate-lease/SKILL.md"
    assert os.path.exists(skill_path), "SKILL.md must exist"
    with open(skill_path) as f:
        content = f.read()
    assert content.startswith("---"), "Must have YAML frontmatter"
    parts = content.split("---")
    frontmatter = yaml.safe_load(parts[1])
    assert frontmatter["name"] == "generate-lease"
    assert frontmatter["description"].startswith("Use when")
    assert "template" in frontmatter["description"].lower() or "lease" in frontmatter["description"].lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_skill_format.py`
Expected: FAIL with `AssertionError: SKILL.md must exist`

- [ ] **Step 3: Create `.agents/skills/generate-lease/SKILL.md`**

Write comprehensive instructions:
- Trigger conditions ("Use when the user wants to draft, generate, or create a new residential lease agreement for a tenant at 1375 Michelle Ave...").
- Parameters checklist (required: tenant name, lease start date, lease end date; optional: rent, deposit, chores, parking).
- Procedure for gathering missing inputs interactively if not provided.
- CLI invocation instructions.
- Verification and link formatting rules.

- [ ] **Step 4: Run skill format test**

Run: `pytest tests/test_skill_format.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add .agents/skills/generate-lease/ tests/test_skill_format.py
git commit -m "feat: add generate-lease skill definition and documentation"
```

---

### Task 4: End-to-End Live Verification

**Files:**
- Test: `tests/test_e2e_lease_generation.py`

**Interfaces:**
- Consumes: Live `gdocs` CLI and Master Template Doc
- Produces: Verified live Google Doc generation and validation

- [ ] **Step 1: Write E2E verification test**

```python
# tests/test_e2e_lease_generation.py
import subprocess, json
from scripts.create_lease import generate_lease

def test_live_lease_generation_and_content():
    # Generate test lease
    test_tenant = "Test Tenant Alice"
    result = generate_lease(
        tenant_name=test_tenant,
        start_date="8/1/2026",
        end_date="7/31/2027",
        rent="$850",
        deposit="$850.00"
    )
    assert "doc_id" in result
    new_doc_id = result["doc_id"]
    
    # Read back doc content using gdocs
    read_out = subprocess.check_output(["gdocs", "readonly", "read", new_doc_id]).decode("utf-8")
    
    # Assert test tenant appears and no Maria Versaci remains
    assert test_tenant in read_out
    assert "Maria Versaci" not in read_out
    assert "{{TENANT_NAME}}" not in read_out
    assert "$850" in read_out
```

- [ ] **Step 2: Run E2E test to verify end-to-end functionality**

Run: `pytest tests/test_e2e_lease_generation.py -v`
Expected: PASS

- [ ] **Step 3: Commit and clean up test artifact if desired**

```bash
git add tests/test_e2e_lease_generation.py
git commit -m "test: verify end-to-end lease generation and placeholder replacement"
```
