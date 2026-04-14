"""
views/about.py
Dynamic About page reading directly from the MySQL CMS.
"""
import streamlit as st
from db_connector import get_connection

def show_about() -> None:
    # ── Fetch Dynamic Data from Database ─────────────────────────────────────
    about_text = "MedPredict AI is an intelligent disease prediction system."
    diseases_info = []

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch About Page Text
        cursor.execute("SELECT content FROM app_content WHERE section_name = 'about_purpose'")
        res = cursor.fetchone()
        if res:
            about_text = res['content']

        # Fetch Dynamic Diseases for the Cards
        cursor.execute("SELECT name, icon, description FROM diseases")
        diseases_info = cursor.fetchall()

        conn.close()
    except Exception as e:
        st.error(f"Database Error: {e}")

    # ── Hero ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-banner" style="text-align:center;">
        <div class="hero-title">🏥 MedPredict AI</div>
        <p class="hero-subtitle" style="margin:0 auto; max-width:600px;">
            Final Year College Project — Disease Prediction System<br>
            <span style="color:#3D4F78; font-size:0.85rem;">
                Streamlit · Python · MySQL · Google Gemini AI
            </span>
        </p>
    </div>
    <br>
    """, unsafe_allow_html=True)

    # ── Overview & Purpose (Dynamic) ────────────────────────────────────────
    st.markdown(f"""
    <div class="result-card">
        <h3 style="color:#EEF2FF; margin-top:0; font-size:1.25rem;">🎯 Purpose & What is this App?</h3>
        <p style="color:#8B9CC8; line-height:1.75; font-size:0.95rem; margin-bottom:1rem;">
            {about_text}
        </p>
    </div>
    <br>
    """, unsafe_allow_html=True)

    # ── Project Credits & Tech Stack ──────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="result-card" style="height:100%;">
            <h3 style="color:#EEF2FF; margin-top:0; font-size:1.15rem;">👨‍💻 Project Credits</h3>
            <p style="color:#8B9CC8; line-height:1.75; font-size:0.9rem; margin:0;">
                <strong>Lead Developer:</strong> Gyan Singh<br>
                <strong>Project Type:</strong> Final Year College Project<br><br>
                This project demonstrates how medical assessment algorithms can be combined with modern Generative AI.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="result-card" style="height:100%;">
            <h3 style="color:#EEF2FF; margin-top:0; font-size:1.15rem;">⚙️ Technology Stack</h3>
            <ul style="color:#8B9CC8; line-height:1.75; font-size:0.9rem; margin:0; padding-left:1.2rem;">
                <li><strong style="color:#EEF2FF">Frontend:</strong> Streamlit (Python)</li>
                <li><strong style="color:#EEF2FF">Database:</strong> MySQL (Dynamic CMS)</li>
                <li><strong style="color:#EEF2FF">AI Engine:</strong> Google Gemini</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Dynamic Disease Profiles ──────────────────────────────────────────────
    st.markdown('<h3 style="color:#EEF2FF; font-size:1.1rem; margin-bottom:1rem;">🔬 Supported Disease Profiles</h3>', unsafe_allow_html=True)

    if not diseases_info:
        st.info("No diseases have been added to the system yet. Admins can add them via the Admin Panel.")
    else:
        # Create columns dynamically (max 5 per row)
        cols = st.columns(min(len(diseases_info), 5))
        for i, d in enumerate(diseases_info):
            col = cols[i % 5]
            with col:
                icon = d['icon'] if d['icon'] else "🦠"
                st.markdown(f"""
                <div class="stat-card" style="padding:1.25rem 0.75rem;">
                    <div style="font-size:2rem; margin-bottom:0.4rem">{icon}</div>
                    <div style="color:#00D4FF; font-weight:700; font-size:0.9rem; margin-bottom:0.3rem">{d['name']}</div>
                    <div style="color:#8B9CC8; font-size:0.72rem; line-height:1.4">{d['description']}</div>
                </div>
                """, unsafe_allow_html=True)

    # ── Disclaimer ────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="margin-top:2rem; padding:1rem 1.5rem; background:rgba(255,169,64,0.07); border:1px solid rgba(255,169,64,0.2); border-radius:12px; text-align:center;">
        ⚠️ <strong style="color:#FFA940">Academic Disclaimer</strong><br>
        <span style="color:#8B9CC8; font-size:0.875rem;">
            MedPredict AI is an academic project. Always consult a healthcare professional for medical advice.
        </span>
    </div>
    """, unsafe_allow_html=True)