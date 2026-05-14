import streamlit as st
import json
from utils.predict import mock_predict
from utils.audit import run_audit

st.set_page_config(page_title="PCOS Forensic Audit Tool", layout="wide")

st.title("PCOS Forensic Audit Tool")
st.caption("Teammate 1 — Rotterdam criteria · visit-by-visit analysis · mock predict()")

# ── Session state ──────────────────────────────────────────────────────────────
if "num_visits" not in st.session_state:
    st.session_state.num_visits = 1

# ── Add / remove visits ────────────────────────────────────────────────────────
col_add, col_remove, _ = st.columns([1, 1, 4])
with col_add:
    if st.button("＋ Add visit"):
        st.session_state.num_visits += 1
with col_remove:
    if st.button("－ Remove last") and st.session_state.num_visits > 1:
        st.session_state.num_visits -= 1

st.divider()

# ── Visit input forms ──────────────────────────────────────────────────────────
visit_inputs = []

for i in range(st.session_state.num_visits):
    with st.expander(f"Visit {i + 1}", expanded=True):
        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("**Demographics**")
            age = st.number_input("Age", min_value=15, max_value=50, value=None,
                                  placeholder="15–50", key=f"age_{i}")
            bmi = st.number_input("BMI (kg/m²)", min_value=10.0, max_value=60.0,
                                  value=None, placeholder="e.g. 24.5",
                                  format="%.1f", key=f"bmi_{i}")
            weight_kg = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0,
                                        value=None, placeholder="optional",
                                        format="%.1f", key=f"weight_{i}")

        with c2:
            st.markdown("**Cycle**")
            cycle_regular_str = st.selectbox(
                "Cycle regular?",
                options=["— not recorded —", "Regular", "Irregular"],
                key=f"cycle_reg_{i}"
            )
            cycle_regular = None if cycle_regular_str == "— not recorded —" \
                else (cycle_regular_str == "Regular")

            cycle_length_days = st.number_input(
                "Cycle length (days)", min_value=21, max_value=90,
                value=None, placeholder="21–45", key=f"cycle_len_{i}"
            )

            st.markdown("**Symptoms**")
            hirsutism     = st.checkbox("Hirsutism (excess hair)", key=f"hirs_{i}")
            skin_darkening = st.checkbox("Skin darkening", key=f"skin_{i}")
            pimples       = st.checkbox("Pimples / acne", key=f"pimples_{i}")
            weight_gain   = st.checkbox("Unexplained weight gain", key=f"wgain_{i}")
            hair_loss     = st.checkbox("Hair loss / thinning", key=f"hloss_{i}")

        with c3:
            st.markdown("**Lab values** (optional)")
            lh_miu_ml  = st.number_input("LH (mIU/mL)",  value=None, placeholder="optional",
                                         format="%.1f", key=f"lh_{i}")
            fsh_miu_ml = st.number_input("FSH (mIU/mL)", value=None, placeholder="optional",
                                         format="%.1f", key=f"fsh_{i}")
            amh_ng_ml  = st.number_input("AMH (ng/mL)",  value=None, placeholder="optional",
                                         format="%.1f", key=f"amh_{i}")
            tsh_miu_l  = st.number_input("TSH (mIU/L)",  value=None, placeholder="optional",
                                         format="%.1f", key=f"tsh_{i}")
            rbs_mg_dl  = st.number_input("RBS (mg/dL)",  value=None, placeholder="optional",
                                         format="%.1f", key=f"rbs_{i}")

            st.markdown("**Ultrasound** (optional)")
            fcl = st.number_input("Follicles — left ovary",  value=None, placeholder="count",
                                  min_value=0, key=f"fcl_{i}")
            fcr = st.number_input("Follicles — right ovary", value=None, placeholder="count",
                                  min_value=0, key=f"fcr_{i}")

        visit_inputs.append({
            "age": age, "bmi": bmi, "weight_kg": weight_kg,
            "cycle_regular": cycle_regular, "cycle_length_days": cycle_length_days,
            "hirsutism": hirsutism, "skin_darkening": skin_darkening,
            "pimples": pimples, "weight_gain": weight_gain, "hair_loss": hair_loss,
            "lh_miu_ml": lh_miu_ml, "fsh_miu_ml": fsh_miu_ml, "amh_ng_ml": amh_ng_ml,
            "tsh_miu_l": tsh_miu_l, "rbs_mg_dl": rbs_mg_dl,
            "follicle_count_l": fcl, "follicle_count_r": fcr,
        })

st.divider()

# ── Run audit ──────────────────────────────────────────────────────────────────
if st.button("🔍 Run forensic audit", type="primary", use_container_width=True):

    # Run predict() on every visit
    visit_results = []
    for i, inputs in enumerate(visit_inputs):
        result = mock_predict(inputs)
        result["visit"] = i + 1
        result["inputs"] = inputs
        visit_results.append(result)

    report = run_audit(visit_results)
    summary = report["patient_summary"]

    # ── Summary metrics ────────────────────────────────────────────────────────
    st.subheader("Audit report")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Visits analysed", summary["visits_analysed"])
    m2.metric("Visits flagged +ve", summary["total_flagged_visits"])
    m3.metric("Missed opportunities", summary["missed_opportunities"],
              delta="⚠ review" if summary["missed_opportunities"] > 0 else None,
              delta_color="inverse")
    m4.metric("First positive visit",
              f"Visit {summary['first_positive_visit']}" if summary["first_positive_visit"] else "None")

    # ── Missed opportunity alert ───────────────────────────────────────────────
    if summary["missed_opportunities"] > 0:
        missed = summary["missed_opportunity_visits"]
        visits_str = ", ".join(f"visit {m['visit']}" for m in missed)
        st.warning(
            f"⚠ Rotterdam criteria first met at visit {summary['first_positive_visit']}, "
            f"but {summary['missed_opportunities']} prior visit(s) showed partial criteria "
            f"({visits_str}). These may represent missed diagnosis opportunities."
        )

    # ── Visit timeline ─────────────────────────────────────────────────────────
    st.subheader("Visit timeline")

    for v in visit_results:
        cm = v["criteria_met"]
        score = sum(cm.values())
        prob = v["pcos_probability"]

        if v["pcos_positive"]:
            icon, color = "🔴", "red"
        elif score == 1:
            icon, color = "🟡", "orange"
        else:
            icon, color = "🟢", "green"

        with st.container(border=True):
            col_icon, col_main, col_criteria = st.columns([0.3, 2, 2])

            with col_icon:
                st.markdown(f"### {icon}")
                st.caption(f"Visit {v['visit']}")

            with col_main:
                st.markdown(f"**p(PCOS) = {prob:.2f}** · Phenotype: `{v['phenotype']}` · Confidence: `{v['confidence_level']}`")
                if v["pcos_positive"]:
                    st.error("Rotterdam criteria met (≥2) — PCOS positive")
                elif score == 1:
                    st.warning("1 criterion met — monitor")
                else:
                    st.success("No criteria met")

                if v["missing_tests"]:
                    st.caption(f"Missing tests: {', '.join(v['missing_tests'])}")
                if v["equity_flags"]:
                    st.caption(f"Equity flags: {', '.join(v['equity_flags'])}")
                if v.get("is_adolescent"):
                    st.caption("⚠ Adolescent — separate diagnostic track applies")

            with col_criteria:
                c_o, c_h, c_p = st.columns(3)
                def criterion_display(col, label, met, description):
                    with col:
                        if met:
                            st.success(f"**{label}** ✓")
                        else:
                            st.error(f"**{label}** ✗")
                        st.caption(description)

                criterion_display(c_o, "O", cm["O"], "Oligo/anovulation")
                criterion_display(c_h, "H", cm["H"], "Hyperandrogenism")
                criterion_display(c_p, "P", cm["P"], "Polycystic ovaries")

    # ── Criteria pattern across all visits ────────────────────────────────────
    st.subheader("Criteria pattern across all visits")
    pattern = summary["criteria_pattern"]
    p1, p2, p3 = st.columns(3)
    p1.metric("O met in visits", f"{pattern['O_visit_count']} / {summary['visits_analysed']}")
    p2.metric("H met in visits", f"{pattern['H_visit_count']} / {summary['visits_analysed']}")
    p3.metric("P met in visits", f"{pattern['P_visit_count']} / {summary['visits_analysed']}")

    # ── Output JSON ────────────────────────────────────────────────────────────
    st.subheader("Output JSON — share with teammates")
    st.caption("This is the exact schema Teammate 2 (equity layer) and Teammate 3 (UI) will consume.")

    output_json = {
        "patient_summary": summary,
        "visits": [
            {k: v for k, v in visit.items() if k != "inputs"}
            for visit in visit_results
        ]
    }

    st.json(output_json)

    col_dl, _ = st.columns([1, 3])
    with col_dl:
        st.download_button(
            label="⬇ Download JSON",
            data=json.dumps(output_json, indent=2),
            file_name="pcos_audit_output.json",
            mime="application/json",
        )
