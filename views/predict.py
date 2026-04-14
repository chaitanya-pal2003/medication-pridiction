"""
views/predict.py
Dynamic Prediction module reading diseases and symptoms from MySQL.
"""
import streamlit as st
import json
from db_connector import get_connection

def show_predict() -> None:
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">🔬 AI Disease Predictor</h2>
        <span class="section-badge">Symptom Analysis</span>
    </div>
    <br>
    """, unsafe_allow_html=True)

    # 1. Fetch available diseases from Database
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, icon FROM diseases")
        diseases = cursor.fetchall()
    except Exception as e:
        st.error(f"Database Error: {e}")
        return

    if not diseases:
        st.warning("⚠️ No diseases found in the database. Please ask an Admin to add diseases via the Admin Panel.")
        return

    # Create mapping for the selectbox
    disease_options = {f"{d['icon']} {d['name']}": d['id'] for d in diseases}

    st.write("### Step 1: Select Target Disease Profile")
    selected_disease_label = st.selectbox("Choose the condition you want to check for:", list(disease_options.keys()))
    selected_disease_id = disease_options[selected_disease_label]
    selected_disease_name = selected_disease_label.split(" ", 1)[1] # Extract name without icon

    st.markdown("---")

    # 2. Fetch symptoms for the selected disease
    cursor.execute("SELECT symptom_name, weight FROM symptoms WHERE disease_id = %s", (selected_disease_id,))
    symptoms = cursor.fetchall()

    if not symptoms:
        st.info(f"No symptoms have been mapped to {selected_disease_name} yet.")
        return

    symptom_names = [s['symptom_name'] for s in symptoms]
    symptom_weights = {s['symptom_name']: s['weight'] for s in symptoms}

    st.write(f"### Step 2: Select Your Symptoms for {selected_disease_name}")
    selected_symptoms = st.multiselect(
        "Select all symptoms you are currently experiencing:",
        options=symptom_names
    )

    if st.button("🔮 Analyze Symptoms", type="primary", use_container_width=True):
        if not selected_symptoms:
            st.error("Please select at least one symptom to analyze.")
            return

        with st.spinner("Analyzing symptoms using Google Gemini AI..."):
            # Calculate Risk Score
            total_score = sum([symptom_weights[sym] for sym in selected_symptoms])

            # Simple risk logic (You can make this dynamic later too!)
            if total_score >= 10:
                risk_level = "High Risk"
            elif total_score >= 5:
                risk_level = "Moderate Risk"
            else:
                risk_level = "Low Risk"

            # -------------------------------------------------------------
            # 🤖 AI INTEGRATION POINT:
            # CALL YOUR EXISTING GEMINI AI FUNCTION HERE.
            # Example: ai_response = my_ai_function(selected_disease_name, selected_symptoms, risk_level)
            # -------------------------------------------------------------

            # Placeholder AI text (Replace this with your actual Gemini call)
            ai_response = f"Based on your symptoms ({', '.join(selected_symptoms)}), the calculated risk level for {selected_disease_name} is **{risk_level}**. Please consult a doctor for a formal diagnosis."

            # Save to Database History
            try:
                user_email = st.session_state.get("user_email", "guest@medpredict.com")
                symptoms_json = json.dumps(selected_symptoms)

                cursor.execute("""
                    INSERT INTO history (user_email, disease, risk_level, symptoms, ai_response) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_email, selected_disease_name, risk_level, symptoms_json, ai_response))
                conn.commit()
            except Exception as e:
                st.error(f"Failed to save history: {e}")

            # Display Results
            st.success("Analysis Complete!")
            st.markdown(f"""
            <div class="result-card">
                <h3>Analysis Results: {selected_disease_name}</h3>
                <h4 style="color: {'#FF4D4F' if risk_level == 'High Risk' else '#FFA940' if risk_level == 'Moderate Risk' else '#2ED573'};">{risk_level}</h4>
                <p><strong>Symptoms reported:</strong> {', '.join(selected_symptoms)}</p>
                <hr>
                <p><strong>🤖 AI Insight:</strong></p>
                <p>{ai_response}</p>
            </div>
            """, unsafe_allow_html=True)

    conn.close()