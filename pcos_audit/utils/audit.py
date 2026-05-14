"""
Rotterdam audit engine.
Takes a list of visit outputs from predict() and generates the forensic report.
"""

def run_audit(visit_results: list[dict]) -> dict:
    """
    visit_results: list of dicts, each is the output of predict() with visit number added.
    Returns a structured audit report.
    """
    flagged = [v for v in visit_results if v["pcos_positive"]]
    first_flagged = flagged[0] if flagged else None

    # Missed opportunities = visits before first positive that had 1 criterion met
    missed_opportunities = []
    if first_flagged:
        first_idx = visit_results.index(first_flagged)
        for v in visit_results[:first_idx]:
            score = sum(v["criteria_met"].values())
            if score >= 1:
                missed_opportunities.append({
                    "visit": v["visit"],
                    "criteria_met": v["criteria_met"],
                    "score": score,
                    "missing_tests": v["missing_tests"],
                })

    # Aggregate pattern across all visits
    all_O = [v["criteria_met"]["O"] for v in visit_results]
    all_H = [v["criteria_met"]["H"] for v in visit_results]
    all_P = [v["criteria_met"]["P"] for v in visit_results]

    return {
        "patient_summary": {
            "visits_analysed": len(visit_results),
            "first_positive_visit": first_flagged["visit"] if first_flagged else None,
            "total_flagged_visits": len(flagged),
            "missed_opportunities": len(missed_opportunities),
            "missed_opportunity_visits": missed_opportunities,
            "criteria_pattern": {
                "O_ever_met": any(all_O),
                "H_ever_met": any(all_H),
                "P_ever_met": any(all_P),
                "O_visit_count": sum(all_O),
                "H_visit_count": sum(all_H),
                "P_visit_count": sum(all_P),
            }
        },
        "visits": visit_results,
    }
