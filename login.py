import streamlit as st
import sys, os
sys.path.append(os.path.dirname(__file__))
from sheets_db import get_hotel
from style import apply_style, sidebar_logo

def show_login():
    apply_style()

    # Extra CSS for login page only
    st.markdown("""
    <style>
    .login-card {
        max-width: 420px;
        margin: 60px auto 0 auto;
        background: var(--secondary-background-color);
        border: 1px solid rgba(148,163,184,0.2);
        border-radius: 16px;
        padding: 40px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.08);
    }
    .login-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--text-color);
        margin-bottom: 6px;
    }
    .login-sub {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: var(--text-color);
        opacity: 0.5;
        margin-bottom: 28px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Centered login card
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class='login-card'>
            <div style='text-align:center;margin-bottom:20px'>
                <div style='width:52px;height:52px;
                            background:linear-gradient(135deg,#1e40af,#3b82f6);
                            border-radius:12px;display:inline-flex;
                            align-items:center;justify-content:center;
                            font-size:24px;box-shadow:0 4px 12px rgba(59,130,246,0.3)'>
                    🏔️
                </div>
            </div>
            <div class='login-title' style='text-align:center'>Welcome back</div>
            <div class='login-sub' style='text-align:center'>
                Sign in to your hotel dashboard
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit   = st.form_submit_button("Sign In", use_container_width=True)

        if submit:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                with st.spinner("Signing in..."):
                    hotel = get_hotel(username)

                if hotel is None:
                    st.error("❌ Username not found.")
                elif hotel["password"] != password:
                    st.error("❌ Incorrect password.")
                else:
                    # Save to session state
                    st.session_state["logged_in"]  = True
                    st.session_state["hotel_id"]   = hotel["hotel_id"]
                    st.session_state["hotel_name"] = hotel["name"]
                    st.session_state["username"]   = hotel["username"]
                    st.session_state["plan"]       = hotel["plan"]
                    st.rerun()