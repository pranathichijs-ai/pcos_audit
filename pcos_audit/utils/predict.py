"""
mock_predict() mirrors the exact JSON shape the real model will return.
When the real model is ready, swap this function out — inputs/outputs stay identical.
"""

def mock_predict(inputs: dict) -> dict:
    age = inputs.get("age")
    bmi = inputs.get("bmi")
    cycle_regular = inputs.get("cycle_regular")
    cycle_length_days = inputs.get("cycle_length_days")
    hirsutism = inputs.get("hirsutism", False)
    skin_darkening = inputs.get("skin_darkening", False)
    pimples = inputs.get("pimples", False)
    weight_gain = inputs.get("weight_gain", False)
    hair_loss = inputs.get("hair_loss", False)
    lh_miu_ml = inputs.get("lh_miu_ml")
    amh_ng_ml = inputs.get("amh_ng_ml")
    fsh_miu_ml = inputs.get("fsh_miu_ml")
    tsh_miu_l = inputs.get("tsh_miu_l")
    rbs_mg_dl = inputs.get("rbs_mg_dl")
    follicle_count_l = inputs.get("follicle_count_l", 0) or 0
    follicle_count_r = inputs.get("follicle_count_r", 0) or 0

    # --- Rotterdam criteria (rule-based) ---
    # O: Oligo/anovulation
    O = (cycle_regular is False) or (cycle_length_days is not None and cycle_length_days > 35)

    # H: Hyperandrogenism (clinical signs + elevated LH if available)
    clinical_H = hirsutism or pimples or skin_darkening
    biochem_H = (lh_miu_ml is not None and lh_miu_ml > 10)
    H = clinical_H or biochem_H

    # P: Polycystic ovaries on ultrasound (>=20 total follicles)
    total_follicles = follicle_count_l + follicle_count_r
    P = total_follicles >= 20

    criteria_met = {"O": O, "H": H, "P": P}
    score = sum([O, H, P])

    # Probability (mock — will be replaced by model)
    if score == 3:
        prob = 0.91
    elif score == 2:
        prob = 0.72
    elif score == 1:
        prob = 0.38
    else:
        prob = 0.12

    pcos_positive = prob >= 0.5

    # Phenotype
    if O and H and P:
        phenotype = "A"
    elif O and H:
        phenotype = "B"
    elif O and P:
        phenotype = "C"
    elif H and P:
        phenotype = "D"
    else:
        phenotype = "insufficient_data"

    # Confidence based on data completeness
    optional_fields = [lh_miu_ml, amh_ng_ml, fsh_miu_ml, tsh_miu_l,
                       rbs_mg_dl, follicle_count_l, follicle_count_r]
    filled = sum(1 for f in optional_fields if f is not None)
    if filled >= 5:
        confidence_level = "high"
    elif filled >= 2:
        confidence_level = "moderate"
    else:
        confidence_level = "low"

    # Missing tests
    missing_tests = []
    if lh_miu_ml is None:
        missing_tests.append("lh_miu_ml")
    if amh_ng_ml is None:
        missing_tests.append("amh_ng_ml")
    if follicle_count_l == 0 and follicle_count_r == 0:
        missing_tests.append("follicle_count (ultrasound)")

    # Equity flags
    equity_flags = []
    if bmi and bmi > 30 and not H:
        equity_flags.append("high_bmi_low_androgen")
    if age and age <= 21:
        equity_flags.append("young_bmi_normal")

    return {
        "pcos_probability": round(prob, 2),
        "pcos_positive": pcos_positive,
        "phenotype": phenotype,
        "criteria_met": criteria_met,
        "confidence_level": confidence_level,
        "missing_tests": missing_tests,
        "is_adolescent": age is not None and age <= 21,
        "equity_flags": equity_flags,
    }
