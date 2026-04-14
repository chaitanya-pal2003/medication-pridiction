"""
engine/symptom_engine.py
Rule-based weighted symptom scoring engine.
"""
from engine.diseases import DISEASES


# Risk level metadata
_RISK_META = {
    "Low":      {"color": "#2ED573", "bg": "rgba(46,213,115,0.12)",  "border": "rgba(46,213,115,0.3)",  "emoji": "✅"},
    "Medium":   {"color": "#FFA940", "bg": "rgba(255,169,64,0.12)",  "border": "rgba(255,169,64,0.3)",  "emoji": "⚠️"},
    "High":     {"color": "#FF6347", "bg": "rgba(255,99,71,0.12)",   "border": "rgba(255,99,71,0.3)",   "emoji": "🔴"},
    "Critical": {"color": "#FF4D4F", "bg": "rgba(255,77,79,0.12)",   "border": "rgba(255,77,79,0.3)",   "emoji": "🚨"},
}

_ADVICE = {
    "Low":      "Your risk is low. Maintain a healthy lifestyle, stay hydrated, and monitor any changes in your symptoms.",
    "Medium":   "Moderate risk detected. Monitor your symptoms closely and consider consulting a healthcare provider within a few days.",
    "High":     "High risk identified. Please schedule an appointment with a doctor as soon as possible.",
    "Critical": "Critical risk! Seek emergency medical attention immediately — do not delay.",
}


def predict_disease(disease_name: str, selected_symptoms: list[str]) -> dict:
    """
    Score the given symptoms against the disease profile and return a
    comprehensive result dict.

    Returns:
        dict with keys: disease, score, risk_level, risk_color, risk_bg,
                        risk_border, risk_emoji, advice, matched_symptoms,
                        matched_count, total_symptoms, max_possible, raw_score
    """
    disease = DISEASES.get(disease_name)
    if not disease:
        raise ValueError(f"Unknown disease: {disease_name!r}")

    symptom_weights = disease["symptoms"]
    max_possible    = sum(symptom_weights.values())
    raw_score       = sum(symptom_weights.get(s, 0) for s in selected_symptoms)

    # Normalise to 0-100
    normalized = round((raw_score / max_possible) * 100, 1) if max_possible > 0 else 0.0

    # Determine risk level
    thresholds = disease["thresholds"]
    if normalized >= thresholds["Critical"]:
        risk_level = "Critical"
    elif normalized >= thresholds["High"]:
        risk_level = "High"
    elif normalized >= thresholds["Medium"]:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    meta = _RISK_META[risk_level]

    return {
        "disease":          disease_name,
        "score":            normalized,
        "raw_score":        raw_score,
        "max_possible":     max_possible,
        "risk_level":       risk_level,
        "risk_color":       meta["color"],
        "risk_bg":          meta["bg"],
        "risk_border":      meta["border"],
        "risk_emoji":       meta["emoji"],
        "advice":           _ADVICE[risk_level],
        "matched_symptoms": selected_symptoms,
        "matched_count":    len(selected_symptoms),
        "total_symptoms":   len(symptom_weights),
        "disease_color":    disease["color"],
        "disease_icon":     disease["icon"],
    }
