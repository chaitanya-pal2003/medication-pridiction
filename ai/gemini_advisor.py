"""
ai/gemini_advisor.py
Google Gemini AI integration — structure data prediction and plain-language health explanations.
"""
from google import genai
from config import GEMINI_API_KEY
import json
import streamlit as st

def get_ai_explanation_stream(disease: str, risk_level: str, symptoms: list[str], score: float):
    """
    Yields the Gemini response chunk by chunk for a typing effect.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        yield "⚠️ AI Explanation Unavailable.\n\nYour Gemini API key is not configured in the .env file."
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
        client = genai.Client(api_key=GEMINI_API_KEY)
        # We use generate_content_stream to get the typing effect!
        response = client.models.generate_content_stream(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        for chunk in response:
            yield chunk.text
    except Exception as exc:
        yield f"AI explanation could not be generated. Error: {exc}"

def analyze_symptoms_with_ai(symptoms_text: str) -> dict:
    """
    Analyzes raw symptom text and returns a predicted disease, risk level, and explanation in JSON format.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        return {
            "disease": "Unknown",
            "risk_level": "Unknown",
            "explanation": "⚠️ AI Explanation Unavailable. Your Gemini API key is not configured in the .env file."
        }

    prompt = f"""You are a compassionate and expert medical AI diagnostician. A patient has provided the following symptoms:
"{symptoms_text}"

Based on these symptoms, predict the most likely disease or condition and the severity of the risk.
You must return the result as a raw JSON object string WITH NO MARKDOWN FORMATTING OR CODE BLOCKS (do not wrap in ```json ... ```) with exactly these three keys:
- "disease": The name of the most probable disease or condition (e.g., "Migraine", "Asthma", "COVID-19", "Common Cold", "Heart Disease"). Keep it brief.
- "risk_level": Must be exactly one of: "Low Risk", "Moderate Risk", "High Risk", "Critical Risk".
- "explanation": A clear, empathetic explanation covering what this means, possible reasons, recommended next steps, and a strong reminder to immediately consult a real doctor.

JSON format:
{{
  "disease": "Disease Name",
  "risk_level": "Risk Level",
  "explanation": "Explanation text..."
}}"""

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        
        response_text = response.text.strip()
        # Clean markdown code blocks if the model insists on adding them
        if response_text.startswith("```json"):
            response_text = response_text[7:].strip()
        if response_text.endswith("```"):
            response_text = response_text[:-3].strip()
            
        return json.loads(response_text)
    except Exception as exc:
        return {
            "disease": "Prediction Error",
            "risk_level": "Unknown",
            "explanation": f"AI analysis failed. Please try again later. Error: {exc}"
        }