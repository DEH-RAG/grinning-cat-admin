import time
import streamlit as st
from streamlit_js_eval import set_cookie
from grinning_cat_python_sdk import GrinningCatClient

from app.env import get_env
from app.utils import show_overlay_spinner, build_client_configuration, clear_auth_cookies, _build_me_data


def login_page():
    st.header("Login Page")

    st.sidebar.warning("Please log in to access the admin features.")

    with st.form(key="login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        if not st.form_submit_button(label="Login"):
            return

        if not username or not password:
            st.error("Please enter both username and password.")
            return

        spinner_container = show_overlay_spinner(f"Authenticating {username}...")
        try:
            client = GrinningCatClient(build_client_configuration())
            token_response = client.auth.token(username, password)
            token = token_response.access_token

            st.session_state["token"] = token
            # Write the token cookie. The me cookie is intentionally NOT written
            # here: set_cookie() is asynchronous (JS-based) and a st.rerun()
            # fired in the same render cycle would race against it, causing the
            # browser to receive an empty me cookie. Instead we only populate
            # st.session_state["me"] via _build_me_data(); the me cookie will be
            # written on the next page refresh by _get_cookie_me() in main.py,
            # after the browser has fully committed the token cookie.
            set_cookie("token", token, duration_days=int(get_env("GRINNING_CAT_JWT_EXPIRE_MINUTES")) / (60 * 24))
            _build_me_data()

            st.toast("Login successful!", icon="\u2705")
            spinner_container.empty()

            time.sleep(1)
            st.rerun()
        except Exception as e:
            clear_auth_cookies()
            spinner_container.empty()
            st.error(f"Error during authentication: {e}")
            return
