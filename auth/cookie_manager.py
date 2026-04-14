"""
auth/cookie_manager.py
Handles browser cookies to keep users logged in across page refreshes.
"""

import datetime
import json
import streamlit as st
import extra_streamlit_components as stx

def get_cookie_manager():
    if "cookie_manager" not in st.session_state:
        st.session_state["cookie_manager"] = stx.CookieManager(key="auth_manager")
    return st.session_state["cookie_manager"]

def set_auth_cookie(user_data: dict) -> None:
    """Saves the user data into a browser cookie that expires in 30 days."""
    cm = get_cookie_manager()
    expire_date = datetime.datetime.now() + datetime.timedelta(days=30)
    cm.set("medpredict_auth", json.dumps(user_data), expires_at=expire_date)

def get_auth_cookie():
    cm = get_cookie_manager()
    # This is the important part: get() can return None if the JS hasn't finished loading
    val = cm.get("medpredict_auth")
    if val:
        try:
            return json.loads(val) if isinstance(val, str) else val
        except:
            return None
    return None

def delete_auth_cookie() -> None:
    """Deletes the cookie when the user logs out."""
    cm = get_cookie_manager()
    try:
        cm.delete("medpredict_auth")
    except KeyError:
        # If the cookie doesn't exist or is already deleted, ignore it
        pass