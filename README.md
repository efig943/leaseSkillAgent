# Lease Skill Agent 📄🏡

An automated agent skill and CLI tool to generate customized residential lease agreements directly in **Google Docs** from your own master lease template. 

It preserves 100% of your original document's typography, page breaks, legal signatures, and formatting while instantly substituting tenant details, lease terms, rent, and deposits.

---

## Features

- 📑 **Native Google Docs Templating:** Uses the Google Docs API to duplicate your master template and substitute `{{KEY}}` variables without any markdown degradation.
- 🤖 **Antigravity Skill Built-in:** Just type *"Draft a lease for [Tenant] from [Start] to [End]"* in Antigravity chat.
- ⚡ **Standalone CLI Runner:** Run via terminal command line with date parsing, currency normalization, and default handling.
- 🔒 **Zero Public Sharing:** All generated documents remain private to your Google account.

---

## Prerequisites

1. **Python 3.8+**
2. **Google Antigravity** installed.
3. **Google Docs Plugin** installed in Antigravity:
   - In Antigravity, add the official Google Docs plugin (`antigravity-plugins-official/plugin/gdocs`).
   - Sign in with your Google account when prompted.

---

## Quick Start (Installation)

1. Clone this repository to your computer:
   ```bash
   git clone https://github.com/efig943/leaseSkillAgent.git
   cd leaseSkillAgent
   ```

2. Open this folder in **Antigravity** (or run `agy` in this directory).

---

## How to Connect Your Own Lease Template

You can easily use your own lease agreement as the master template. Follow these 3 steps:

### Step 1: Prepare Your Master Lease in Google Docs
1. Open your standard lease agreement in Google Docs (or make a copy of your existing lease).
2. Replace tenant-specific values with double curly-brace placeholders:
   - `{{TENANT_NAME}}` – Everywhere the tenant's name appears (title, header, rule acknowledgments, signature blocks).
   - `{{START_DATE}}` – Commencement / Effective date (e.g. `8/1/2026`).
   - `{{END_DATE}}` – Termination date (e.g. `7/31/2027`).
   - `{{RENT_AMOUNT}}` – Monthly rent (e.g. `$1,200`).
   - `{{SECURITY_DEPOSIT}}` – Security deposit (e.g. `$1,200.00`).
   - `{{HOUSEHOLD_CHORE}}` – (Optional) Assigned chore or custom house rule.

> **Tip:** Keep the surrounding underline dashes (`___`) around `{{TENANT_NAME}}` if your document has fill-in-the-blank lines—they will remain aesthetically preserved.

### Step 2: Find Your Google Doc ID
Look at the URL of your master template Google Doc in your browser address bar:
```text
https://docs.google.com/document/d/1qr-5EWMLP_dHGzzLvSsh8bV1z2fsyjN026aHwsrOSS8/edit
                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                  This segment is your DOCUMENT ID
```
Copy that ID string.

### Step 3: Update `template_config.json`
Open `template_config.json` in this project and paste your Document ID:
```json
{
  "template_doc_id": "PASTE_YOUR_DOCUMENT_ID_HERE",
  "template_title": "My Residential Lease Master Template"
}
```

---

## How to Use

### Method 1: Ask Antigravity (Chat Interface)
Simply open the Antigravity chat in this workspace and ask naturally:
> *"Create a new lease for Alex Mercer starting 9/1/2026 and ending 8/31/2027 with $1,200 rent."*

The agent will validate the inputs, invoke the skill, and return the clickable Google Doc link to the newly drafted lease.

### Method 2: Command Line (CLI)
You can run the Python script directly from your terminal:

```bash
# Basic usage with defaults ($800 rent / $800 deposit)
python3 scripts/create_lease.py \
  --tenant "Alex Mercer" \
  --start "9/1/2026" \
  --end "8/31/2027"

# Custom rent and deposit (note: use numbers or single quotes for bash safety)
python3 scripts/create_lease.py \
  --tenant "Sarah Connor" \
  --start "2026-09-01" \
  --end "2027-08-31" \
  --rent 1200 \
  --deposit 1200.00 \
  --chore "maintaining the front lawn and vacuuming common areas"

# Dry run (previews variables without creating a document)
python3 scripts/create_lease.py \
  --tenant "John Doe" \
  --start "8/1/2026" \
  --end "7/31/2027" \
  --dry-run
```

#### CLI Options:
| Flag | Description | Default |
|---|---|---|
| `--tenant` | Full name of tenant (Required) | |
| `--start` | Lease start date (`M/D/YYYY` or `YYYY-MM-DD`) | |
| `--end` | Lease end date (`M/D/YYYY` or `YYYY-MM-DD`) | |
| `--rent` | Monthly rent amount | `$800` |
| `--deposit` | Security deposit amount | `$800.00` |
| `--chore` | Assigned household chore | Standard robot sweeper & mopping |
| `--template` | Custom Google Doc template ID | Uses `template_config.json` |
| `--dry-run` | Prints generated payload without creating doc | |

---

## Project Structure

```text
leaseSkillAgent/
├── .agents/skills/generate-lease/  # Antigravity skill definition & instructions
│   └── SKILL.md
├── scripts/
│   ├── create_lease.py             # CLI runner & parameter validator
│   └── setup_master_template.py    # Setup script to clone and format master doc
├── tests/                          # Unit and integration test suite
│   ├── test_create_lease.py
│   ├── test_skill_format.py
│   └── test_e2e_lease_generation.py
├── template_config.json            # Configuration pointing to the active master template
└── README.md
```

---

## Running Tests

To run the automated test suite:
```bash
pip install pytest pyyaml
PYTHONPATH=. pytest tests/ -v
```

---

## License
MIT
