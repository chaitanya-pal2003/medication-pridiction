"""
views/history.py
Prediction history page — filter, sort, expand, export.
"""
import json
import streamlit as st
import pandas as pd
from db_connector import execute_query


def show_history() -> None:
    user_email = st.session_state.get("user_email")

    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">📋 Prediction History</h2>
        <span class="section-badge">All Records</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Filters ──────────────────────────────────────────────────────────────
    f1, f2, f3 = st.columns(3)
    with f1:
        disease_f = st.selectbox(
            "Filter by Disease",
            ["All Diseases", "Diabetes", "Heart Disease", "Hypertension", "Asthma", "Typhoid"],
            key="hist_disease",
        )
    with f2:
        risk_f = st.selectbox(
            "Filter by Risk Level",
            ["All Risk Levels", "Low Risk", "Moderate Risk", "High Risk", "Critical"],
            key="hist_risk",
        )
    with f3:
        sort_f = st.selectbox(
            "Sort By",
            ["Newest First", "Oldest First"],
            key="hist_sort",
        )

    # ── Query ─────────────────────────────────────────────────────────────────
    query  = "SELECT * FROM history WHERE user_email = %s"
    params = [user_email]

    if disease_f != "All Diseases":
        query += " AND disease = %s"
        params.append(disease_f)

    if risk_f != "All Risk Levels":
        query += " AND risk_level = %s"
        params.append(risk_f)

    _sort_map = {
        "Newest First":  "created_at DESC",
        "Oldest First":  "created_at ASC"
    }
    query += f" ORDER BY {_sort_map[sort_f]}"

    records = execute_query(query, tuple(params), fetch=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Empty state ───────────────────────────────────────────────────────────
    if not records:
        st.markdown("""
        <div style="text-align:center; padding:4rem; color:#3D4F78;">
            <div style="font-size:4rem; margin-bottom:1rem">📋</div>
            <h3 style="color:#8B9CC8">No records found</h3>
            <p>Try different filters, or make your first prediction on the Predict page!</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Count label ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="color:#8B9CC8; font-size:0.85rem; margin-bottom:1rem;">
        Showing <strong style="color:#EEF2FF">{len(records)}</strong> record(s)
    </div>
    """, unsafe_allow_html=True)

    # ── Records (expandable) ──────────────────────────────────────────────────
    for rec in records:
        rl       = str(rec["risk_level"]).lower().replace(" ", "-")
        try:
            symptoms = json.loads(rec["symptoms"]) if rec["symptoms"] else []
        except:
            symptoms = []

        dt       = rec["created_at"]
        dstr     = dt.strftime("%b %d, %Y  %H:%M") if hasattr(dt, "strftime") else str(dt)[:16]

        with st.expander(
            f"{rec['disease']}  ·  {rec['risk_level']}  ·  {dstr}"
        ):
            left, right = st.columns([1, 2])

            with left:
                st.markdown(f"""
                <div style="text-align:center; padding:1.25rem 0.5rem;">
                    <div style="margin:0.75rem 0;">
                        <span class="risk-badge risk-{rl}">{rec['risk_level']}</span>
                    </div>
                    <div style="color:#3D4F78; font-size:0.78rem; margin-top:0.25rem">{rec['disease']}</div>
                    <div style="color:#3D4F78; font-size:0.72rem; margin-top:0.2rem">{dstr}</div>
                </div>
                """, unsafe_allow_html=True)

            with right:
                chips = "".join(f'<span class="symptom-chip">{s}</span>' for s in symptoms) \
                        if symptoms else '<span style="color:#3D4F78">None recorded</span>'
                st.markdown(f"""
                <div style="margin-bottom:1rem;">
                    <div style="color:#8B9CC8; font-size:0.72rem; text-transform:uppercase;
                                letter-spacing:0.1em; margin-bottom:0.5rem;">Reported Symptoms</div>
                    <div>{chips}</div>
                </div>
                """, unsafe_allow_html=True)

                if rec.get("ai_response"):
                    st.markdown(f"""
                    <div class="ai-card" style="margin-top:0.5rem;">
                        <div class="ai-header">🤖&nbsp; AI Explanation</div>
                        <div style="color:#8B9CC8; font-size:0.84rem; line-height:1.7;
                                    white-space:pre-wrap;">{rec['ai_response']}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # ── CSV export ────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    df  = pd.DataFrame(records)
    df  = df.drop(columns=["ai_response", "symptoms", "user_email", "id"], errors="ignore")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥  Export as CSV",
        data=csv,
        file_name="medpredict_history.csv",
        mime="text/csv",
        key="csv_export",
    )