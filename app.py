"""
app.py — MedPredict AI Entry Point
Disease Prediction System — Final Year College Project

Run with:  streamlit run app.py
"""
import os
import sys
import time
import streamlit as st

# Ensure project root is on the path so all packages import correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="MedPredict AI — Disease Prediction System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "## MedPredict AI\nDisease Prediction System — Final Year College Project",
        "Get Help": None,
        "Report a bug": None,
    },
)

# Import local auth modules AFTER page config to prevent Streamlit errors
from auth.cookie_manager import get_cookie_manager, get_auth_cookie
from auth.auth_handler import set_session, is_logged_in


# ── CSS injection ─────────────────────────────────────────────────────────────
def _load_css() -> None:
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


_load_css()


# ── Database initialisation (once per session) ────────────────────────────────
if "db_ready" not in st.session_state:
    try:
        from db_connector import init_db
        init_db()
        st.session_state["db_ready"] = True
    except Exception as db_err:
        st.error(
            f"❌ **Database connection failed.**\n\n"
            f"{db_err}\n\n"
            f"**Steps to fix:**\n"
            f"1. Make sure MySQL is running.\n"
            f"2. Copy `.env.example` → `.env` and fill in your credentials.\n"
            f"3. Restart the app with `streamlit run app.py`"
        )
        st.stop()


# ── Cookie Auto-Login ─────────────────────────────────────────────────────────
# 1. Initialize the cookie widget
get_cookie_manager()

# 2. The Magic Fix for Refreshing: Give the widget 0.2 seconds to mount and fetch data,
# then force a rerun so it reads the cookie before kicking you out!
if "cookies_loaded" not in st.session_state:
    st.session_state["cookies_loaded"] = True
    time.sleep(0.2)
    st.rerun()

# 3. Check for cookie if the user is not in active session
if not is_logged_in() and not st.session_state.get("just_logged_out", False):
    saved_cookie = get_auth_cookie()

    if saved_cookie:
        # Silently restore the session from the cookie
        set_session(saved_cookie, remember_me=False)
        st.rerun()


# ── Auth gate ─────────────────────────────────────────────────────────────────
if not is_logged_in():
    from auth.login import show_auth_page
    show_auth_page()
    st.stop()

# ── Top Header Bar (Profile & Logout) ─────────────────────────────────────────
# Creates a clean top navigation bar for user account actions
header_col1, header_col2, header_col3 = st.columns([6, 1, 1])
with header_col2:
    if st.button("👤 Profile", use_container_width=True):
        st.session_state["current_page"] = "profile"
        st.rerun()
with header_col3:
    if st.button("🚪 Logout", type="primary", use_container_width=True):
        from auth.auth_handler import logout
        logout()

st.markdown("---") # Visual divider below the header


# ── Default Page State ────────────────────────────────────────────────────────
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "home"


# ── Sidebar Navigation ────────────────────────────────────────────────────────
with st.sidebar:
    user_name  = st.session_state.get("user_name",  "User")
    user_email = st.session_state.get("user_email", "")
    user_role  = st.session_state.get("role", "user")

    # Logo
    st.markdown("""
    <div class="sidebar-logo">
        <div class="logo-icon">🏥</div>
        <div class="logo-text">
            <h2>MedPredict AI</h2>
            <p>Disease Prediction System</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # User badge (Now shows Admin/User role!)
    role_color = "#FF4D4F" if user_role == "admin" else "#2ED573"
    st.markdown(f"""
    <div class="user-badge" style="position: relative;">
        <div class="user-avatar">{user_name[0].upper()}</div>
        <div class="user-info">
            <strong>{user_name}</strong>
            <span>{user_email}</span>
            <span style="font-size:0.7rem; color:{role_color}; text-transform:uppercase; font-weight:bold;">
                {user_role}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Base Navigation Items
    NAV_ITEMS = {
        "🏠  Dashboard":        "home",
        "🔬  Predict Disease":  "predict",
        "📋  History":          "history",
        "ℹ️   About":           "about",
    }

    # Inject Admin Panel dynamically
    if user_role == "admin":
        NAV_ITEMS["👑  Admin Panel"] = "admin_panel"

    # Nav buttons rendering
    for label, page_key in NAV_ITEMS.items():
        is_active = st.session_state["current_page"] == page_key
        # Style active button differently via a tiny CSS trick
        btn_style = """<style>div[data-testid='stButton']:last-of-type > button {
            background: linear-gradient(135deg,#8352FD,#00D4FF) !important;
            color:#fff !important; border:none !important;
        }</style>""" if is_active else ""
        if btn_style:
            st.markdown(btn_style, unsafe_allow_html=True)
        if st.button(label, key=f"nav_{page_key}", use_container_width=True):
            st.session_state["current_page"] = page_key
            st.rerun()


# ── Page Router ───────────────────────────────────────────────────────────────
page = st.session_state.get("current_page", "home")

if page == "home":
    from views.home    import show_home;    show_home()
elif page == "predict":
    from views.predict import show_predict; show_predict()
elif page == "history":
    from views.history import show_history; show_history()
elif page == "about":
    from views.about   import show_about;   show_about()
elif page == "admin_panel":
    from views.admin_panel import show_admin_panel; show_admin_panel()
elif page == "profile":
    # Basic Profile Page View
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">👤 My Profile</h2>
        <span class="section-badge">Account Details</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])

    with c2:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.1); border-radius:15px; padding:2rem; text-align:center;">
            <div style="font-size:4rem; margin-bottom:1rem;">🧑‍💻</div>
            <h3 style="color:#EEF2FF; margin-bottom:0.5rem;">{st.session_state.get('user_name')}</h3>
            <p style="color:#8B9CC8; font-size:1.1rem; margin-bottom:0.2rem;">{st.session_state.get('user_email')}</p>
            <p style="color:#00D4FF; font-weight:bold; text-transform:uppercase; font-size:0.9rem;">
                Role: {st.session_state.get('role', 'User')}
            </p>
        </div>
        """, unsafe_allow_html=True)