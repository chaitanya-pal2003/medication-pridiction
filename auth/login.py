"""
auth/login.py
Advanced Streamlit Login & Registration UI with real-time stats and demo mode.
"""
import re
import streamlit as st
from auth.auth_handler import login_user, register_user, set_session
from db_connector import execute_query

# ─── Fetch Real-Time Data ─────────────────────────────────────────────────────
@st.cache_data(ttl=60) # Cache for 60 seconds to prevent database spam
def get_platform_stats():
    """Fetch live counts of users and predictions from the database."""
    try:
        users = execute_query("SELECT COUNT(*) as cnt FROM users", fetch=True)
        preds = execute_query("SELECT COUNT(*) as cnt FROM history", fetch=True)
        return users[0]['cnt'], preds[0]['cnt']
    except Exception:
        return 0, 0

# ─── Validation Helpers ───────────────────────────────────────────────────────
def is_valid_email(email: str) -> bool:
    """Regex to check if the email format is valid."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


def show_auth_page() -> None:
    """Full-page login / register screen shown to unauthenticated users."""

    # ── Logo & Branding ────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding: 2.5rem 0 1rem;">
        <div style="font-size:4rem; margin-bottom:0.5rem; animation: float 3s ease-in-out infinite;">🏥</div>
        <h1 style="font-family:'Space Grotesk',sans-serif; font-size:2.5rem; font-weight:800;
                   background:linear-gradient(135deg,#8352FD,#00D4FF);
                   -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                   background-clip:text; margin:0 0 0.25rem;">
            MedPredict AI
        </h1>
        <p style="color:#8B9CC8; margin:0; font-size:1.1rem; font-weight:500;">
            Next-Generation Disease Prediction System
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Real-Time Platform Stats ───────────────────────────────────────────────
    users_count, preds_count = get_platform_stats()

    _, stat1, stat2, _ = st.columns([1.5, 1, 1, 1.5])
    with stat1:
        st.markdown(f"""
        <div style="text-align:center; padding:10px; background:rgba(131,82,253,0.1); border-radius:10px; border:1px solid rgba(131,82,253,0.2);">
            <div style="font-size:1.5rem; font-weight:bold; color:#EEF2FF;">{users_count}+</div>
            <div style="font-size:0.75rem; color:#8B9CC8; text-transform:uppercase;">Active Users</div>
        </div>
        """, unsafe_allow_html=True)
    with stat2:
        st.markdown(f"""
        <div style="text-align:center; padding:10px; background:rgba(0,212,255,0.1); border-radius:10px; border:1px solid rgba(0,212,255,0.2);">
            <div style="font-size:1.5rem; font-weight:bold; color:#EEF2FF;">{preds_count}+</div>
            <div style="font-size:0.75rem; color:#8B9CC8; text-transform:uppercase;">AI Predictions</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Centre the form ────────────────────────────────────────────────────────
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        # Added a "Demo Mode" tab for easy college project presentations!
        tab_login, tab_register, tab_demo = st.tabs(["🔑  Sign In", "✨  Create Account", "🚀 Demo Mode"])

        # ─── Login Tab ─────────────────────────────────────────────────────────
        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            log_email    = st.text_input("Email Address", placeholder="patient@example.com", key="log_email")
            log_password = st.text_input("Password",      placeholder="••••••••",            key="log_password", type="password")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Secure Login ➔", key="login_btn", type="primary", use_container_width=True):
                if not log_email or not log_password:
                    st.warning("⚠️ Please enter both email and password.")
                else:
                    with st.spinner("Authenticating..."):
                        result = login_user(log_email, log_password)
                    if result["success"]:
                        set_session(result)
                        st.toast(f"Welcome back, {result['name']}!", icon="👋")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")

        # ─── Register Tab ──────────────────────────────────────────────────────
        with tab_register:
            st.markdown("<br>", unsafe_allow_html=True)
            name     = st.text_input("Full Name",         placeholder="John Doe",              key="reg_name")
            email    = st.text_input("Email Address",     placeholder="you@example.com",       key="reg_email")
            password = st.text_input("Password",          placeholder="At least 6 characters", key="reg_password",    type="password")
            confirm  = st.text_input("Confirm Password",  placeholder="Re-enter password",     key="reg_confirm",     type="password")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("✨  Create Free Account", key="register_btn", type="primary", use_container_width=True):
                # Advanced Validation
                if not all([name, email, password, confirm]):
                    st.error("⚠️ Please fill in all fields.")
                elif not is_valid_email(email):
                    st.error("⚠️ Please enter a valid email address format.")
                elif len(password) < 6:
                    st.error("⚠️ Security alert: Password must be at least 6 characters long.")
                elif password != confirm:
                    st.error("⚠️ Passwords do not match. Please re-type carefully.")
                else:
                    with st.spinner("Provisioning your AI medical workspace..."):
                        result = register_user(name, email, password)
                    if result["success"]:
                        set_session(result)
                        st.balloons() # Fun animation for new users!
                        st.success(f"🎉 Account created! Welcome, **{result['name']}**!")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")

        # ─── Demo Mode Tab ─────────────────────────────────────────────────────
        with tab_demo:
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("🎓 **For Evaluators & Testers:** Click the button below to instantly log in using a temporary Guest Account. No registration required!")

            if st.button("🚀 Enter Guest Mode", key="demo_btn", type="primary", use_container_width=True):
                with st.spinner("Generating Guest Session..."):
                    # Check if guest user exists, if not, create one
                    guest_email = "guest@medpredict.ai"
                    guest_pwd = "guestpassword123"

                    # Try to log in as guest
                    login_attempt = login_user(guest_email, guest_pwd)

                    if not login_attempt["success"]:
                        # Register the guest account if it doesn't exist yet
                        register_user("Guest Evaluator", guest_email, guest_pwd)
                        login_attempt = login_user(guest_email, guest_pwd)

                    if login_attempt["success"]:
                        set_session(login_attempt)
                        st.toast("Logged in as Guest Evaluator!", icon="🚀")
                        st.rerun()
                    else:
                        st.error("Failed to generate guest account. Please use normal registration.")