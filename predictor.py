"""
Smart Placement Prediction & Career Analytics System
Model Inference, Validation, Risk Classification & What-If Engine
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List, Optional

# Base directory for the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

METADATA_PATH = os.path.join(MODELS_DIR, "model_metadata.json")
MODEL_PATH = os.path.join(MODELS_DIR, "placement_model.joblib")
BENCHMARK_PATH = os.path.join(REPORTS_DIR, "placement_comparison.csv")

# Placed student benchmarks from placement_comparison.csv
DEFAULT_BENCHMARKS = {
    "CGPA": 8.01,
    "AptitudeTestScore": 84.42,
    "Internships": 1.24,
    "Projects": 2.50,
    "Workshops/Certifications": 1.39,
    "SoftSkillsRating": 4.52,
    "SSC_Marks": 74.69,
    "HSC_Marks": 79.75
}

class PlacementPredictor:
    """Handles loading the trained model, feature validation, prediction, risk calculation, and what-if simulation."""

    def __init__(self, model_path: Optional[str] = None, metadata_path: Optional[str] = None):
        self.model_path = model_path or MODEL_PATH
        self.metadata_path = metadata_path or METADATA_PATH
        self.model = None
        self.metadata = {}
        self.features: List[str] = []
        self.risk_thresholds: Dict[str, float] = {}
        self.benchmarks: Dict[str, float] = self._load_benchmarks()
        self._load_artifacts()

    def _load_benchmarks(self) -> Dict[str, float]:
        """Loads historical placement feature benchmarks if available."""
        if os.path.exists(BENCHMARK_PATH):
            try:
                df = pd.read_csv(BENCHMARK_PATH)
                placed_row = df[df["PlacementStatus"] == "Placed"]
                if not placed_row.empty:
                    row = placed_row.iloc[0]
                    return {
                        "CGPA": float(row.get("mean_cgpa", DEFAULT_BENCHMARKS["CGPA"])),
                        "AptitudeTestScore": float(row.get("mean_aptitude", DEFAULT_BENCHMARKS["AptitudeTestScore"])),
                        "Internships": float(row.get("mean_internships", DEFAULT_BENCHMARKS["Internships"])),
                        "Projects": float(row.get("mean_projects", DEFAULT_BENCHMARKS["Projects"])),
                        "Workshops/Certifications": float(row.get("mean_certifications", DEFAULT_BENCHMARKS["Workshops/Certifications"])),
                        "SoftSkillsRating": float(row.get("mean_soft_skills", DEFAULT_BENCHMARKS["SoftSkillsRating"])),
                        "SSC_Marks": float(row.get("mean_ssc", DEFAULT_BENCHMARKS["SSC_Marks"])),
                        "HSC_Marks": float(row.get("mean_hsc", DEFAULT_BENCHMARKS["HSC_Marks"]))
                    }
            except Exception:
                pass
        return DEFAULT_BENCHMARKS.copy()

    def _load_artifacts(self) -> None:
        """Loads the metadata JSON and joblib model."""
        if not os.path.exists(self.metadata_path):
            raise FileNotFoundError(f"Metadata file not found: {self.metadata_path}")
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        with open(self.metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        self.features = self.metadata.get("features", [
            "CGPA",
            "Internships",
            "Projects",
            "Workshops/Certifications",
            "AptitudeTestScore",
            "SoftSkillsRating",
            "ExtracurricularActivities",
            "PlacementTraining",
            "SSC_Marks",
            "HSC_Marks"
        ])
        self.risk_thresholds = self.metadata.get("risk_thresholds", {"low_max": 0.3, "medium_max": 0.6})
        self.model = joblib.load(self.model_path)

    def validate_and_prepare_input(self, raw_input: Dict[str, Any]) -> pd.DataFrame:
        """
        Validates raw input dict and produces a 1-row DataFrame matching the exact 10 features
        and types expected by the pipeline.
        """
        data: Dict[str, Any] = {}

        # 1. CGPA (float 0 - 10)
        try:
            val = float(raw_input.get("CGPA", 0.0))
            if not (0.0 <= val <= 10.0):
                raise ValueError(f"CGPA must be between 0.0 and 10.0, received: {val}")
            data["CGPA"] = val
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid CGPA value: {e}")

        # 2. Internships (int >= 0)
        try:
            val = int(raw_input.get("Internships", 0))
            if val < 0:
                raise ValueError("Internships cannot be negative")
            data["Internships"] = val
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid Internships value: {e}")

        # 3. Projects (int >= 0)
        try:
            val = int(raw_input.get("Projects", 0))
            if val < 0:
                raise ValueError("Projects cannot be negative")
            data["Projects"] = val
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid Projects value: {e}")

        # 4. Workshops/Certifications (int >= 0) - preserve exact slash name
        try:
            cert_val = raw_input.get("Workshops/Certifications", raw_input.get("Workshops_Certifications", raw_input.get("Certifications", 0)))
            val = int(cert_val)
            if val < 0:
                raise ValueError("Workshops/Certifications cannot be negative")
            data["Workshops/Certifications"] = val
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid Workshops/Certifications value: {e}")

        # 5. AptitudeTestScore (float/int 0 - 100)
        try:
            val = float(raw_input.get("AptitudeTestScore", 0.0))
            if not (0.0 <= val <= 100.0):
                raise ValueError(f"AptitudeTestScore must be between 0 and 100, received: {val}")
            data["AptitudeTestScore"] = val
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid AptitudeTestScore value: {e}")

        # 6. SoftSkillsRating (float 1.0 - 5.0)
        try:
            val = float(raw_input.get("SoftSkillsRating", 1.0))
            if not (1.0 <= val <= 5.0):
                raise ValueError(f"SoftSkillsRating must be between 1.0 and 5.0, received: {val}")
            data["SoftSkillsRating"] = val
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid SoftSkillsRating value: {e}")

        # 7. ExtracurricularActivities ("Yes" or "No")
        raw_extra = str(raw_input.get("ExtracurricularActivities", "No")).strip().capitalize()
        if raw_extra not in ["Yes", "No"]:
            if str(raw_input.get("ExtracurricularActivities")).lower() in ["1", "true"]:
                raw_extra = "Yes"
            else:
                raw_extra = "No"
        data["ExtracurricularActivities"] = raw_extra

        # 8. PlacementTraining ("Yes" or "No")
        raw_train = str(raw_input.get("PlacementTraining", "No")).strip().capitalize()
        if raw_train not in ["Yes", "No"]:
            if str(raw_input.get("PlacementTraining")).lower() in ["1", "true"]:
                raw_train = "Yes"
            else:
                raw_train = "No"
        data["PlacementTraining"] = raw_train

        # 9. SSC_Marks (float/int 0 - 100)
        try:
            val = float(raw_input.get("SSC_Marks", 0.0))
            if not (0.0 <= val <= 100.0):
                raise ValueError(f"SSC_Marks must be between 0 and 100, received: {val}")
            data["SSC_Marks"] = val
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid SSC_Marks value: {e}")

        # 10. HSC_Marks (float/int 0 - 100)
        try:
            val = float(raw_input.get("HSC_Marks", 0.0))
            if not (0.0 <= val <= 100.0):
                raise ValueError(f"HSC_Marks must be between 0 and 100, received: {val}")
            data["HSC_Marks"] = val
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid HSC_Marks value: {e}")

        # Create DataFrame with exact column ordering
        df = pd.DataFrame([data], columns=self.features)
        return df

    def calculate_risk(self, placement_prob: float) -> Tuple[float, str]:
        """
        Calculates Risk of Non-Placement and classifies it according to metadata thresholds.
        Risk score = 1 - Placement Probability.
        - Low Risk: Risk <= 0.30  (Placement Prob >= 0.70)
        - Medium Risk: 0.30 < Risk <= 0.60 (Placement Prob between 0.40 and 0.70)
        - High Risk: Risk > 0.60  (Placement Prob < 0.40)
        """
        risk_score = round(1.0 - placement_prob, 4)
        low_max = self.risk_thresholds.get("low_max", 0.3)
        med_max = self.risk_thresholds.get("medium_max", 0.6)

        if risk_score <= low_max:
            risk_level = "Low"
        elif risk_score <= med_max:
            risk_level = "Medium"
        else:
            risk_level = "High"

        return risk_score, risk_level

    def predict(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """Performs placement prediction, computes probabilities, and assigns risk level."""
        df = self.validate_and_prepare_input(raw_input)

        # Scikit-learn predict & predict_proba
        probabilities = self.model.predict_proba(df)[0]
        # Positive class index corresponds to class 1 ("Placed")
        classes = list(self.model.classes_)
        if 1 in classes:
            pos_idx = classes.index(1)
        elif "Placed" in classes:
            pos_idx = classes.index("Placed")
        else:
            pos_idx = 1

        placement_prob = round(float(probabilities[pos_idx]), 4)
        non_placement_prob = round(float(1.0 - placement_prob), 4)

        risk_score, risk_level = self.calculate_risk(placement_prob)

        # Predicted label based on model decision threshold (0.5)
        predicted_class = int(self.model.predict(df)[0] if not isinstance(self.model.predict(df)[0], (str, np.str_)) else (1 if self.model.predict(df)[0] == "Placed" else 0))
        predicted_label = "Placed" if placement_prob >= 0.50 else "NotPlaced"

        return {
            "prediction": predicted_label,
            "predicted_class": predicted_class,
            "placement_probability": placement_prob,
            "non_placement_probability": non_placement_prob,
            "placement_percentage": round(placement_prob * 100, 2),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "features_used": df.iloc[0].to_dict()
        }

    def simulate_what_if_scenarios(self, raw_input: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Simulates actionable improvement scenarios matching what_if_scenario_comparison.csv:
        1. Baseline
        2. Aptitude +10
        3. Projects +1
        4. Soft Skills +0.5
        5. Workshops/Certifications +1
        6. Placement Training -> Yes (if No)
        7. Combined Key Improvements (Aptitude +10, Projects +1, Soft Skills +0.5)
        """
        baseline_res = self.predict(raw_input)
        base_prob = baseline_res["placement_probability"]
        clean_input = baseline_res["features_used"]

        scenarios = [
            {
                "Scenario": "Baseline",
                "PlacementProbability": base_prob,
                "NonPlacementProbability": baseline_res["non_placement_probability"],
                "RiskLevel": baseline_res["risk_level"],
                "Change_vs_Baseline_pp": 0.0,
                "Description": "Current student profile without modifications."
            }
        ]

        # Scenario: Aptitude +10
        sim_input = clean_input.copy()
        sim_input["AptitudeTestScore"] = min(100.0, round(float(clean_input["AptitudeTestScore"]) + 10.0, 1))
        res = self.predict(sim_input)
        delta = round((res["placement_probability"] - base_prob) * 100, 2)
        scenarios.append({
            "Scenario": "Aptitude +10",
            "PlacementProbability": res["placement_probability"],
            "NonPlacementProbability": res["non_placement_probability"],
            "RiskLevel": res["risk_level"],
            "Change_vs_Baseline_pp": delta,
            "Description": f"Boost aptitude test score from {clean_input['AptitudeTestScore']} to {sim_input['AptitudeTestScore']}."
        })

        # Scenario: Projects +1
        sim_input = clean_input.copy()
        sim_input["Projects"] = int(clean_input["Projects"]) + 1
        res = self.predict(sim_input)
        delta = round((res["placement_probability"] - base_prob) * 100, 2)
        scenarios.append({
            "Scenario": "Projects +1",
            "PlacementProbability": res["placement_probability"],
            "NonPlacementProbability": res["non_placement_probability"],
            "RiskLevel": res["risk_level"],
            "Change_vs_Baseline_pp": delta,
            "Description": f"Complete 1 additional project ({clean_input['Projects']} → {sim_input['Projects']})."
        })

        # Scenario: Soft Skills +0.5
        sim_input = clean_input.copy()
        sim_input["SoftSkillsRating"] = min(5.0, round(float(clean_input["SoftSkillsRating"]) + 0.5, 2))
        res = self.predict(sim_input)
        delta = round((res["placement_probability"] - base_prob) * 100, 2)
        scenarios.append({
            "Scenario": "Soft Skills +0.5",
            "PlacementProbability": res["placement_probability"],
            "NonPlacementProbability": res["non_placement_probability"],
            "RiskLevel": res["risk_level"],
            "Change_vs_Baseline_pp": delta,
            "Description": f"Enhance soft skills rating from {clean_input['SoftSkillsRating']} to {sim_input['SoftSkillsRating']}."
        })

        # Scenario: Workshops/Certifications +1
        sim_input = clean_input.copy()
        sim_input["Workshops/Certifications"] = int(clean_input["Workshops/Certifications"]) + 1
        res = self.predict(sim_input)
        delta = round((res["placement_probability"] - base_prob) * 100, 2)
        scenarios.append({
            "Scenario": "Certifications +1",
            "PlacementProbability": res["placement_probability"],
            "NonPlacementProbability": res["non_placement_probability"],
            "RiskLevel": res["risk_level"],
            "Change_vs_Baseline_pp": delta,
            "Description": f"Complete 1 industry certification ({clean_input['Workshops/Certifications']} → {sim_input['Workshops/Certifications']})."
        })

        # Scenario: Placement Training -> Yes (if currently No)
        if clean_input.get("PlacementTraining") == "No":
            sim_input = clean_input.copy()
            sim_input["PlacementTraining"] = "Yes"
            res = self.predict(sim_input)
            delta = round((res["placement_probability"] - base_prob) * 100, 2)
            scenarios.append({
                "Scenario": "Enroll in Placement Training",
                "PlacementProbability": res["placement_probability"],
                "NonPlacementProbability": res["non_placement_probability"],
                "RiskLevel": res["risk_level"],
                "Change_vs_Baseline_pp": delta,
                "Description": "Enroll and actively participate in campus placement training."
            })

        # Scenario: All Improvements Combined
        sim_input = clean_input.copy()
        sim_input["AptitudeTestScore"] = min(100.0, round(float(clean_input["AptitudeTestScore"]) + 10.0, 1))
        sim_input["Projects"] = int(clean_input["Projects"]) + 1
        sim_input["SoftSkillsRating"] = min(5.0, round(float(clean_input["SoftSkillsRating"]) + 0.5, 2))
        sim_input["Workshops/Certifications"] = int(clean_input["Workshops/Certifications"]) + 1
        sim_input["PlacementTraining"] = "Yes"
        res = self.predict(sim_input)
        delta = round((res["placement_probability"] - base_prob) * 100, 2)
        scenarios.append({
            "Scenario": "Combined Growth Package",
            "PlacementProbability": res["placement_probability"],
            "NonPlacementProbability": res["non_placement_probability"],
            "RiskLevel": res["risk_level"],
            "Change_vs_Baseline_pp": delta,
            "Description": "Simultaneous focus on Aptitude (+10), Project (+1), Soft Skills (+0.5), Cert (+1), and Training."
        })

        return scenarios

    def generate_career_recommendations(self, raw_input: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates personalized career recommendations matching reports/career_recommendations_demo.csv,
        comparing against placed student averages and calculating exact probability boosts.
        """
        baseline_res = self.predict(raw_input)
        base_prob = baseline_res["placement_probability"]
        clean = baseline_res["features_used"]

        recommendations = []

        # 1. Aptitude Test Score
        sim_input = clean.copy()
        sim_apt = min(100.0, round(float(clean["AptitudeTestScore"]) + 10.0, 1))
        sim_input["AptitudeTestScore"] = sim_apt
        res = self.predict(sim_input)
        delta = round((res["placement_probability"] - base_prob) * 100, 2)
        recommendations.append({
            "Feature": "AptitudeTestScore",
            "Recommendation": "Aptitude preparation",
            "Suggested_Action": "Practice quantitative aptitude, logical reasoning, and timed mock tests regularly.",
            "Current_Value": float(clean["AptitudeTestScore"]),
            "Simulated_Value": sim_apt,
            "Benchmark_Placed_Avg": self.benchmarks.get("AptitudeTestScore", 84.42),
            "Placement_Probability_Change_pp": delta,
            "Simulated_Risk": res["risk_level"]
        })

        # 2. Projects
        sim_input = clean.copy()
        sim_proj = int(clean["Projects"]) + 1
        sim_input["Projects"] = sim_proj
        res = self.predict(sim_input)
        delta = round((res["placement_probability"] - base_prob) * 100, 2)
        recommendations.append({
            "Feature": "Projects",
            "Recommendation": "Practical project experience",
            "Suggested_Action": "Complete a well-documented project and be prepared to explain its design, implementation, and results.",
            "Current_Value": float(clean["Projects"]),
            "Simulated_Value": float(sim_proj),
            "Benchmark_Placed_Avg": self.benchmarks.get("Projects", 2.50),
            "Placement_Probability_Change_pp": delta,
            "Simulated_Risk": res["risk_level"]
        })

        # 3. Soft Skills
        sim_input = clean.copy()
        sim_soft = min(5.0, round(float(clean["SoftSkillsRating"]) + 0.5, 2))
        sim_input["SoftSkillsRating"] = sim_soft
        res = self.predict(sim_input)
        delta = round((res["placement_probability"] - base_prob) * 100, 2)
        recommendations.append({
            "Feature": "SoftSkillsRating",
            "Recommendation": "Communication and interview skills",
            "Suggested_Action": "Practice mock interviews, structured answers, presentations, and clear technical explanations.",
            "Current_Value": float(clean["SoftSkillsRating"]),
            "Simulated_Value": sim_soft,
            "Benchmark_Placed_Avg": self.benchmarks.get("SoftSkillsRating", 4.52),
            "Placement_Probability_Change_pp": delta,
            "Simulated_Risk": res["risk_level"]
        })

        # 4. Workshops/Certifications
        sim_input = clean.copy()
        sim_cert = int(clean["Workshops/Certifications"]) + 1
        sim_input["Workshops/Certifications"] = sim_cert
        res = self.predict(sim_input)
        delta = round((res["placement_probability"] - base_prob) * 100, 2)
        recommendations.append({
            "Feature": "Workshops/Certifications",
            "Recommendation": "Relevant workshops or certifications",
            "Suggested_Action": "Consider a relevant course or certification that supports your target role and demonstrates practical skills.",
            "Current_Value": float(clean["Workshops/Certifications"]),
            "Simulated_Value": float(sim_cert),
            "Benchmark_Placed_Avg": self.benchmarks.get("Workshops/Certifications", 1.39),
            "Placement_Probability_Change_pp": delta,
            "Simulated_Risk": res["risk_level"]
        })

        # 5. Internships
        sim_input = clean.copy()
        sim_intern = int(clean["Internships"]) + 1
        sim_input["Internships"] = sim_intern
        res = self.predict(sim_input)
        delta = round((res["placement_probability"] - base_prob) * 100, 2)
        recommendations.append({
            "Feature": "Internships",
            "Recommendation": "Relevant internship experience",
            "Suggested_Action": "Explore internships, supervised projects, or practical experience aligned with your career goals.",
            "Current_Value": float(clean["Internships"]),
            "Simulated_Value": float(sim_intern),
            "Benchmark_Placed_Avg": self.benchmarks.get("Internships", 1.24),
            "Placement_Probability_Change_pp": delta,
            "Simulated_Risk": res["risk_level"]
        })

        # Sort recommendations by highest placement probability change (descending)
        recommendations.sort(key=lambda x: x["Placement_Probability_Change_pp"], reverse=True)
        return recommendations


# Standalone Self-Test
if __name__ == "__main__":
    print("=" * 60)
    print("SMART PLACEMENT PREDICTOR: STANDALONE ENGINE TEST")
    print("=" * 60)

    try:
        predictor = PlacementPredictor()
        print("[SUCCESS] Loaded metadata and model successfully!")
        print(f"Model Name: {predictor.metadata.get('model_name')}")
        print(f"Target: {predictor.metadata.get('target')}")
        print(f"Features ({len(predictor.features)}): {predictor.features}")
        print(f"Risk Thresholds: {predictor.risk_thresholds}")

        # Sample student from test_clean.csv Row 1 (actual label: NotPlaced)
        sample_student = {
            "CGPA": 7.7,
            "Internships": 1,
            "Projects": 1,
            "Workshops/Certifications": 0,
            "AptitudeTestScore": 69,
            "SoftSkillsRating": 4.0,
            "ExtracurricularActivities": "No",
            "PlacementTraining": "No",
            "SSC_Marks": 55,
            "HSC_Marks": 69
        }

        print("\n--- Running Baseline Prediction on Sample Student ---")
        pred_res = predictor.predict(sample_student)
        print(f"Predicted Status       : {pred_res['prediction']}")
        print(f"Placement Probability  : {pred_res['placement_probability']} ({pred_res['placement_percentage']}%)")
        print(f"Non-Placement Prob     : {pred_res['non_placement_probability']}")
        print(f"Placement Risk Level   : {pred_res['risk_level']} (Risk Score: {pred_res['risk_score']})")

        print("\n--- Running What-If Scenarios ---")
        scenarios = predictor.simulate_what_if_scenarios(sample_student)
        for s in scenarios:
            print(f"  • {s['Scenario']:<28} | Prob: {s['PlacementProbability']:.4f} | Risk: {s['RiskLevel']:<6} | Delta: {s['Change_vs_Baseline_pp']:+5.2f} pp")

        print("\n--- Running Career Recommendations ---")
        recs = predictor.generate_career_recommendations(sample_student)
        for r in recs:
            print(f"  • {r['Feature']:<24}: {r['Current_Value']} -> {r['Simulated_Value']} | Boost: +{r['Placement_Probability_Change_pp']:.2f} pp | {r['Recommendation']}")

        print("\n" + "=" * 60)
        print("[ALL TESTS COMPLETED SUCCESSFULLY]")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] An error occurred during self-test: {e}")
        import traceback
        traceback.print_exc()
