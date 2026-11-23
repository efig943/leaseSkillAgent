#!/usr/bin/env python3
import json
import re
import subprocess
import sys

SOURCE_DOC_ID = "1k7bN5RUz1z__B7TRsWooZrg-AKf6G0cHGbNNleO-9xM"
CONFIG_FILE = "template_config.json"

def run_cmd(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\nError: {result.stderr}")
    return result.stdout.strip()

def setup_template(existing_doc_id=None):
    if existing_doc_id:
        template_id = existing_doc_id
        print(f"Using existing template copy: {template_id}")
    else:
        print("Copying source document to create Residential Lease Master Template...")
        output = run_cmd(["gdocs", "mutate", "copy", SOURCE_DOC_ID, "Residential Lease Master Template"])
        match = re.search(r"\(ID:\s*([a-zA-Z0-9_-]+)\)", output)
        if not match:
            raise RuntimeError(f"Failed to parse new document ID from output: {output}")
        template_id = match.group(1)
        print(f"Created template copy with ID: {template_id}")

        replacements = [
            ("Maria Versaci", "{{TENANT_NAME}}"),
            ("7/1/2026", "{{START_DATE}}"),
            ("6/30/2027", "{{END_DATE}}"),
            ("$800.00", "{{SECURITY_DEPOSIT}}"),
            ("$800", "{{RENT_AMOUNT}}"),
            ("making sure the robot sweeper is clean and empty every week, as well as once a month mop the floors. Be careful since the floors are wood.", "{{HOUSEHOLD_CHORE}}")
        ]

        for old_val, new_val in replacements:
            print(f"Replacing '{old_val}' with '{new_val}'...")
            run_cmd(["gdocs", "mutate", "replace", template_id, old_val, new_val])

    # Verify template
    print("Verifying template contents...")
    raw_read = run_cmd(["gdocs", "readonly", "read", template_id])
    read_text = raw_read.replace(r"\_", "_")

    name_matches = read_text.count("{{TENANT_NAME}}")
    print(f"Occurrences of {{{{TENANT_NAME}}}}: {name_matches}")
    assert name_matches == 8, f"Expected 8 occurrences of {{{{TENANT_NAME}}}}, found {name_matches}"
    assert "Maria Versaci" not in read_text, "Original tenant name still present!"
    assert "{{START_DATE}}" in read_text, "START_DATE placeholder missing"
    assert "{{END_DATE}}" in read_text, "END_DATE placeholder missing"
    assert "{{RENT_AMOUNT}}" in read_text, "RENT_AMOUNT placeholder missing"
    assert "{{SECURITY_DEPOSIT}}" in read_text, "SECURITY_DEPOSIT placeholder missing"
    assert "{{HOUSEHOLD_CHORE}}" in read_text, "HOUSEHOLD_CHORE placeholder missing"

    config = {
        "template_doc_id": template_id,
        "source_doc_id": SOURCE_DOC_ID,
        "template_title": "Residential Lease Master Template",
        "placeholders": [
            "TENANT_NAME",
            "START_DATE",
            "END_DATE",
            "RENT_AMOUNT",
            "SECURITY_DEPOSIT",
            "HOUSEHOLD_CHORE"
        ]
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Saved configuration to {CONFIG_FILE}")
    return template_id

if __name__ == "__main__":
    existing_id = "1qr-5EWMLP_dHGzzLvSsh8bV1z2fsyjN026aHwsrOSS8" if len(sys.argv) == 1 else sys.argv[1]
    setup_template(existing_id)
