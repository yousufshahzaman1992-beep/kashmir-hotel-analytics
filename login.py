import streamlit as st
import sys, os

DIRPATH = os.path.dirname(os.path.abspath(__file__))
if DIRPATH not in sys.path:
    sys.path.insert(0, DIRPATH)

from sheets_db import verify_login
from style import apply_style

def show_login():
    apply_style()
    st.markdown("""
    <style>
    /* Aggressively hide all sidebar components on login */
    section[data-testid="stSidebar"], 
    [data-testid="stSidebarNav"],
    button[kind="headerNoPadding"] { display: none !important; }

    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%) !important;
        min-height: 100vh;
    }
    .block-container {
        max-width: 440px !important;
        padding-top: 4vh !important;
        margin: 0 auto !important;
    }
    .lg-badge { text-align: center; margin-bottom: 24px; }
    .lg-badge-inner {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(59,130,246,0.12);
        border: 1px solid rgba(59,130,246,0.25);
        border-radius: 100px;
        padding: 6px 16px;
        font-size: 0.75rem;
        color: #93c5fd;
        letter-spacing: 0.5px;
    }
    .lg-dot {
        width: 6px; height: 6px;
        background: #3b82f6;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 6px #3b82f6;
    }
    .lg-logo { text-align: center; margin-bottom: 32px; }
    .lg-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 64px; height: 64px;
        background: linear-gradient(135deg, #1d4ed8, #60a5fa);
        border-radius: 18px;
        font-size: 32px;
        box-shadow: 0 0 0 1px rgba(59,130,246,0.3),
                    0 8px 32px rgba(59,130,246,0.5);
        margin-bottom: 14px;
    }
    .lg-name {
        font-size: 1.5rem; font-weight: 700;
        color: #f8fafc; letter-spacing: -0.5px; margin-bottom: 4px;
    }
    .lg-tagline { font-size: 0.82rem; color: #64748b; letter-spacing: 0.3px; }
    .lg-card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 28px 36px 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3),
                    inset 0 1px 0 rgba(255,255,255,0.1);
        margin-bottom: 0;
    }
    .lg-card-title {
        font-size: 1.15rem; font-weight: 700;
        color: #f1f5f9; margin-bottom: 4px; letter-spacing: -0.2px;
    }
    .lg-card-sub { font-size: 0.8rem; color: #64748b; margin-bottom: 20px; }
    .lg-contact {
        background: rgba(59,130,246,0.07);
        border: 1px solid rgba(59,130,246,0.2);
        border-radius: 12px;
        padding: 16px 20px;
        text-align: center;
        margin-top: 20px;
    }
    .lg-contact-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #93c5fd;
        margin-bottom: 6px;
    }
    .lg-contact-text {
        font-size: 0.78rem;
        color: #64748b;
        line-height: 1.6;
    }
    .lg-contact-email { color: #3b82f6; font-weight: 500; }
    input[type="text"], input[type="password"] {
        background: var(--secondary-background-color) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        color: var(--text-color) !important;
        border-radius: 10px !important;
    }
    input[type="text"]:focus, input[type="password"]:focus {
        border-color: rgba(59,130,246,0.6) !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    }
    label[data-testid="stWidgetLabel"] p {
        color: #94a3b8 !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
    }
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #1d4ed8, #3b82f6) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.4px !important;
        padding: 14px !important;
        box-shadow: 0 4px 16px rgba(59,130,246,0.4) !important;
        margin-top: 6px !important;
    }
    .stFormSubmitButton > button:hover {
        box-shadow: 0 6px 24px rgba(59,130,246,0.55) !important;
        transform: translateY(-1px) !important;
    }
    .lg-features {
        display: flex; justify-content: center;
        gap: 6px; margin-top: 20px;
    }
    .lg-chip {
        display: inline-flex; align-items: center; gap: 5px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 100px; padding: 5px 12px;
        font-size: 0.72rem; color: #64748b;
    }
    .lg-footer {
        text-align: center; font-size: 0.72rem;
        color: #64748b; margin-top: 20px;
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

    # ── Sign In Card ──────────────────────────────────────
    st.markdown("""
    <div class='lg-card'>
        <div class='lg-card-title'>Sign in to your account</div>
        <div class='lg-card-sub'>Enter your credentials to continue</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
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