# Design Document: Residential Lease Generation Skill

- **Date:** 2026-11-22
- **Topic:** Lease Generation Skill from Google Docs Template
- **Status:** Draft for Builder Review

---

## 1. Intent and the "Why"
The user manages residential rental properties (specifically the property at 1375 Michelle Ave, Tracy, CA). Writing residential leases manually by duplicating prior documents and editing fields by hand is time-consuming, prone to copy-paste errors (such as missed name replacements or outdated dates), and carries legal risk if prior tenant details are accidentally retained.

The goal is to create an Antigravity skill that automates generating new residential leases in Google Docs for new tenants based on the established lease standard (modeled after the recent "Maria Versaci Lease"), ensuring 100% visual and legal consistency with zero manual search-and-replace friction.

---

## 2. Goals, Non-Goals, and Anti-Goals

### Goals
- Create a permanent, clean **Master Lease Template Google Doc** derived from the "Maria Versaci Lease" (`1k7bN5RUz1z__B7TRsWooZrg-AKf6G0cHGbNNleO-9xM`), with standard variable tags (e.g., `{{TENANT_NAME}}`, `{{START_DATE}}`, `{{END_DATE}}`, `{{RENT_AMOUNT}}`, `{{SECURITY_DEPOSIT}}`, `{{CHORES}}`, etc.).
- Build an Antigravity skill (e.g., `generate-lease` under `.agents/skills/generate-lease/SKILL.md`) that can be invoked whenever a lease needs to be drafted.
- The skill takes lease terms (either supplied upfront or prompted interactively) and calls `gdocs mutate create-from-template` to instantiate a brand new Google Doc titled `[Tenant Name] Lease`.
- Ensure all occurrences of the tenant's name (8 distinct positions in the original agreement including premises clause, rules initial section, and signatures) are accurately populated.
- Output the direct Google Docs edit link to the user immediately upon completion.

### Non-Goals
- E-signature integration (DocuSign, HelloSign) - out of scope for this skill.
- Automated tenant background checking or payment processing.
- Modifying or tampering with past lease documents.

### Anti-Goals
- Never modify or overwrite the original "Maria Versaci Lease" document.
- Never alter the master template document during individual lease generation runs.
- Never make generated lease documents publicly accessible (keep Google Docs sharing restricted to the owner's default permissions).

---

## 3. Constraints
- Must integrate with the installed `gdocs` CLI (`cl/986250228`).
- Must operate within the authenticated Google account (`ethan.figueredo943@gmail.com`).
- Must conform to Antigravity's Skill specification (`SKILL.md` with YAML frontmatter).
- Must preserve the formatting, typography, legal clauses, underlines, and structure of the original agreement.

---

## 4. Approaches Considered

### Approach 1: Master Template Doc with Native Placeholders (Selected)
Duplicate the "Maria Versaci Lease" once into a dedicated "Residential Lease Master Template" Google Doc. Replace tenant-specific values with `{{KEY}}` placeholders. Generate new leases using `gdocs mutate create-from-template TEMPLATE_ID "[Tenant Name] Lease" --var KEY=VALUE`.
- **Pros:** Native Google Docs API support, zero risk of accidental text collision, clean separation between template and instances, 100% styling fidelity.
- **Cons:** Requires a one-time template doc creation step.
- **Verdict:** Selected by user.

### Approach 2: Direct Doc Clone & Surgical Substitution (`gdocs mutate copy` + `sed`)
Keep the original Maria Versaci document as the direct source. Every time a new lease is requested, copy the doc and execute sed substitutions.
- **Pros:** No extra master template doc in Drive.
- **Cons:** Brittle; regex/sed matching on strings like "Maria Versaci" or dates can fail if formatting varies, or unintentionally replace text elsewhere.
- **Verdict:** Rejected in favor of Approach 1.

### Approach 3: Local Markdown Template & Import (`gdocs mutate import-md`)
Maintain a markdown template in git, interpolate variables locally, and import via `gdocs mutate import-md`.
- **Pros:** Code-centric, version-controlled in git.
- **Cons:** Markdown import cannot faithfully replicate complex legal doc layouts, specific underline fill-in blanks, and pagination from Google Docs.
- **Verdict:** Rejected.

---

## 5. Architectural and Operational Design

### 5.1 Template Creation (One-time Setup)
1. Copy the source document `1k7bN5RUz1z__B7TRsWooZrg-AKf6G0cHGbNNleO-9xM` to `Residential Lease Master Template`.
2. Replace variable fields in the new master document with:
   - `{{EFFECTIVE_DATE}}`: e.g. `7/1/2026`
   - `{{TENANT_NAME}}`: All 8 occurrences of tenant name (including signature line, agreement header, and rules acknowledgments).
   - `{{PREMISES_ADDRESS}}`: `1375 Michelle Ave., Tracy, CA, California 95376` (defaultable)
   - `{{COMMENCEMENT_DATE}}`: e.g. `7/1/2026`
   - `{{TERMINATION_DATE}}`: e.g. `6/30/2027`
   - `{{RENT_AMOUNT}}`: e.g. `$800`
   - `{{PAYMENT_METHOD}}`: e.g. `Baseline` (or Zelle, Venmo, etc.)
   - `{{SECURITY_DEPOSIT}}`: e.g. `$800.00`
   - `{{PARKING_TERMS}}`: e.g. `one car in the driveway`
   - `{{HOUSEHOLD_CHORE}}`: e.g. `making sure the robot sweeper is clean and empty every week, as well as once a month mop the floors. Be careful since the floors are wood.`
3. Record the resulting `MASTER_TEMPLATE_DOC_ID` in the skill's reference.

### 5.2 The Skill (`generate-lease`)
- **Location:** `.agents/skills/generate-lease/SKILL.md` (and optional helper script `scripts/create_lease.sh` or `scripts/create_lease.py`).
- **Inputs:**
  - `tenant_name` (Required)
  - `start_date` (Required)
  - `end_date` (Required)
  - `rent_amount` (Required, default: `$800`)
  - `deposit_amount` (Required, default: matches rent)
  - `chore` (Optional, defaults to robot sweeper & monthly mopping)
  - `parking` (Optional, defaults to one car in driveway)
  - `payment_method` (Optional, defaults to Baseline)
- **Workflow:**
  1. Validate provided parameters. If essential parameters are missing, prompt the user.
  2. Invoke `gdocs mutate create-from-template MASTER_TEMPLATE_DOC_ID "[Tenant Name] Lease" --var TENANT_NAME="..." ...`
  3. Retrieve and output the clickable Google Doc URL (`https://docs.google.com/document/d/<NEW_DOC_ID>/edit`).

---

## 6. What is Left to the Builder
- Precise placeholder formatting inside the Master Template (ensuring surrounding underscores/lines remain aesthetically pleasing).
- Helper script implementation (`create_lease.py` or bash wrapper) to handle date formatting and CLI escaping cleanly.
- Test execution with test tenant details to verify that all 8 tenant name positions and all date/dollar positions populate properly.
