#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import sys

DEFAULT_RENT = "$800"
DEFAULT_DEPOSIT = "$800.00"
DEFAULT_CHORE = "making sure the robot sweeper is clean and empty every week, as well as once a month mop the floors. Be careful since the floors are wood."
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "template_config.json")

def load_template_id():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            data = json.load(f)
            return data.get("template_doc_id")
    return "1qr-5EWMLP_dHGzzLvSsh8bV1z2fsyjN026aHwsrOSS8"

def validate_lease_args(tenant_name, start_date, end_date, rent=None, deposit=None, chore=None):
    if not tenant_name or not tenant_name.strip():
        raise ValueError("tenant_name is required")
    if not start_date or not start_date.strip():
        raise ValueError("start_date is required")
    if not end_date or not end_date.strip():
        raise ValueError("end_date is required")

    clean_rent = rent.strip() if rent else DEFAULT_RENT
    if not clean_rent.startswith("$") and clean_rent.replace(".", "").isdigit():
        clean_rent = f"${clean_rent}"

    clean_deposit = deposit.strip() if deposit else DEFAULT_DEPOSIT
    if not clean_deposit.startswith("$") and clean_deposit.replace(".", "").isdigit():
        clean_deposit = f"${clean_deposit}"

    return {
        "tenant_name": tenant_name.strip(),
        "start_date": start_date.strip(),
        "end_date": end_date.strip(),
        "rent": clean_rent,
        "deposit": clean_deposit,
        "chore": chore.strip() if chore else DEFAULT_CHORE
    }

def build_template_vars(args: dict) -> list[str]:
    return [
        f"TENANT_NAME={args['tenant_name']}",
        f"START_DATE={args['start_date']}",
        f"END_DATE={args['end_date']}",
        f"RENT_AMOUNT={args['rent']}",
        f"SECURITY_DEPOSIT={args['deposit']}",
        f"HOUSEHOLD_CHORE={args['chore']}"
    ]

def generate_lease(tenant_name, start_date, end_date, rent=None, deposit=None, chore=None, dry_run=False, template_id=None):
    validated = validate_lease_args(tenant_name, start_date, end_date, rent, deposit, chore)
    t_id = template_id or load_template_id()
    doc_title = f"{validated['tenant_name']} Lease"

    cmd = ["gdocs", "mutate", "create-from-template", t_id, doc_title]
    for var in build_template_vars(validated):
        cmd.extend(["--var", var])

    if dry_run:
        return {
            "dry_run": True,
            "cmd": cmd,
            "title": doc_title,
            "args": validated
        }

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gdocs command failed:\n{result.stderr}\nOutput: {result.stdout}")

    output = result.stdout.strip()
    # Output typically contains:
    # Created document: [Title] (ID: [DOC_ID])
    # Link: https://docs.google.com/document/d/[DOC_ID]/edit
    doc_id = None
    id_match = re.search(r"\(ID:\s*([a-zA-Z0-9_-]+)\)", output)
    if id_match:
        doc_id = id_match.group(1)
    else:
        link_match = re.search(r"/document/d/([a-zA-Z0-9_-]+)/", output)
        if link_match:
            doc_id = link_match.group(1)

    url = f"https://docs.google.com/document/d/{doc_id}/edit" if doc_id else None

    return {
        "doc_id": doc_id,
        "url": url,
        "title": doc_title,
        "raw_output": output
    }

def main():
    parser = argparse.ArgumentParser(description="Generate a residential lease in Google Docs from template")
    parser.add_argument("--tenant", required=True, help="Full name of tenant")
    parser.add_argument("--start", required=True, help="Start date (e.g. 8/1/2026)")
    parser.add_argument("--end", required=True, help="End date (e.g. 7/31/2027)")
    parser.add_argument("--rent", default=DEFAULT_RENT, help=f"Monthly rent (default: {DEFAULT_RENT})")
    parser.add_argument("--deposit", default=DEFAULT_DEPOSIT, help=f"Security deposit (default: {DEFAULT_DEPOSIT})")
    parser.add_argument("--chore", default=DEFAULT_CHORE, help="Household chore assigned to tenant")
    parser.add_argument("--dry-run", action="store_true", help="Print command without creating document")

    args = parser.parse_args()
    try:
        res = generate_lease(
            tenant_name=args.tenant,
            start_date=args.start,
            end_date=args.end,
            rent=args.rent,
            deposit=args.deposit,
            chore=args.chore,
            dry_run=args.dry_run
        )
        if args.dry_run:
            print("Dry run successful:")
            print(json.dumps(res, indent=2))
        else:
            print(f"Successfully created: {res['title']}")
            print(f"Doc ID: {res['doc_id']}")
            print(f"Link: {res['url']}")
    except Exception as e:
        print(f"Error generating lease: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
