"""
views/predict.py
Dynamic Prediction module using Gemini AI for symptom analysis.
"""
import streamlit as st
import json
from db_connector import get_connection
from ai.gemini_advisor import analyze_symptoms_with_ai

def show_predict() -> None:
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">🔬 AI Disease Predictor</h2>
        <span class="section-badge">Symptom Analysis</span>
    </div>
    <br>
    """, unsafe_allow_html=True)

    st.write("### Describe Your Symptoms")
    st.info("Please describe how you are feeling in detail. Include any pain, discomfort, fever, or unusual symptoms you've noticed recently.")
    
    symptoms_text = st.text_area(
        "Enter your symptoms here:",
        placeholder="e.g., I have had a severe headache since yesterday, feeling a bit nauseous, and my throat hurts...",
        height=150
    )

    if st.button("🔮 Analyze Symptoms", type="primary", use_container_width=True):
        if not symptoms_text or len(symptoms_text.strip()) < 5:
            st.error("Please provide a more detailed description of your symptoms to analyze.")
            return

        with st.spinner("Analyzing symptoms using Google Gemini AI..."):
            
            # Call AI function
            ai_result = analyze_symptoms_with_ai(symptoms_text)
            
            # Extract results
            predicted_disease = ai_result.get("disease", "Unknown")
            risk_level = ai_result.get("risk_level", "Unknown")
            explanation = ai_result.get("explanation", "No explanation provided.")

            # Save to Database History
            try:
                conn = get_connection()
                cursor = conn.cursor()
                user_email = st.session_state.get("user_email", "guest@medpredict.com")
                
                # We save the raw symptoms text they typed
                cursor.execute("""
                    INSERT INTO history (user_email, disease, risk_level, symptoms, ai_response) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_email, predicted_disease, risk_level, symptoms_text, explanation))
                conn.commit()
                cursor.close()
                conn.close()
            except Exception as e:
                st.error(f"Failed to save history: {e}")

            # Display Results
            st.success("Analysis Complete!")
            
            # Determine color based on risk level
            risk_lower = risk_level.lower()
            if "high" in risk_lower or "critical" in risk_lower:
                risk_color = "#FF4D4F" # Red
            elif "moderate" in risk_lower or "medium" in risk_lower:
                risk_color = "#FFA940" # Orange
            elif "low" in risk_lower:
                risk_color = "#2ED573" # Green
            else:
                risk_color = "#888888" # Grey

            st.markdown(f"""
            <div class="result-card">
                <h3>Predicted Condition: {predicted_disease}</h3>
                <h4 style="color: {risk_color};">Risk Level: {risk_level}</h4>
                <p><strong>Your reported symptoms:</strong><br/> <i>{symptoms_text}</i></p>
                <hr>
                <p><strong>🤖 AI Insight & Recommendations:</strong></p>
                <p style="white-space: pre-wrap;">{explanation}</p>
            </div>
            """, unsafe_allow_html=True)