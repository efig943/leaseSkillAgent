---
name: generate-lease
description: Use when drafting, generating, or creating a new residential lease agreement Google Doc for a tenant (e.g. for 1375 Michelle Ave) using the master lease template.
---

# Generate Lease Agreement

This skill creates a customized California Residential Lease Agreement in Google Docs for a new tenant, using the master template doc derived from the Maria Versaci lease standard.

## Master Template Reference

- **Template Title:** Residential Lease Master Template
- **Template Doc ID:** `1qr-5EWMLP_dHGzzLvSsh8bV1z2fsyjN026aHwsrOSS8`
- **Source Property:** 1375 Michelle Ave., Tracy, CA 95376
- **Landlord:** Ethan Gabriel Figueredo

## Variables & Defaults

| Variable | Description | Default Value | Required? |
|---|---|---|---|
| `tenant_name` | Full legal name of tenant | (None) | **Yes** |
| `start_date` | Commencement Date (`M/D/YYYY` or `YYYY-MM-DD`) | (None) | **Yes** |
| `end_date` | Termination Date (`M/D/YYYY` or `YYYY-MM-DD`) | (None) | **Yes** |
| `rent` | Monthly rent amount | `$800` | Optional |
| `deposit` | Security deposit amount | `$800.00` | Optional |
| `chore` | Assigned household chore | `making sure the robot sweeper is clean and empty every week, as well as once a month mop the floors. Be careful since the floors are wood.` | Optional |

> **Note on House Rules:** Standard rules for 1375 Michelle Ave (Parking: 1 car in driveway; Quiet hours: 10 PM - 7 AM; Smoking: not permitted; Utilities: split with other tenants) are built into the template document.

## Procedure

### 1. Gather Information
Verify that you have the tenant's full name, lease start date, and lease end date.
- If any of these 3 required values are missing from the user's prompt, ask the user to clarify before executing.
- Confirm if custom rent, deposit, or household chore instructions were requested; otherwise, use the defaults above.

### 2. Execute Lease Creation
Run the generator script with the provided parameters (note: do NOT double-quote `$` in bash; pass numbers directly like `--rent 800` or use single quotes):

```bash
python3 scripts/create_lease.py \
  --tenant "Tenant Full Name" \
  --start "8/1/2026" \
  --end "7/31/2027" \
  [--rent 800] \
  [--deposit 800.00] \
  [--chore "Custom chore description"]
```

Alternatively, invoke `gdocs` directly with single quotes around variables containing `$` to prevent shell expansion:

```bash
gdocs mutate create-from-template 1qr-5EWMLP_dHGzzLvSsh8bV1z2fsyjN026aHwsrOSS8 "Tenant Full Name Lease" \
  --var "TENANT_NAME=Tenant Full Name" \
  --var "START_DATE=8/1/2026" \
  --var "END_DATE=7/31/2027" \
  --var 'RENT_AMOUNT=$800' \
  --var 'SECURITY_DEPOSIT=$800.00' \
  --var "HOUSEHOLD_CHORE=making sure the robot sweeper is clean and empty every week, as well as once a month mop the floors. Be careful since the floors are wood."
```

### 3. Verify and Share Link
The command returns the newly created document's ID and web URL.
Present the resulting document clearly to the user with a direct markdown link:

```markdown
Your new lease has been created:
[<Tenant Full Name> Lease](https://docs.google.com/document/d/<DOC_ID>/edit)
```
