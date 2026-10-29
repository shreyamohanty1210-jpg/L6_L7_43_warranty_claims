import pytest
from warranty_claims import out_of_warranty_charge, claim_allowed, sla_status

# Test cases written to execute every line (statement) of warranty_claims.py.


# ---------- out_of_warranty_charge ----------

def test_unknown_plan_raises():
    with pytest.raises(ValueError, match="unknown plan"):
        out_of_warranty_charge("gold", 10, "defect", False)

def test_negative_age_raises():
    with pytest.raises(ValueError, match="invalid age"):
        out_of_warranty_charge("basic", -1, "defect", False)

def test_within_warranty():
    assert out_of_warranty_charge("standard", 20, "defect", False) == 0

def test_registered_basic_defect_small_excess():
    # basic 12 + 6 (registered) = 18 months covered, excess 2 at rate 100
    assert out_of_warranty_charge("basic", 20, "defect", True) == 200

def test_accidental_large_excess():
    # basic 12 months covered, excess 18 > 12 -> rate 200 + 50 + 25 = 275
    assert out_of_warranty_charge("basic", 30, "accidental", False) == 18 * 275


# ---------- claim_allowed ----------

def test_claim_allowed():
    assert claim_allowed(60, 1, False) is True

def test_recall_claim_allowed():
    assert claim_allowed(10, 3, True) is True

def test_claim_too_soon():
    assert claim_allowed(10, 1, False) is False


# ---------- sla_status ----------

def test_sla_hardware_priority_on_track():
    # hardware 48 + priority 24 = 72 hour cutoff
    assert sla_status(100, True, True) == "on_track"

def test_sla_software_at_risk():
    # software cutoff 24, at_risk window is 12..23
    assert sla_status(15, False, False) == "at_risk"

def test_sla_software_critical():
    assert sla_status(5, False, False) == "critical"
