"""
ai/gemini_advisor.py
Google Gemini AI integration — streams plain-language health explanations.
"""
from google import genai
from config import GEMINI_API_KEY
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
            model="gemini-2.0-flash",
            contents=prompt,
        )
        for chunk in response:
            yield chunk.text
    except Exception as exc:
        yield f"AI explanation could not be generated. Error: {exc}"