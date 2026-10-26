"""
Smart Placement Prediction & Career Analytics System
Stage 6 End-to-End Integration & Comprehensive Verification Test Suite
"""

import json
import sys
from app import app, predictor

def run_tests():
    print("=" * 78)
    print("SMART PLACEMENT ANALYTICS: END-TO-END INTEGRATION TEST SUITE (STAGE 6)")
    print("=" * 78)

    client = app.test_client()
    passed_tests = 0
    total_tests = 0

    def assert_test(name, condition, details=""):
        nonlocal passed_tests, total_tests
        total_tests += 1
        if condition:
            passed_tests += 1
            print(f"  [PASS] Test {total_tests:02d}: {name}")
        else:
            print(f"  [FAIL] Test {total_tests:02d}: {name} -> {details}")

    # Profiles for testing
    high_risk_student = {
        "CGPA": 7.7,
        "Internships": 1,
        "Projects": 1,
        "Workshops/Certifications": 0,
        "AptitudeTestScore": 69.0,
        "SoftSkillsRating": 4.0,
        "ExtracurricularActivities": "No",
        "PlacementTraining": "No",
        "SSC_Marks": 55.0,
        "HSC_Marks": 69.0
    }

    placed_student = {
        "CGPA": 7.9,
        "Internships": 1,
        "Projects": 3,
        "Workshops/Certifications": 2,
        "AptitudeTestScore": 90.0,
        "SoftSkillsRating": 4.8,
        "ExtracurricularActivities": "Yes",
        "PlacementTraining": "Yes",
        "SSC_Marks": 82.0,
        "HSC_Marks": 80.0
    }

    borderline_student = {
        "CGPA": 7.8,
        "Internships": 0,
        "Projects": 2,
        "Workshops/Certifications": 0,
        "AptitudeTestScore": 79.0,
        "SoftSkillsRating": 4.5,
        "ExtracurricularActivities": "Yes",
        "PlacementTraining": "No",
        "SSC_Marks": 80.0,
        "HSC_Marks": 81.0
    }

    # ----------------------------------------------------
    # 1. Test Web Page Route GET / & Layout Integrity
    # ----------------------------------------------------
    print("\n1. Testing Web Page Frontend Route (GET /)...")
    resp_home = client.get("/")
    assert_test(
        "Homepage (/) returns HTTP 200 OK",
        resp_home.status_code == 200,
        f"Status: {resp_home.status_code}"
    )
    html_content = resp_home.data.decode("utf-8")
    assert_test(
        "Homepage contains correct title and dashboard brand",
        "Smart Placement Prediction & Career Analytics System" in html_content and "SmartPlacement" in html_content,
        "HTML title/brand check failed"
    )
    assert_test(
        "Homepage contains all 10 input feature labels",
        all(k in html_content for k in ["CGPA", "SSC_Marks", "HSC_Marks", "AptitudeTestScore", "SoftSkillsRating", "Projects", "Workshops/Certifications", "Internships", "ExtracurricularActivities", "PlacementTraining"]),
        "Missing feature fields in HTML"
    )
    assert_test(
        "Homepage contains Dataset Partitioning and Class Balance components",
        "Dataset Partitioning &amp; Historical Placement Distribution" in html_content or "Dataset Partitioning & Historical Placement Distribution" in html_content,
        "Dataset partitioning section missing from HTML"
    )
    assert_test(
        "Homepage contains Academic & Aptitude Benchmark KPI cards",
        "Aptitude Test Score" in html_content and "College CGPA" in html_content and "84.42" in html_content and "8.01" in html_content,
        "Benchmark KPI cards missing from HTML"
    )
    assert_test(
        "Homepage contains Decision Support Advisory note (Estimates disclaimer)",
        "Decision Support Advisory" in html_content and "not absolute guarantees" in html_content,
        "Advisory disclaimer missing from HTML"
    )
    assert_test(
        "Homepage contains Stale Inputs Warning container and Recommendations refresh button",
        "stale-warning" in html_content and "btn-recalc-recs" in html_content,
        "Stale inputs warning or recommendations refresh button missing"
    )

    # ----------------------------------------------------
    # 2. Test GET /api/health
    # ----------------------------------------------------
    print("\n2. Testing GET /api/health...")
    resp = client.get("/api/health")
    data = resp.get_json()
    assert_test(
        "Health check returns HTTP 200",
        resp.status_code == 200,
        f"Status: {resp.status_code}"
    )
    assert_test(
        "Health check indicates healthy status and model loaded",
        data.get("status") == "healthy" and data.get("model_loaded") is True,
        f"Data: {data}"
    )
    assert_test(
        "Health check returns correct model name (Tuned Logistic Regression)",
        data.get("model_name") == "Tuned Logistic Regression",
        f"Model name: {data.get('model_name')}"
    )
    assert_test(
        "Health check reports 10 expected features",
        data.get("expected_features_count") == 10,
        f"Count: {data.get('expected_features_count')}"
    )

    # Test GET /api/sample-profiles
    resp_profiles = client.get("/api/sample-profiles")
    d_profiles = resp_profiles.get_json()
    assert_test(
        "Sample profiles returns HTTP 200 with at_risk, placed, and borderline profiles",
        resp_profiles.status_code == 200 and "at_risk" in d_profiles.get("profiles", {}) and "placed" in d_profiles.get("profiles", {}) and "borderline" in d_profiles.get("profiles", {}),
        f"Profiles: {d_profiles}"
    )

    # ----------------------------------------------------
    # 3. TASK 1: Student Risk Assessment & Boundary Cases
    # ----------------------------------------------------
    print("\n3. Testing Task 1: Student Risk Assessment & Boundary Cases...")
    
    # 3a. High Risk Case (prob < 0.40, risk > 0.60)
    resp_high = client.post("/api/predict", data=json.dumps(high_risk_student), content_type="application/json")
    d_high = resp_high.get_json()
    assert_test(
        "High-Risk student returns prediction 'NotPlaced' and risk_level 'High'",
        d_high.get("prediction") == "NotPlaced" and d_high.get("risk_level") == "High",
        f"Result: {d_high}"
    )
    assert_test(
        "High-Risk risk_score matches 1 - placement_prob (0.9095)",
        d_high.get("risk_score") == 0.9095 and d_high.get("placement_probability") == 0.0905,
        f"Prob: {d_high.get('placement_probability')}, Risk: {d_high.get('risk_score')}"
    )

    # 3b. Low Risk Case (prob >= 0.70, risk <= 0.30)
    resp_low = client.post("/api/predict", data=json.dumps(placed_student), content_type="application/json")
    d_low = resp_low.get_json()
    assert_test(
        "Strong placed student returns prediction 'Placed' and risk_level 'Low'",
        d_low.get("prediction") == "Placed" and d_low.get("risk_level") == "Low",
        f"Result: {d_low}"
    )
    assert_test(
        "Low-Risk student placement prob >= 0.70 and risk score <= 0.30",
        d_low.get("placement_probability") >= 0.70 and d_low.get("risk_score") <= 0.30,
        f"Prob: {d_low.get('placement_probability')}, Risk: {d_low.get('risk_score')}"
    )

    # 3c. Medium Risk Case (0.40 <= prob < 0.70, 0.30 < risk <= 0.60)
    resp_med = client.post("/api/predict", data=json.dumps(borderline_student), content_type="application/json")
    d_med = resp_med.get_json()
    assert_test(
        "Borderline student risk_score falls in Medium range (0.30 < risk <= 0.60)",
        0.30 < d_med.get("risk_score") <= 0.60 and d_med.get("risk_level") == "Medium",
        f"Prob: {d_med.get('placement_probability')}, Risk: {d_med.get('risk_score')}, Level: {d_med.get('risk_level')}"
    )

    # 3d. Probability invariant: placement_prob + non_placement_prob == 1.0
    for label, d in [("High", d_high), ("Low", d_low), ("Med", d_med)]:
        p = d.get("placement_probability")
        np_p = d.get("non_placement_probability")
        assert_test(
            f"Probability invariant holds for {label} profile ({p} + {np_p} == 1.0)",
            round(p + np_p, 4) == 1.0,
            f"Sum: {p + np_p}"
        )

    # 3e. Risk thresholds verification against models/model_metadata.json
    assert_test(
        "Risk thresholds match metadata (low_max=0.3, medium_max=0.6)",
        predictor.risk_thresholds.get("low_max") == 0.3 and predictor.risk_thresholds.get("medium_max") == 0.6,
        f"Thresholds: {predictor.risk_thresholds}"
    )

    # 3f. Boundary Case Verification
    # Boundary 1: Placement prob 0.70 -> risk 0.30 -> Low Risk
    r1, l1 = predictor.calculate_risk(0.70)
    assert_test("Boundary: Placement prob 0.70 -> Risk 0.30 (Low Risk boundary)", r1 == 0.30 and l1 == "Low", f"Got: {r1}, {l1}")

    # Boundary 2: Placement prob 0.6999 -> risk 0.3001 -> Medium Risk (just above low_max)
    r2, l2 = predictor.calculate_risk(0.6999)
    assert_test("Boundary: Placement prob 0.6999 -> Risk 0.3001 (Medium Risk lower edge)", r2 == 0.3001 and l2 == "Medium", f"Got: {r2}, {l2}")

    # Boundary 3: Placement prob 0.40 -> risk 0.60 -> Medium Risk (upper medium_max)
    r3, l3 = predictor.calculate_risk(0.40)
    assert_test("Boundary: Placement prob 0.40 -> Risk 0.60 (Medium Risk upper edge)", r3 == 0.60 and l3 == "Medium", f"Got: {r3}, {l3}")

    # Boundary 4: Placement prob 0.3999 -> risk 0.6001 -> High Risk (just above medium_max)
    r4, l4 = predictor.calculate_risk(0.3999)
    assert_test("Boundary: Placement prob 0.3999 -> Risk 0.6001 (High Risk threshold)", r4 == 0.6001 and l4 == "High", f"Got: {r4}, {l4}")

    # Boundary 5: Certain placement prob 1.0 -> Risk 0.0 -> Low Risk
    r5, l5 = predictor.calculate_risk(1.0)
    assert_test("Boundary: Placement prob 1.00 -> Risk 0.00 (Minimum Risk Low)", r5 == 0.0 and l5 == "Low", f"Got: {r5}, {l5}")

    # Boundary 6: Certain non-placement prob 0.0 -> Risk 1.0 -> High Risk
    r6, l6 = predictor.calculate_risk(0.0)
    assert_test("Boundary: Placement prob 0.00 -> Risk 1.00 (Maximum Risk High)", r6 == 1.0 and l6 == "High", f"Got: {r6}, {l6}")

    # ----------------------------------------------------
    # 4. TASK 2: What-If Analysis Detailed Validation
    # ----------------------------------------------------
    print("\n4. Testing Task 2: What-If Analysis Verification...")
    resp_wi = client.post("/api/what-if", data=json.dumps(high_risk_student), content_type="application/json")
    d_wi = resp_wi.get_json()
    assert_test(
        "What-if returns HTTP 200 with success status",
        resp_wi.status_code == 200 and d_wi.get("status") == "success",
        f"Status: {resp_wi.status_code}"
    )
    scenarios = d_wi.get("scenarios", [])
    assert_test(
        "What-if contains Baseline + 6 improvement scenarios (total 7)",
        len(scenarios) == 7,
        f"Count: {len(scenarios)}"
    )

    # Scenario deltas verification matching reports/what_if_scenario_comparison.csv
    scenario_map = {s["Scenario"]: s for s in scenarios}
    assert_test(
        "Baseline probability exactly matches predict endpoint (0.0905)",
        scenario_map.get("Baseline", {}).get("PlacementProbability") == 0.0905,
        f"Baseline: {scenario_map.get('Baseline')}"
    )
    assert_test(
        "Aptitude +10 increases probability by +4.89 pp (0.0905 -> 0.1394)",
        scenario_map.get("Aptitude +10", {}).get("Change_vs_Baseline_pp") == 4.89 and scenario_map.get("Aptitude +10", {}).get("PlacementProbability") == 0.1394,
        f"Aptitude scenario: {scenario_map.get('Aptitude +10')}"
    )
    assert_test(
        "Projects +1 increases probability by +2.61 pp (0.0905 -> 0.1166)",
        scenario_map.get("Projects +1", {}).get("Change_vs_Baseline_pp") == 2.61 and scenario_map.get("Projects +1", {}).get("PlacementProbability") == 0.1166,
        f"Projects scenario: {scenario_map.get('Projects +1')}"
    )
    assert_test(
        "Soft Skills +0.5 increases probability by +2.44 pp (0.0905 -> 0.1149)",
        scenario_map.get("Soft Skills +0.5", {}).get("Change_vs_Baseline_pp") == 2.44 and scenario_map.get("Soft Skills +0.5", {}).get("PlacementProbability") == 0.1149,
        f"Soft skills scenario: {scenario_map.get('Soft Skills +0.5')}"
    )
    assert_test(
        "Certifications +1 increases probability by +1.20 pp (0.0905 -> 0.1025)",
        scenario_map.get("Certifications +1", {}).get("Change_vs_Baseline_pp") == 1.20 and scenario_map.get("Certifications +1", {}).get("PlacementProbability") == 0.1025,
        f"Certs scenario: {scenario_map.get('Certifications +1')}"
    )
    assert_test(
        "Combined package yields +22.93 pp cumulative gain (0.0905 -> 0.3198)",
        scenario_map.get("Combined Growth Package", {}).get("Change_vs_Baseline_pp") == 22.93,
        f"Combined: {scenario_map.get('Combined Growth Package')}"
    )

    # What-if on Placed Student Profile (verifies dynamic profile simulation)
    resp_wi_placed = client.post("/api/what-if", data=json.dumps(placed_student), content_type="application/json")
    d_wi_placed = resp_wi_placed.get_json()
    scenarios_placed = d_wi_placed.get("scenarios", [])
    assert_test(
        "What-if for Placed Student generates 6 scenarios (omits Training because already Yes)",
        len(scenarios_placed) == 6 and not any(s["Scenario"] == "Enroll in Placement Training" for s in scenarios_placed),
        f"Placed scenarios count: {len(scenarios_placed)}"
    )
    assert_test(
        "Placed student baseline probability reflects actual high probability (> 0.70)",
        scenarios_placed[0]["PlacementProbability"] >= 0.70 and scenarios_placed[0]["RiskLevel"] == "Low",
        f"Baseline: {scenarios_placed[0]}"
    )

    # What-if error handling
    resp_wi_err = client.post("/api/what-if", data=json.dumps({"CGPA": -3.0}), content_type="application/json")
    assert_test(
        "Invalid input to What-if returns HTTP 400 Bad Request",
        resp_wi_err.status_code == 400 and resp_wi_err.get_json().get("status") == "fail",
        f"Response: {resp_wi_err.data}"
    )

    # ----------------------------------------------------
    # 5. TASK 3: Career Recommendations Detailed Validation
    # ----------------------------------------------------
    print("\n5. Testing Task 3: Career Recommendations Verification...")
    resp_rec = client.post("/api/recommendations", data=json.dumps(high_risk_student), content_type="application/json")
    d_rec = resp_rec.get_json()
    assert_test(
        "Recommendations returns HTTP 200 with success status",
        resp_rec.status_code == 200 and d_rec.get("status") == "success",
        f"Status: {resp_rec.status_code}"
    )
    recs = d_rec.get("recommendations", [])
    assert_test(
        "Returns 5 prioritized career recommendations",
        len(recs) == 5,
        f"Count: {len(recs)}"
    )

    # Verify descending sort by impact boost
    deltas = [r["Placement_Probability_Change_pp"] for r in recs]
    assert_test(
        "Recommendations are sorted in descending order of probability boost",
        deltas == sorted(deltas, reverse=True),
        f"Deltas: {deltas}"
    )

    # Verify all 8 fields present on each recommendation item
    required_rec_fields = ["Feature", "Recommendation", "Suggested_Action", "Current_Value", "Simulated_Value", "Benchmark_Placed_Avg", "Placement_Probability_Change_pp", "Simulated_Risk"]
    all_fields_ok = all(all(f in r for f in required_rec_fields) for r in recs)
    assert_test(
        "Each recommendation item contains all 8 required analytical fields",
        all_fields_ok,
        f"Sample rec: {recs[0] if recs else None}"
    )

    # Recommendations on Placed Student (verifies dynamic profile values)
    resp_rec_placed = client.post("/api/recommendations", data=json.dumps(placed_student), content_type="application/json")
    d_rec_placed = resp_rec_placed.get_json()
    recs_placed = d_rec_placed.get("recommendations", [])
    apt_rec = next((r for r in recs_placed if r["Feature"] == "AptitudeTestScore"), {})
    proj_rec = next((r for r in recs_placed if r["Feature"] == "Projects"), {})
    assert_test(
        "Recommendations for Placed Student reflect actual input values (Aptitude=90.0, Projects=3)",
        apt_rec.get("Current_Value") == 90.0 and proj_rec.get("Current_Value") == 3.0,
        f"Aptitude: {apt_rec}, Projects: {proj_rec}"
    )

    # Recommendations error handling
    resp_rec_err = client.post("/api/recommendations", data=json.dumps({"AptitudeTestScore": 180.0}), content_type="application/json")
    assert_test(
        "Invalid input to Recommendations returns HTTP 400 Bad Request",
        resp_rec_err.status_code == 400 and resp_rec_err.get_json().get("status") == "fail",
        f"Response: {resp_rec_err.data}"
    )

    # ----------------------------------------------------
    # 6. TASK 4: Frontend Integration & Stale-Result Prevention
    # ----------------------------------------------------
    print("\n6. Testing Task 4: Frontend Integration & Stale Prevention...")
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html_src = f.read()
    with open("static/js/main.js", "r", encoding="utf-8") as f:
        js_src = f.read()

    assert_test(
        "Frontend HTML has prediction, recalculate, and reset button elements",
        all(bid in html_src for bid in ["btn-submit-predict", "btn-recalc-whatif", "btn-recalc-recs", "btn-reset-form"]),
        "Missing interactive button IDs in index.html"
    )
    assert_test(
        "Frontend HTML contains stale input warning banner and advisory disclaimers",
        "stale-warning" in html_src and "estimate-disclaimer" in html_src,
        "Missing stale warning or disclaimer classes"
    )
    assert_test(
        "Frontend JS attaches input modification listener to flag stale results",
        "stale-warning" in js_src and "form.addEventListener('input'" in js_src,
        "Missing input event listener for stale result warning in main.js"
    )
    assert_test(
        "Frontend JS sets immediate loading spinner states to clear previous student results",
        "loading-state" in js_src and "spinner" in js_src,
        "Missing loading states in main.js"
    )
    assert_test(
        "Frontend JS reset button clears scenarios, recommendations, and chart instances",
        "btn-reset-form" in js_src and "whatIfChartInstance.destroy()" in js_src,
        "Reset button does not clear previous results and charts"
    )

    # ----------------------------------------------------
    # 7. Analytics Data Integrity Checks
    # ----------------------------------------------------
    print("\n7. Testing Analytics Data Integrity...")
    resp_analytics = client.get("/api/analytics-data")
    analytics_json = resp_analytics.get_json()
    payload_data = analytics_json.get("data", {})

    models = payload_data.get("model_comparisons", [])
    assert_test(
        "Analytics data contains exactly 10 candidate models",
        len(models) == 10,
        f"Count: {len(models)}"
    )

    cv = payload_data.get("cross_validation", [])
    assert_test(
        "Cross-validation contains 3 benchmark models with stability stats",
        len(cv) == 3,
        f"CV data: {cv}"
    )

    shap = payload_data.get("shap_importance", [])
    assert_test(
        "SHAP importance contains all 12 feature components with Aptitude rank #1",
        len(shap) == 12 and shap[0].get("Feature") == "numeric__AptitudeTestScore",
        f"Top SHAP feature: {shap[0] if shap else None}"
    )

    risk = payload_data.get("risk_summary", [])
    assert_test(
        "Risk summary contains Low, Medium, High summing to 1,984 test students",
        len(risk) == 3 and sum(r.get("Students", 0) for r in risk) == 1984,
        f"Risk summary: {risk}"
    )

    comp = payload_data.get("placement_comparison", [])
    placed_row = next((c for c in comp if c.get("PlacementStatus") == "Placed"), {})
    not_placed_row = next((c for c in comp if c.get("PlacementStatus") == "NotPlaced"), {})
    assert_test(
        "Placement comparison has 2,611 Placed (CGPA 8.01) vs 3,742 NotPlaced (CGPA 7.47)",
        placed_row.get("student_count") == 2611 and placed_row.get("mean_cgpa") == 8.01 and not_placed_row.get("student_count") == 3742 and not_placed_row.get("mean_cgpa") == 7.47,
        f"Placed: {placed_row}, NotPlaced: {not_placed_row}"
    )

    eda = payload_data.get("eda_summary", {})
    assert_test(
        "EDA summary reports 6,353 train, 1,591 val, 1,984 test records (9,928 total)",
        eda.get("training_records") == 6353 and eda.get("validation_records") == 1591 and eda.get("test_records") == 1984,
        f"EDA summary: {eda}"
    )

    # ----------------------------------------------------
    # 8. Static Reports & Figure Serving
    # ----------------------------------------------------
    print("\n8. Testing Static Report Figure Serving...")
    figures = [
        "01_placement_distribution.png",
        "02_academic_and_aptitude.png",
        "03_experience_and_projects.png",
        "04_training_and_extracurriculars.png",
        "05_correlation_heatmap.png"
    ]
    all_figs_ok = all(client.get(f"/reports/figures/{fig}").status_code == 200 for fig in figures)
    assert_test(
        "All 5 Phase 1 EDA figures return HTTP 200",
        all_figs_ok,
        "Figure serving check failed"
    )

    resp_ten = client.get("/reports/ten_model_comparison.png")
    assert_test(
        "Ten-model comparison figure returns HTTP 200",
        resp_ten.status_code == 200 and len(resp_ten.data) > 0,
        f"Status: {resp_ten.status_code}"
    )

    # ----------------------------------------------------
    # Final Summary
    # ----------------------------------------------------
    print("\n" + "=" * 78)
    print(f"RESULTS: {passed_tests}/{total_tests} TESTS PASSED")
    print("=" * 78)

    if passed_tests == total_tests:
        print("[SUCCESS] All Stage 5 Advanced Features & Data Integrity tests passed perfectly!")
        return 0
    else:
        print("[FAILURE] Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
