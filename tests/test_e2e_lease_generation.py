# tests/test_e2e_lease_generation.py
import subprocess
import pytest
from scripts.create_lease import generate_lease

def test_live_lease_generation_and_content():
    test_tenant = "Test Tenant Alex Mercer"
    result = generate_lease(
        tenant_name=test_tenant,
        start_date="9/1/2026",
        end_date="8/31/2027",
        rent="$850",
        deposit="$850.00"
    )
    assert "doc_id" in result
    new_doc_id = result["doc_id"]
    assert new_doc_id is not None, f"Failed to get doc_id from result: {result}"

    # Read back document content via gdocs
    read_out = subprocess.check_output(["gdocs", "readonly", "read", new_doc_id]).decode("utf-8")
    cleaned = read_out.replace(r"\_", "_")

    # Assert test tenant appears in all expected places
    tenant_occurrences = cleaned.count(test_tenant)
    print(f"Occurrences of {test_tenant}: {tenant_occurrences}")
    assert tenant_occurrences == 8, f"Expected 8 occurrences of tenant name, got {tenant_occurrences}"

    # Assert no remnant placeholder or prior tenant name
    assert "Maria Versaci" not in cleaned
    assert "{{TENANT_NAME}}" not in cleaned
    assert "{{START_DATE}}" not in cleaned
    assert "{{END_DATE}}" not in cleaned
    assert "{{RENT_AMOUNT}}" not in cleaned
    assert "{{SECURITY_DEPOSIT}}" not in cleaned

    # Assert new terms are present
    assert "$850" in cleaned
    assert "$850.00" in cleaned
    assert "9/1/2026" in cleaned
    assert "8/31/2027" in cleaned
