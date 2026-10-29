import pytest
from warranty_claims import out_of_warranty_charge, claim_allowed, sla_status

# Test cases written so that every decision in warranty_claims.py is
# evaluated both True and False (branch coverage), including boundary values.


# ---------- out_of_warranty_charge ----------

# if plan not in COVERED_MONTHS  -> True / False
def test_unknown_plan_raises():
    with pytest.raises(ValueError, match="unknown plan"):
        out_of_warranty_charge("gold", 10, "defect", False)

def test_known_plan_accepted():
    assert out_of_warranty_charge("basic", 0, "defect", False) == 0

# if age_months < 0  -> True / False
def test_negative_age_raises():
    with pytest.raises(ValueError, match="invalid age"):
        out_of_warranty_charge("basic", -1, "defect", False)

def test_zero_age_is_valid():
    assert out_of_warranty_charge("premium", 0, "accidental", True) == 0

# if is_registered and plan != "premium"
def test_registered_non_premium_gets_extension():
    # standard 24 + 6 = 30 months covered
    assert out_of_warranty_charge("standard", 30, "defect", True) == 0
    assert out_of_warranty_charge("standard", 31, "defect", True) == 100

def test_registered_premium_gets_no_extension():
    # premium stays at 36 months even when registered
    assert out_of_warranty_charge("premium", 37, "defect", True) == 100

def test_unregistered_gets_no_extension():
    assert out_of_warranty_charge("standard", 25, "defect", False) == 100

# if excess <= 0  -> True / False (boundary at excess == 0 and 1)
def test_excess_exactly_zero_is_free():
    assert out_of_warranty_charge("basic", 12, "defect", False) == 0

def test_excess_one_month_is_charged():
    assert out_of_warranty_charge("basic", 13, "defect", False) == 100

# if claim_type == "accidental"  -> True / False
def test_accidental_small_excess_rate():
    assert out_of_warranty_charge("basic", 15, "accidental", False) == 3 * 200

def test_defect_small_excess_rate():
    assert out_of_warranty_charge("basic", 15, "defect", False) == 3 * 100

# if excess > 12  -> True / False (boundary at 12 and 13)
def test_excess_exactly_twelve_no_surcharge():
    assert out_of_warranty_charge("basic", 24, "defect", False) == 12 * 100

def test_excess_thirteen_defect_surcharge():
    # nested if claim_type == "accidental" -> False
    assert out_of_warranty_charge("basic", 25, "defect", False) == 13 * 150

def test_excess_thirteen_accidental_surcharge():
    # nested if claim_type == "accidental" -> True
    assert out_of_warranty_charge("basic", 25, "accidental", False) == 13 * 275

def test_registered_basic_defect_small_excess():
    assert out_of_warranty_charge("basic", 20, "defect", True) == 200

def test_accidental_large_excess():
    assert out_of_warranty_charge("basic", 30, "accidental", False) == 18 * 275


# ---------- claim_allowed ----------

# if is_recall -> True, return claims_filed <= 5 (True / False)
def test_recall_claim_allowed_at_limit():
    assert claim_allowed(0, 5, True) is True

def test_recall_claim_rejected_over_limit():
    assert claim_allowed(100, 6, True) is False

# if days_since_last_claim < 30 -> True / False (boundary 29 / 30)
def test_claim_too_soon():
    assert claim_allowed(29, 0, False) is False

def test_claim_exactly_thirty_days():
    assert claim_allowed(30, 0, False) is True

# return claims_filed <= 2 (True / False)
def test_claim_allowed():
    assert claim_allowed(60, 1, False) is True

def test_claim_allowed_at_limit():
    assert claim_allowed(60, 2, False) is True

def test_claim_rejected_too_many_claims():
    assert claim_allowed(60, 3, False) is False


# ---------- sla_status ----------

# if is_hardware -> True / False, if is_priority -> True / False
def test_sla_hardware_priority_on_track():
    assert sla_status(100, True, True) == "on_track"

def test_sla_hardware_not_priority_cutoff():
    # cutoff 48
    assert sla_status(48, True, False) == "on_track"
    assert sla_status(47, True, False) == "at_risk"

def test_sla_software_priority_cutoff():
    # cutoff 24 + 24 = 48
    assert sla_status(48, False, True) == "on_track"
    assert sla_status(36, False, True) == "at_risk"
    assert sla_status(35, False, True) == "critical"

# if hours_left >= cutoff / elif hours_left >= cutoff - 12 / else
def test_sla_software_on_track_boundary():
    assert sla_status(24, False, False) == "on_track"

def test_sla_software_at_risk():
    assert sla_status(15, False, False) == "at_risk"

def test_sla_software_at_risk_lower_boundary():
    assert sla_status(12, False, False) == "at_risk"

def test_sla_software_critical():
    assert sla_status(11, False, False) == "critical"

def test_sla_hardware_priority_critical():
    # cutoff 72, at_risk from 60
    assert sla_status(59, True, True) == "critical"
