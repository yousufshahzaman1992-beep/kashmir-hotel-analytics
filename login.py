import streamlit as st
import sys, os

DIRPATH = os.path.dirname(os.path.abspath(__file__))
if DIRPATH not in sys.path:
    sys.path.insert(0, DIRPATH)

from sheets_db import verify_login
from style import apply_style

def show_login():
    # apply_style() is already called by app.py before show_login();
    # calling it again would re-inject the JS lock, resetting the timer.
    st.markdown("""
    <style>
    /* Aggressively hide all sidebar components on login */
    section[data-testid="stSidebar"], 
    [data-testid="stSidebarNav"],
    button[kind="headerNoPadding"] { display: none !important; }

    :root, [data-theme="dark"] {
        --login-bg: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%);
        --login-card-bg: rgba(15, 23, 42, 0.95);
        --login-card-border: rgba(255,255,255,0.08);
        --login-text-primary: #f8fafc;
        --login-text-secondary: #94a3b8;
        --login-text-muted: #64748b;
        --login-badge-bg: rgba(59,130,246,0.08);
        --login-badge-border: rgba(59,130,246,0.2);
        --login-badge-text: #93c5fd;
        --login-input-bg: #0a1228;
        --login-input-border: rgba(255,255,255,0.12);
        --login-button-bg: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #1d4ed8 100%);
        --login-button-text: #ffffff;
        --login-button-shadow: rgba(59, 130, 246, 0.4);
        --login-chip-bg: rgba(255,255,255,0.05);
        --login-chip-border: rgba(255,255,255,0.08);
        --login-shadow: rgba(0,0,0,0.35);
    }
    
    [data-theme="light"] {
        --login-bg: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #f8fafc 100%);
        --login-card-bg: rgba(255,255,255,0.95);
        --login-card-border: rgba(0,0,0,0.08);
        --login-text-primary: #0f172a;
        --login-text-secondary: #475569;
        --login-text-muted: #64748b;
        --login-badge-bg: rgba(37,99,235,0.05);
        --login-badge-border: rgba(37,99,235,0.15);
        --login-badge-text: #2563eb;
        --login-input-bg: #ffffff;
        --login-input-border: rgba(0,0,0,0.12);
        --login-button-bg: linear-gradient(135deg, #2563eb 0%, #3b82f6 50%, #1d4ed8 100%);
        --login-button-text: #ffffff;
        --login-button-shadow: rgba(37, 99, 235, 0.2);
        --login-chip-bg: rgba(0,0,0,0.03);
        --login-chip-border: rgba(0,0,0,0.06);
        --login-shadow: rgba(0,0,0,0.08);
    }

    .stApp {
        background: var(--login-bg) !important;
        min-height: 100vh;
    }
    .block-container {
        max-width: 440px !important;
        padding-top: 8vh !important;
        margin: 0 auto !important;
    }
    .lg-badge { text-align: center; margin-bottom: 24px; }
    .lg-badge-inner {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: var(--login-badge-bg);
        border: 1px solid var(--login-badge-border);
        backdrop-filter: blur(10px);
        border-radius: 100px;
        padding: 6px 16px;
        font-size: 0.75rem;
        color: var(--login-badge-text);
        letter-spacing: 0.5px;
    }
    .lg-dot {
        width: 6px; height: 6px;
        background: var(--login-badge-text);
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 6px var(--login-badge-text);
    }
    .lg-logo { text-align: center; margin-bottom: 32px; }
    .lg-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 64px; height: 64px;
        background: var(--login-button-bg);
        border-radius: 18px;
        font-size: 32px;
        box-shadow: 0 0 0 1px var(--login-badge-border),
                    0 8px 32px var(--login-button-shadow);
        margin-bottom: 16px;
    }
    .lg-name {
        font-size: 1.5rem; font-weight: 700;
        color: var(--login-text-primary); letter-spacing: -0.5px; margin-bottom: 4px;
    }
    .lg-tagline { font-size: 0.82rem; color: var(--login-text-muted); letter-spacing: 0.3px; }
    [data-testid="stForm"] {
        background: var(--login-card-bg) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid var(--login-card-border) !important;
        border-radius: 20px !important;
        padding: 32px 36px !important;
        box-shadow: 0 8px 32px var(--login-shadow) !important;
        margin-bottom: 24px !important;
    }
    .lg-card-title {
        font-size: 1.25rem; font-weight: 700;
        color: var(--login-text-primary); margin-bottom: 6px; letter-spacing: -0.4px;
    }
    .lg-card-sub { font-size: 0.85rem; color: var(--login-text-secondary); margin-bottom: 24px; }
    .lg-contact {
        background: var(--login-badge-bg);
        border: 1px solid var(--login-badge-border);
        border-radius: 12px;
        padding: 16px 20px;
        text-align: center;
        margin-top: 20px;
    }
    .lg-contact-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--login-badge-text);
        margin-bottom: 6px;
    }
    .lg-contact-text {
        font-size: 0.78rem;
        color: var(--login-text-muted);
        line-height: 1.6;
    }
    .lg-contact-email { color: var(--login-badge-text); font-weight: 500; }
    input[type="text"], input[type="password"] {
        background: var(--login-input-bg) !important;
        border: 1px solid var(--login-input-border) !important;
        color: var(--login-text-primary) !important;
        border-radius: 10px !important;
    }
    input[type="text"]:-webkit-autofill,
    input[type="text"]:-webkit-autofill:hover, 
    input[type="text"]:-webkit-autofill:focus, 
    input[type="text"]:-webkit-autofill:active,
    input[type="password"]:-webkit-autofill,
    input[type="password"]:-webkit-autofill:hover, 
    input[type="password"]:-webkit-autofill:focus, 
    input[type="password"]:-webkit-autofill:active {
        -webkit-box-shadow: 0 0 0 1000px var(--login-input-bg) inset !important;
        -webkit-text-fill-color: var(--login-text-primary) !important;
        box-shadow: 0 0 0 1000px var(--login-input-bg) inset !important;
        transition: background-color 5000s ease-in-out 0s !important;
    }
    input[type="text"]:focus, input[type="password"]:focus {
        border-color: var(--login-badge-text) !important;
        box-shadow: 0 0 0 3px var(--login-badge-border) !important;
    }
    label[data-testid="stWidgetLabel"] p {
        color: var(--login-text-secondary) !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
    }
    .stFormSubmitButton > button {
        background: var(--login-button-bg) !important;
        color: var(--login-button-text) !important;
        border: none !important;
        border-radius: 10px !important;
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.4px !important;
        padding: 14px !important;
        box-shadow: 0 4px 16px var(--login-button-shadow) !important;
        margin-top: 6px !important;
    }
    .stFormSubmitButton > button:hover {
        box-shadow: 0 6px 24px var(--login-button-shadow) !important;
        transform: translateY(-1px) !important;
    }
    .lg-features {
        display: flex; justify-content: center;
        gap: 6px; margin-top: 20px;
    }
    .lg-chip {
        display: inline-flex; align-items: center; gap: 5px;
        background: var(--login-chip-bg);
        border: 1px solid var(--login-chip-border);
        border-radius: 100px; padding: 5px 12px;
        font-size: 0.72rem; color: var(--login-text-muted);
    }
    .lg-footer {
        text-align: center; font-size: 0.72rem;
        color: var(--login-text-muted); margin-top: 20px;
        line-height: 2;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Live badge ────────────────────────────────────────
    st.markdown("""
    <div class='lg-badge'>
        <div class='lg-badge-inner'>
            <span class='lg-dot'></span>
            Platform is live and ready
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Logo ──────────────────────────────────────────────
    st.markdown("""
    <div class='lg-logo'>
        <div class='lg-icon'>🏔️</div>
        <div class='lg-name'>Kashmir Hotel Analytics</div>
        <div class='lg-tagline'>Hotel Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        st.markdown("""
            <div class='lg-card-title'>Sign in to your account</div>
            <div class='lg-card-sub'>Enter your credentials to continue</div>
        """, unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="your username")
        password = st.text_input("Password", type="password",
                                 placeholder="••••••••")
        submit   = st.form_submit_button("Sign In  →", use_container_width=True)

    if submit:
        if not username or not password:
            st.error("Please enter both username and password.")
        else:
            hotel = verify_login(username, password)
            if hotel:
                st.session_state["logged_in"] = True
                st.session_state["hotel"]     = hotel
                if st.query_params.get("hid") != hotel["hotel_id"]:
                    st.query_params["hid"] = hotel["hotel_id"]
                st.rerun()
            else:
                st.error("❌ Incorrect username or password.")

    # ── Privacy + Contact boxes ───────────────────────────
    st.markdown("""
    <div class='lg-contact'>
        <div class='lg-contact-title'>🔒 Your Data is Private</div>
        <div class='lg-contact-text'>
            Only you can see your hotel's bookings and revenue.<br>
            We never share your data with anyone.
        </div>
    </div>

    <br>

    <div class='lg-contact'>
        <div class='lg-contact-title'>Want to get started?</div>
        <div class='lg-contact-text'>
            Contact us to set up your free account.<br><br>
            📧 <span class='lg-contact-email'>Kashmirhotels6@gmail.com</span><br>
            💬 WhatsApp: <span class='lg-contact-email'>+91 8491828292</span><br><br>
            <span style='font-size:0.72rem;color:#475569'>
            Need help? We respond within 2 hours on WhatsApp.
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Feature chips ─────────────────────────────────────
    st.markdown("""
    <div class='lg-features'>
        <div class='lg-chip'>🔒 Private</div>
        <div class='lg-chip'>📊 Live data</div>
        <div class='lg-chip'>☁️ Cloud sync</div>
        <div class='lg-chip'>🌙 Dark mode</div>
    </div>
    <div class='lg-footer'>
        © 2025 Kashmir Analytics · All rights reserved
    </div>
    """, unsafe_allow_html=True)

    # CSS Unlock — triggers the dynamic has-selector to reveal the page
    st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)