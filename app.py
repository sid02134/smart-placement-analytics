"""
Smart Placement Prediction & Career Analytics System
Flask Backend API & Web Application
"""

import os
import json
import pandas as pd
from flask import Flask, request, jsonify, render_template, send_from_directory
from predictor import PlacementPredictor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
FIGURES_DIR = os.path.join(REPORTS_DIR, "figures")

app = Flask(__name__, template_folder="templates", static_folder="static")

# Initialize Predictor instance reusing placement_model.joblib and model_metadata.json
try:
    predictor = PlacementPredictor()
    model_loaded = True
    init_error = None
except Exception as e:
    predictor = None
    model_loaded = False
    init_error = str(e)


# -------------------------------------------------------------------------
# Web Page Route
# -------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    """Serves the main Smart Placement Analytics web dashboard."""
    return render_template("index.html")


# -------------------------------------------------------------------------
# Static File Routes for Analytical Reports & Figures
# -------------------------------------------------------------------------
@app.route("/reports/figures/<path:filename>")
def serve_figure(filename):
    """Serves pre-generated EDA figure images."""
    return send_from_directory(FIGURES_DIR, filename)


@app.route("/reports/<path:filename>")
def serve_report_file(filename):
    """Serves report images and artifacts."""
    return send_from_directory(REPORTS_DIR, filename)


# -------------------------------------------------------------------------
# REST API Endpoints
# -------------------------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint confirming API status and model load state."""
    if not model_loaded:
        return jsonify({
            "status": "unhealthy",
            "model_loaded": False,
            "error": init_error
        }), 500

    return jsonify({
        "status": "healthy",
        "model_loaded": True,
        "model_name": predictor.metadata.get("model_name"),
        "positive_class": predictor.metadata.get("positive_class_label", "Placed"),
        "expected_features_count": len(predictor.features),
        "expected_features": predictor.features,
        "risk_thresholds": predictor.risk_thresholds
    }), 200


@app.route("/api/predict", methods=["POST"])
def predict():
    """
    Accepts all 10 student features and returns:
    - predicted placement status ('Placed' or 'NotPlaced')
    - placement probability
    - non-placement probability
    - risk score and risk level ('Low', 'Medium', 'High')
    """
    if not model_loaded:
        return jsonify({"status": "error", "error": "Model is not loaded."}), 500

    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({
            "status": "fail",
            "error": "Invalid request body. Expected a valid JSON object containing student features."
        }), 400

    try:
        result = predictor.predict(data)
        return jsonify({
            "status": "success",
            "prediction": result["prediction"],
            "predicted_class": result["predicted_class"],
            "placement_probability": result["placement_probability"],
            "non_placement_probability": result["non_placement_probability"],
            "placement_percentage": result["placement_percentage"],
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "features_used": result["features_used"]
        }), 200
    except ValueError as ve:
        return jsonify({
            "status": "fail",
            "error": str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"Prediction failed: {str(e)}"
        }), 500


@app.route("/api/what-if", methods=["POST"])
def what_if():
    """
    Accepts student features and returns what-if scenario simulations
    comparing baseline against incremental skill, aptitude, and experience improvements.
    """
    if not model_loaded:
        return jsonify({"status": "error", "error": "Model is not loaded."}), 500

    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({
            "status": "fail",
            "error": "Invalid request body. Expected a valid JSON object containing student features."
        }), 400

    try:
        scenarios = predictor.simulate_what_if_scenarios(data)
        return jsonify({
            "status": "success",
            "total_scenarios": len(scenarios),
            "scenarios": scenarios
        }), 200
    except ValueError as ve:
        return jsonify({
            "status": "fail",
            "error": str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"What-if simulation failed: {str(e)}"
        }), 500


@app.route("/api/recommendations", methods=["POST"])
def recommendations():
    """
    Accepts student features and returns tailored, prioritized career improvement
    recommendations benchmarked against successfully placed students.
    """
    if not model_loaded:
        return jsonify({"status": "error", "error": "Model is not loaded."}), 500

    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({
            "status": "fail",
            "error": "Invalid request body. Expected a valid JSON object containing student features."
        }), 400

    try:
        recs = predictor.generate_career_recommendations(data)
        return jsonify({
            "status": "success",
            "total_recommendations": len(recs),
            "recommendations": recs
        }), 200
    except ValueError as ve:
        return jsonify({
            "status": "fail",
            "error": str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"Recommendation generation failed: {str(e)}"
        }), 500


@app.route("/api/analytics-data", methods=["GET"])
def analytics_data():
    """
    Loads and serves genuine analytical data directly from existing project reports:
    - EDA summary statistics
    - Model comparison metrics (10 models)
    - SHAP feature importances
    - Historical feature benchmarks (Placed vs NotPlaced)
    - Risk distribution
    """
    try:
        data_payload = {}

        # 1. EDA Summary
        eda_path = os.path.join(REPORTS_DIR, "phase1_eda_summary.json")
        if os.path.exists(eda_path):
            with open(eda_path, "r", encoding="utf-8") as f:
                data_payload["eda_summary"] = json.load(f)

        # 2. All Models Validation
        all_models_path = os.path.join(REPORTS_DIR, "all_models_validation.csv")
        if os.path.exists(all_models_path):
            df_models = pd.read_csv(all_models_path)
            data_payload["model_comparisons"] = df_models.to_dict(orient="records")

        # 3. Tuned Models
        tuned_path = os.path.join(REPORTS_DIR, "tuned_models_validation.csv")
        if os.path.exists(tuned_path):
            df_tuned = pd.read_csv(tuned_path)
            data_payload["tuned_models"] = df_tuned.to_dict(orient="records")

        # 4. SHAP Feature Importance
        shap_path = os.path.join(REPORTS_DIR, "shap_feature_importance.csv")
        if os.path.exists(shap_path):
            df_shap = pd.read_csv(shap_path)
            data_payload["shap_importance"] = df_shap.to_dict(orient="records")

        # 5. Placement Feature Comparison (Placed vs NotPlaced averages)
        comp_path = os.path.join(REPORTS_DIR, "placement_comparison.csv")
        if os.path.exists(comp_path):
            df_comp = pd.read_csv(comp_path)
            data_payload["placement_comparison"] = df_comp.to_dict(orient="records")

        # 6. Placement Risk Distribution
        risk_path = os.path.join(REPORTS_DIR, "placement_risk_summary.csv")
        if os.path.exists(risk_path):
            df_risk = pd.read_csv(risk_path)
            data_payload["risk_summary"] = df_risk.to_dict(orient="records")

        # 7. Cross Validation Results
        cv_path = os.path.join(REPORTS_DIR, "cross_validation_results.csv")
        if os.path.exists(cv_path):
            df_cv = pd.read_csv(cv_path)
            data_payload["cross_validation"] = df_cv.to_dict(orient="records")

        return jsonify({
            "status": "success",
            "data": data_payload
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"Failed to load analytics data: {str(e)}"
        }), 500


@app.route("/api/sample-profiles", methods=["GET"])
def sample_profiles():
    """Returns verified student test profiles for 1-click loading."""
    profiles = {
        "at_risk": {
            "name": "High Risk Profile (Row 1 of Test Set)",
            "data": {
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
        },
        "placed": {
            "name": "Strong Placement Profile (Row 2 of Test Set)",
            "data": {
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
        },
        "borderline": {
            "name": "Moderate / Borderline Profile (Row 22 of Test Set)",
            "data": {
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
        }
    }
    return jsonify({"status": "success", "profiles": profiles}), 200


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"status": "fail", "error": "Resource or endpoint not found."}), 404
    return render_template("index.html"), 200


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"status": "fail", "error": "HTTP method not allowed for this endpoint."}), 405


@app.errorhandler(500)
def server_error(e):
    return jsonify({"status": "error", "error": "Internal server error."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting SmartPlacementAnalytics API on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)
