# tests/test_create_lease.py
import pytest
from scripts.create_lease import validate_lease_args, build_template_vars

def test_validate_lease_args_missing_name():
    with pytest.raises(ValueError, match="tenant_name is required"):
        validate_lease_args("", "7/1/2026", "6/30/2027")

def test_validate_lease_args_defaults():
    args = validate_lease_args("Jane Doe", "7/1/2026", "6/30/2027")
    assert args["tenant_name"] == "Jane Doe"
    assert args["start_date"] == "7/1/2026"
    assert args["end_date"] == "6/30/2027"
    assert args["rent"] == "$800"
    assert args["deposit"] == "$800.00"
    assert "robot sweeper" in args["chore"]

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
    assert "END_DATE=6/30/2027" in vars_list
    assert "RENT_AMOUNT=$800" in vars_list
    assert "SECURITY_DEPOSIT=$800.00" in vars_list
    assert "HOUSEHOLD_CHORE=standard chore" in vars_list
