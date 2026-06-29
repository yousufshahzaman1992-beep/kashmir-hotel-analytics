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
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

    /* Aggressively hide all sidebar components on login */
    section[data-testid="stSidebar"], 
    [data-testid="stSidebarNav"],
    button[kind="headerNoPadding"] { display: none !important; }

    :root, [data-theme="dark"] {
        --login-bg:           #050e0b;
        --login-card-bg:      rgba(11, 26, 22, 0.75);
        --login-card-border:  rgba(16, 185, 129, 0.12);
        --login-text-primary: #f8fafc;
        --login-text-secondary: #94a3b8;
        --login-text-muted:   #475569;
        --login-badge-bg:     rgba(16, 185, 129, 0.08);
        --login-badge-border: rgba(16, 185, 129, 0.2);
        --login-badge-text:   #34d399;
        --login-input-bg:     #071310;
        --login-input-border: rgba(255, 255, 255, 0.06);
        --login-button-bg:    linear-gradient(135deg, #064e3b 0%, #10b981 100%);
        --login-button-text:  #ffffff;
        --login-button-shadow: rgba(16, 185, 129, 0.25);
        --login-shadow:       rgba(0, 0, 0, 0.5);
        --mesh-bg-gradient:
            radial-gradient(ellipse 60% 40% at 50% 0%, rgba(16,185,129,0.08) 0%, transparent 60%),
            radial-gradient(ellipse 60% 50% at 50% 100%, rgba(245,158,11,0.04) 0%, transparent 60%);
        --primary-color:      #10b981;
    }
    
    [data-theme="light"] {
        --login-bg:           #f8fafc;
        --login-card-bg:      rgba(255, 255, 255, 0.9);
        --login-card-border:  rgba(4, 120, 87, 0.08);
        --login-text-primary: #0f172a;
        --login-text-secondary: #475569;
        --login-text-muted:   #94a3b8;
        --login-badge-bg:     rgba(4, 120, 87, 0.04);
        --login-badge-border: rgba(4, 120, 87, 0.12);
        --login-badge-text:   #047857;
        --login-input-bg:     #ffffff;
        --login-input-border: rgba(0, 0, 0, 0.08);
        --login-button-bg:    linear-gradient(135deg, #047857 0%, #059669 100%);
        --login-button-text:  #ffffff;
        --login-button-shadow: rgba(4, 120, 87, 0.15);
        --login-shadow:       rgba(15, 23, 42, 0.08);
        --mesh-bg-gradient:
            radial-gradient(ellipse 60% 40% at 50% 0%, rgba(4,120,87,0.03) 0%, transparent 60%),
            radial-gradient(ellipse 60% 50% at 50% 100%, rgba(180,83,9,0.02) 0%, transparent 60%);
        --primary-color:      #047857;
    }

    .stApp {
        background-color: var(--login-bg) !important;
        background: var(--login-bg) !important;
        min-height: 100vh;
        font-family: 'Inter', sans-serif;
    }
    
    /* Animated background mesh */
    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background: var(--mesh-bg-gradient);
        pointer-events: none;
        z-index: 0;
    }

    .block-container {
        max-width: 420px !important;
        padding-top: 10vh !important;
        margin: 0 auto !important;
        position: relative;
        z-index: 1;
    }
    .lg-logo { text-align: center; margin-bottom: 28px; }
    .lg-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 52px; height: 52px;
        background: linear-gradient(135deg, #064e3b, #10b981);
        border-radius: 14px;
        font-size: 26px;
        box-shadow: 0 4px 20px var(--login-button-shadow);
        margin-bottom: 14px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .lg-name {
        font-family: 'Outfit', sans-serif;
        font-size: 1.45rem; font-weight: 800;
        color: var(--login-text-primary);
        letter-spacing: -0.6px; margin-bottom: 4px;
    }
    .lg-tagline { 
        font-size: 0.78rem; 
        color: var(--login-text-secondary); 
        letter-spacing: 0.5px;
        text-transform: uppercase;
        font-weight: 600;
    }
    [data-testid="stForm"] {
        background: var(--login-card-bg) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid var(--login-card-border) !important;
        border-radius: 16px !important;
        padding: 32px 32px !important;
        box-shadow: 0 12px 40px var(--login-shadow) !important;
        margin-bottom: 24px !important;
    }
    .lg-card-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.2rem; font-weight: 700;
        color: var(--login-text-primary); margin-bottom: 4px; letter-spacing: -0.3px;
    }
    .lg-card-sub { font-size: 0.8rem; color: var(--login-text-secondary); margin-bottom: 24px; }
    
    input[type="text"], input[type="password"] {
        background: var(--login-input-bg) !important;
        border: 1px solid var(--login-input-border) !important;
        color: var(--login-text-primary) !important;
        border-radius: 8px !important;
        padding: 10px 12px !important;
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
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 2px var(--login-badge-border) !important;
    }
    label[data-testid="stWidgetLabel"] p {
        color: var(--login-text-primary) !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        margin-bottom: 6px !important;
    }
    .stFormSubmitButton > button {
        background: var(--login-button-bg) !important;
        color: var(--login-button-text) !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.2px !important;
        padding: 12px !important;
        box-shadow: 0 4px 12px var(--login-button-shadow) !important;
        margin-top: 8px !important;
        transition: all 0.2s ease !important;
    }
    .stFormSubmitButton > button:hover {
        box-shadow: 0 6px 18px var(--login-button-shadow) !important;
        transform: translateY(-1px) !important;
    }
    .lg-footer {
        text-align: center; font-size: 0.75rem;
        color: var(--login-text-muted); margin-top: 32px;
        line-height: 1.8;
    }
    .lg-footer-links {
        margin-top: 8px;
        display: flex;
        justify-content: center;
        gap: 12px;
        font-size: 0.75rem;
    }
    .lg-footer-link {
        color: var(--login-badge-text) !important;
        text-decoration: none !important;
        font-weight: 500;
        transition: opacity 0.2s;
    }
    .lg-footer-link:hover {
        opacity: 0.8;
        text-decoration: underline !important;
    }
    .lg-footer-dot {
        color: var(--login-text-muted);
    }
    </style>
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
            <div class='lg-card-title'>Sign In</div>
            <div class='lg-card-sub'>Enter your hotel credentials to access the platform.</div>
        """, unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="your username")
        password = st.text_input("Password", type="password",
                                 placeholder="••••••••")
        submit   = st.form_submit_button("Sign In", width='stretch')

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

    # ── Footer ────────────────────────────────────────────
    st.markdown("""
    <div class='lg-footer'>
        <div style='margin-bottom: 4px; font-weight: 600; color: var(--login-text-primary);'>🔒 Enterprise-Grade Security</div>
        <div style='color: var(--login-text-secondary); max-width: 320px; margin: 0 auto 12px auto; font-size: 0.72rem;'>
            Only authorized hotel managers can access booking records and revenue analytics. Your data is encrypted and completely confidential.
        </div>
        <div class='lg-footer-links'>
            <a href='mailto:Kashmirhotels6@gmail.com' class='lg-footer-link'>Email Support</a>
            <span class='lg-footer-dot'>•</span>
            <a href='https://wa.me/918491828292' target='_blank' class='lg-footer-link'>WhatsApp Helpdesk</a>
        </div>
        <div style='margin-top: 32px; font-size: 0.65rem; color: var(--login-text-muted); letter-spacing: 0.5px;'>
            © 2026 KASHMIR ANALYTICS · ALL RIGHTS RESERVED
        </div>
    </div>
    """, unsafe_allow_html=True)

    # CSS Unlock — triggers the dynamic has-selector to reveal the page
    st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)