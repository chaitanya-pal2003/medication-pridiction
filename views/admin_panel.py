"""
views/admin_panel.py
Comprehensive Admin Dashboard with CMS and Audit Logging.
"""
import streamlit as st
import pandas as pd
import bcrypt
from db_connector import get_connection

# ── Helper Functions ────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def log_action(action_type: str, description: str):
    """Helper to instantly write an audit log to the database."""
    admin_email = st.session_state.get("user_email", "Unknown System")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO audit_logs (user_email, action_type, description) VALUES (%s, %s, %s)",
            (admin_email, action_type, description)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Failed to write audit log: {e}")

# ── Main Admin UI ───────────────────────────────────────────────────────────
def show_admin_panel() -> None:
    if st.session_state.get("role") != "admin":
        st.error("🚫 Access Denied. You do not have permission to view this page.")
        st.stop()

    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">👑 Super Admin Dashboard</h2>
    </div>
    <br>
    """, unsafe_allow_html=True)

    tab_dash, tab_users, tab_diseases, tab_about, tab_audit = st.tabs([
        "📊 Dashboard",
        "👥 Manage Users",
        "🔬 Manage Diseases",
        "ℹ️ Manage About Page",
        "📜 Audit Logs"
    ])

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # ── TAB 1: DASHBOARD ──────────────────────────────────────────────────
    with tab_dash:
        st.subheader("System Overview")
        try:
            cursor.execute("SELECT COUNT(*) as total FROM users")
            total_users = cursor.fetchone()['total']

            # FIXED: Reading from 'history', not 'predictions'
            cursor.execute("SELECT COUNT(*) as total FROM history")
            total_predictions = cursor.fetchone()['total']
        except Exception:
            total_users = "Error"
            total_predictions = "Error"

        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**Total Registered Users:** \n### {total_users}")
        with col2:
            st.success(f"**Total Predictions Made:** \n### {total_predictions}")
        with col3:
            st.warning("**System Status:** \n### Online 🟢")

    # ── TAB 2: MANAGE USERS ───────────────────────────────────────────────
    with tab_users:
        st.subheader("User Management")

        cursor.execute("SELECT id, name, email, role, created_at FROM users")
        users_data = cursor.fetchall()

        if users_data:
            df = pd.DataFrame(users_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            with st.expander("🛠️ Edit / Delete / Reset Password"):
                selected_email = st.selectbox("Select user by email:", df['email'].tolist())
                is_current_user = selected_email == st.session_state.get("user_email")

                col1, col2 = st.columns(2)
                with col1:
                    new_role = st.selectbox("Role", ["user", "admin"], key="edit_role")
                    if st.button("Update Role", type="primary"):
                        if is_current_user and new_role == 'user':
                            st.error("You cannot demote yourself!")
                        else:
                            cursor.execute("UPDATE users SET role = %s WHERE email = %s", (new_role, selected_email))
                            conn.commit()
                            log_action("EDIT_USER", f"Changed role of {selected_email} to {new_role}")
                            st.success("Role updated! Refreshing...")
                            st.rerun()

                with col2:
                    new_temp_pass = st.text_input("New Temporary Password", type="password")
                    if st.button("Reset Password"):
                        hashed_pw = hash_password(new_temp_pass)
                        cursor.execute("UPDATE users SET password_hash = %s WHERE email = %s", (hashed_pw, selected_email))
                        conn.commit()
                        log_action("RESET_PASSWORD", f"Reset password for {selected_email}")
                        st.success("Password updated!")

                    if not is_current_user:
                        if st.button("🗑️ Delete User", use_container_width=True):
                            cursor.execute("DELETE FROM users WHERE email = %s", (selected_email,))
                            conn.commit()
                            log_action("DELETE_USER", f"Deleted account: {selected_email}")
                            st.success("User deleted! Refreshing...")
                            st.rerun()

    # ── TAB 3: MANAGE DISEASES (CMS) ──────────────────────────────────────
    with tab_diseases:
        st.subheader("Disease & Symptom Editor")

        d_col1, d_col2 = st.columns(2)
        with d_col1:
            with st.form("add_disease_form"):
                st.write("**Add New Disease Profile**")
                d_name = st.text_input("Disease Name")
                d_icon = st.text_input("Emoji Icon (e.g., 🦠)")
                d_desc = st.text_area("Description")
                if st.form_submit_button("Add Disease"):
                    cursor.execute("INSERT INTO diseases (name, icon, description) VALUES (%s, %s, %s)", (d_name, d_icon, d_desc))
                    conn.commit()
                    log_action("ADD_DISEASE", f"Added disease: {d_name}")
                    st.success("Added! Refreshing...")
                    st.rerun()

        with d_col2:
            cursor.execute("SELECT id, name FROM diseases")
            all_diseases = cursor.fetchall()

            if all_diseases:
                with st.form("add_symptom_form"):
                    st.write("**Add Symptom to Disease**")
                    disease_opts = {d['name']: d['id'] for d in all_diseases}
                    selected_d_name = st.selectbox("Target Disease", list(disease_opts.keys()))
                    s_name = st.text_input("Symptom Name (e.g., 'Severe headache')")
                    if st.form_submit_button("Add Symptom"):
                        cursor.execute("INSERT INTO symptoms (disease_id, symptom_name) VALUES (%s, %s)", (disease_opts[selected_d_name], s_name))
                        conn.commit()
                        log_action("ADD_SYMPTOM", f"Added symptom '{s_name}' to {selected_d_name}")
                        st.success("Symptom added! Refreshing...")
                        st.rerun()

        st.markdown("---")
        st.write("**Current Diseases & Symptoms in Database**")

        # Re-fetch to get IDs for delete operations
        cursor.execute("SELECT id, name, icon FROM diseases ORDER BY name")
        disease_list = cursor.fetchall()

        if disease_list:
            for disease in disease_list:
                with st.expander(f"{disease.get('icon', '🦠')} {disease['name']}"):
                    # ── Delete Disease button ───────────────────────────
                    st.warning(
                        f"⚠️ Deleting **{disease['name']}** will also remove "
                        "all its symptoms permanently."
                    )
                    if st.button(
                        f"🗑️ Delete Disease: {disease['name']}",
                        key=f"del_disease_{disease['id']}",
                        type="primary",
                        use_container_width=True,
                    ):
                        cursor.execute(
                            "DELETE FROM symptoms WHERE disease_id = %s",
                            (disease['id'],)
                        )
                        cursor.execute(
                            "DELETE FROM diseases WHERE id = %s",
                            (disease['id'],)
                        )
                        conn.commit()
                        log_action(
                            "DELETE_DISEASE",
                            f"Deleted disease and its symptoms: {disease['name']}"
                        )
                        st.success(f"Deleted '{disease['name']}'. Refreshing...")
                        st.rerun()

                    # ── List symptoms with individual delete buttons ────
                    cursor.execute(
                        "SELECT id, symptom_name FROM symptoms WHERE disease_id = %s",
                        (disease['id'],)
                    )
                    symptoms = cursor.fetchall()

                    if symptoms:
                        st.write("**Symptoms:**")
                        for sym in symptoms:
                            s_col1, s_col2 = st.columns([4, 1])
                            with s_col1:
                                st.write(f"• {sym['symptom_name']}")
                            with s_col2:
                                if st.button(
                                    "🗑️",
                                    key=f"del_sym_{sym['id']}",
                                    help=f"Delete symptom: {sym['symptom_name']}",
                                ):
                                    cursor.execute(
                                        "DELETE FROM symptoms WHERE id = %s",
                                        (sym['id'],)
                                    )
                                    conn.commit()
                                    log_action(
                                        "DELETE_SYMPTOM",
                                        f"Deleted symptom '{sym['symptom_name']}' "
                                        f"from {disease['name']}"
                                    )
                                    st.success("Symptom deleted. Refreshing...")
                                    st.rerun()
                    else:
                        st.info("No symptoms added yet for this disease.")
        else:
            st.info("No diseases in the database yet.")

    # ── TAB 4: MANAGE ABOUT PAGE ──────────────────────────────────────────
    with tab_about:
        st.subheader("Edit About Page Content")

        cursor.execute("SELECT content FROM app_content WHERE section_name = 'about_purpose'")
        about_data = cursor.fetchone()
        current_about_text = about_data['content'] if about_data else ""

        new_about_text = st.text_area("Purpose & Description", value=current_about_text, height=200)

        if st.button("💾 Save About Page Updates", type="primary"):
            cursor.execute("""
                INSERT INTO app_content (section_name, content) 
                VALUES ('about_purpose', %s) 
                ON DUPLICATE KEY UPDATE content = %s
            """, (new_about_text, new_about_text))
            conn.commit()
            log_action("UPDATE_CONTENT", "Updated the About Page text.")
            st.success("About page updated successfully!")

    # ── TAB 5: AUDIT LOGS ─────────────────────────────────────────────────
    with tab_audit:
        st.subheader("System Security & Action Logs")

        log_view = st.radio("Filter Logs:", ["All System Logs", "My Personal Actions Only"], horizontal=True)

        if log_view == "My Personal Actions Only":
            my_email = st.session_state.get("user_email")
            cursor.execute("SELECT timestamp, action_type, description FROM audit_logs WHERE user_email = %s ORDER BY timestamp DESC", (my_email,))
        else:
            cursor.execute("SELECT timestamp, user_email, action_type, description FROM audit_logs ORDER BY timestamp DESC LIMIT 100")

        logs = cursor.fetchall()

        if logs:
            st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)
        else:
            st.info("No logs found yet.")

    conn.close()