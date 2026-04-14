"""
ai/openai_advisor.py
OpenAI API integration — structure data prediction and plain-language health explanations.
"""
from openai import OpenAI
from config import OPENAI_API_KEY
import json
import streamlit as st

def get_ai_explanation_stream(disease: str, risk_level: str, symptoms: list[str], score: float):
    """
    Yields the OpenAI response chunk by chunk for a typing effect.
    """
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        yield "⚠️ AI Explanation Unavailable.\n\nYour OpenAI API key is not configured in the .env file."
        return

    symptoms_str = ", ".join(symptoms) if symptoms else "none specified"

    prompt = f"""You are a compassionate medical AI assistant. A patient has been assessed for {disease} with a risk score of {score}% ({risk_level} Risk).
Their reported symptoms include: {symptoms_str}.

Please provide a clear, empathetic explanation covering:
1. What This Result Means
2. Possible Reasons for These Symptoms
3. Recommended Next Steps
4. Important Reminder (consult a doctor)

Keep the tone warm and supportive. Use simple language."""

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as exc:
        yield f"AI explanation could not be generated. Error: {exc}"

def analyze_symptoms_with_ai(symptoms_text: str) -> dict:
    """
    Analyzes raw symptom text and returns a predicted disease, risk level, and explanation in JSON format.
    """
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        return {
            "disease": "Unknown",
            "risk_level": "Unknown",
            "explanation": "⚠️ AI Explanation Unavailable. Your OpenAI API key is not configured in the .env file."
        }

    prompt = f"""You are a compassionate and expert medical AI diagnostician. A patient has provided the following symptoms:
"{symptoms_text}"

Based on these symptoms, predict the most likely disease or condition and the severity of the risk.
You must return the result as a raw JSON object string with exactly these three keys:
- "disease": The name of the most probable disease or condition (e.g., "Migraine", "Asthma", "COVID-19", "Common Cold", "Heart Disease"). Keep it brief.
- "risk_level": Must be exactly one of: "Low Risk", "Moderate Risk", "High Risk", "Critical Risk".
- "explanation": A clear, empathetic explanation covering what this means, possible reasons, recommended next steps, and a strong reminder to immediately consult a real doctor.

Make sure the output is pure JSON.
JSON format:
{{
  "disease": "Disease Name",
  "risk_level": "Risk Level",
  "explanation": "Explanation text..."
}}"""

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={ "type": "json_object" },
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.choices[0].message.content.strip()
        return json.loads(response_text)
    except Exception as exc:
        return {
            "disease": "Prediction Error",
            "risk_level": "Unknown",
            "explanation": f"AI analysis failed. Please try again later. Error: {exc}"
        }