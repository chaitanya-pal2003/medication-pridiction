"""
views/home.py
Advanced Analytics Dashboard — Visual charts, stats, and quick navigation.
"""
import streamlit as st
import pandas as pd
from db_connector import execute_query
from datetime import datetime

def show_home() -> None:
    user_name = st.session_state.get("user_name", "User")
    user_email = st.session_state.get("user_email")

    # ── Greeting ────────────────────────────────────────────────────────────
    hour     = datetime.now().hour
    greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")

    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-title">🏥 MedPredict AI Dashboard</div>
        <p class="hero-subtitle">
            {greeting}, <strong style="color:#EEF2FF">{user_name}</strong>! 
            Here is your personal health analytics overview.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Fetch stats with Caching for Performance ─────────────────────────────
    @st.cache_data(ttl=60)
    def get_dashboard_data(email):
        if not email:
            return pd.DataFrame()
        rows = execute_query("SELECT disease, risk_level, created_at FROM history WHERE user_email = %s", (email,),
                             fetch=True)
        return pd.DataFrame(rows)

    df = get_dashboard_data(user_email)

    # ── Top Level Metrics ───────────────────────────────────────────────────
    total_tests = len(df)
    high_risks = len(df[df['risk_level'].str.contains('High|Critical', na=False, case=False)]) if not df.empty else 0

    m1, m2, m3 = st.columns(3)
    m1.metric(label="Total Assessments", value=total_tests)
    m2.metric(label="High/Critical Alerts", value=high_risks, delta_color="inverse")

    with m3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔬 Start New Prediction", type="primary", use_container_width=True):
            st.session_state["current_page"] = "predict"
            st.rerun()

    st.markdown("---")

    # ── Interactive Charts ──────────────────────────────────────────────────
    if not df.empty:
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("📊 Tests by Disease")
            disease_counts = df['disease'].value_counts()
            st.bar_chart(disease_counts, color="#8352FD")

        with c2:
            st.subheader("📈 Risk Level Distribution")
            risk_counts = df['risk_level'].value_counts()
            st.bar_chart(risk_counts, color="#00D4FF")

        st.subheader("⏱️ Recent Activity")
        display_df = df.sort_values(by="created_at", ascending=False).head(5)
        st.dataframe(
            display_df,
            column_config={
                "disease": "Disease Assessed",
                "risk_level": "Risk Level",
                "created_at": st.column_config.DatetimeColumn("Date & Time", format="D MMM YYYY, h:mm a")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("👋 You haven't taken any health assessments yet. Click 'Start New Prediction' to begin!")