"""
engine/diseases.py
Master definitions for all 5 disease profiles.
Each disease includes: icon, theme colour, description, symptom→weight mapping,
and risk thresholds (percentages 0-100).
"""

DISEASES: dict = {

    # ── Diabetes ──────────────────────────────────────────────────────────────
    "Diabetes": {
        "icon":        "🩺",
        "color":       "#FF6B6B",
        "gradient":    "linear-gradient(135deg,#FF6B6B,#FF8E53)",
        "description": (
            "A chronic metabolic condition in which the body cannot properly "
            "regulate blood glucose, either due to insufficient insulin "
            "production (Type 1) or insulin resistance (Type 2)."
        ),
        "symptoms": {
            "Frequent urination":            15,
            "Excessive thirst":              14,
            "Unexplained weight loss":       13,
            "Extreme fatigue":               12,
            "Blurred vision":                11,
            "Slow-healing sores or wounds":  10,
            "Frequent infections":           10,
            "Tingling or numbness (hands/feet)": 9,
            "Increased hunger":               8,
            "Darkened skin patches (neck/armpits)": 7,
            "Dry mouth":                      6,
            "Nausea or vomiting":             5,
        },
        "thresholds": {"Low": 20, "Medium": 40, "High": 65, "Critical": 85},
    },

    # ── Heart Disease ─────────────────────────────────────────────────────────
    "Heart Disease": {
        "icon":        "❤️",
        "color":       "#FF4757",
        "gradient":    "linear-gradient(135deg,#FF4757,#C0392B)",
        "description": (
            "A range of conditions that affect the heart's structure and "
            "function, including coronary artery disease, arrhythmias, "
            "and heart failure."
        ),
        "symptoms": {
            "Chest pain or pressure":           20,
            "Shortness of breath (at rest)":    17,
            "Pain radiating to arm or jaw":     16,
            "Irregular or rapid heartbeat":     14,
            "Extreme fatigue":                  13,
            "Dizziness or lightheadedness":     12,
            "Swelling in legs or ankles":       10,
            "Cold sweats":                       9,
            "Nausea":                            7,
            "Reduced exercise tolerance":        6,
        },
        "thresholds": {"Low": 20, "Medium": 40, "High": 65, "Critical": 85},
    },

    # ── Hypertension ─────────────────────────────────────────────────────────
    "Hypertension": {
        "icon":        "🫀",
        "color":       "#FF7F50",
        "gradient":    "linear-gradient(135deg,#FF7F50,#E74C3C)",
        "description": (
            "Persistently elevated arterial blood pressure (≥130/80 mmHg). "
            "Often called the 'silent killer' because it may show no "
            "obvious symptoms until serious damage occurs."
        ),
        "symptoms": {
            "Severe headache":                  18,
            "Blurred or double vision":         15,
            "Nosebleeds without cause":         14,
            "Shortness of breath":              13,
            "Chest discomfort":                 12,
            "Dizziness":                        11,
            "Pounding sensation (chest/ears)":  10,
            "Fatigue or confusion":              9,
            "Blood in urine":                    8,
            "Flushing of face":                  6,
            "Anxiety or nervousness":            5,
        },
        "thresholds": {"Low": 18, "Medium": 38, "High": 60, "Critical": 80},
    },

    # ── Asthma ────────────────────────────────────────────────────────────────
    "Asthma": {
        "icon":        "🫁",
        "color":       "#5352ED",
        "gradient":    "linear-gradient(135deg,#5352ED,#3742FA)",
        "description": (
            "A chronic inflammatory disease of the airways that causes "
            "recurrent episodes of wheezing, breathlessness, chest tightness, "
            "and coughing, often triggered by allergens or exercise."
        ),
        "symptoms": {
            "Wheezing (whistling sound when breathing)": 18,
            "Shortness of breath":                      17,
            "Chest tightness":                          15,
            "Persistent dry cough":                     14,
            "Cough worse at night or early morning":    13,
            "Breathlessness during exercise":           12,
            "Coughing after physical activity":         10,
            "Difficulty sleeping due to cough":          9,
            "Rapid or noisy breathing":                  8,
            "Mucus or phlegm production":                7,
            "Symptoms triggered by cold air":            6,
        },
        "thresholds": {"Low": 18, "Medium": 38, "High": 60, "Critical": 80},
    },

    # ── Typhoid ───────────────────────────────────────────────────────────────
    "Typhoid": {
        "icon":        "🌡️",
        "color":       "#2ED573",
        "gradient":    "linear-gradient(135deg,#2ED573,#1E9E58)",
        "description": (
            "A systemic bacterial infection caused by Salmonella typhi, "
            "typically spread through contaminated food or water. "
            "Common in areas with poor sanitation."
        ),
        "symptoms": {
            "High fever (above 103°F / 39.4°C)":      18,
            "Sustained fever lasting several days":    16,
            "Abdominal pain or cramps":                14,
            "Severe headache":                         13,
            "Weakness and fatigue":                    12,
            "Rose-coloured spots on skin (trunk)":     11,
            "Loss of appetite":                        10,
            "Nausea":                                   9,
            "Diarrhoea or constipation":                9,
            "Muscle aches and body pain":               7,
            "Dry cough":                                6,
            "Profuse sweating":                         5,
        },
        "thresholds": {"Low": 18, "Medium": 38, "High": 60, "Critical": 80},
    },
# ── COVID-19 ──────────────────────────────────────────────────────────────
    "COVID-19": {
        "icon":        "🦠",
        "color":       "rgba(168,85,247,1)",
        "gradient":    "linear-gradient(135deg,#A855F7,#7E22CE)",
        "description": (
            "A highly contagious respiratory illness caused by the SARS-CoV-2 virus. "
            "Symptoms can range from mild to severe and can appear 2-14 days after exposure."
        ),
        "symptoms": {
            "Fever or chills":                       15,
            "Cough":                                 14,
            "Shortness of breath or difficulty breathing": 18,
            "Fatigue":                               10,
            "Muscle or body aches":                  9,
            "New loss of taste or smell":            16,
            "Sore throat":                           8,
            "Congestion or runny nose":              6,
            "Nausea or vomiting":                    5,
            "Diarrhea":                              5,
            "Persistent pain or pressure in the chest": 20, # Red flag symptom
        },
        "thresholds": {"Low": 25, "Medium": 45, "High": 65, "Critical": 85},
    },
}
