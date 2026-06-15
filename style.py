import streamlit as st

def apply_style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .block-container { padding-top: 2rem; }

    .kpi-card {
        background: var(--secondary-background-color);
        border: 1px solid rgba(148,163,184,0.2);
        border-radius: 12px;
        padding: 20px 22px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        height: 110px;
    }
    .card-wrap {
        background: var(--secondary-background-color);
        border: 1px solid rgba(148,163,184,0.2);
        border-radius: 12px;
        padding: 20px;
    }
    .page-title {
        font-family: 'Inter', sans-serif;
        
        font-size: 2.9rem;
        font-weight: 700;
        color: var(--text-color);
        margin: 0;
        padding-top: 10px;
    }
    .page-sub {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: var(--text-color);
        opacity: 0.5;
        margin-top: 4px;
    }
    .badge {
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 500;
        background: var(--secondary-background-color);
        color: #2563eb;
        border: 1px solid rgba(37,99,235,0.3);
        border-radius: 6px;
        padding: 3px 10px;
    }
    .section-title {
        font-family: 'Inter', sans-serif;
        font-size: 0.78rem;
        font-weight: 600;
        color: var(--text-color);
        opacity: 0.5;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 12px;
    }
    .insight-row {
        font-family: 'Inter', sans-serif;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid rgba(148,163,184,0.15);
        font-size: 0.85rem;
        color: var(--text-color);
        opacity: 0.8;
    }
    .insight-row:last-child { border-bottom: none; }
    .insight-val {
        font-weight: 600;
        color: var(--text-color);
        opacity: 1;
    }
    .divider {
        height: 1px;
        background: rgba(148,163,184,0.2);
        margin: 20px 0;
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: var(--secondary-background-color);
        border: 1px solid rgba(148,163,184,0.2);
        border-left: 3px solid #2563eb;
        border-radius: 12px;
        padding: 16px 20px !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }

    /* Hand cursor on dropdowns */
    [data-testid="stSelectbox"] *,
    [data-testid="stMultiSelect"] *,
    [data-baseweb="select"] *,
    [data-baseweb="popover"] *,
    [role="listbox"] *,
    [role="option"] *,
    ul[data-testid="stSelectboxVirtualDropdown"] *,
    .stSelectbox div,
    .stMultiSelect div {
        cursor: pointer !important;
    }

    /* Hand cursor on buttons */
    button, [role="button"],
    .stButton > button,
    [data-testid="stFormSubmitButton"] > button,
    [data-testid="stDownloadButton"] > button {
        cursor: pointer !important;
    }

    /* Hide function name from spinner */
    [data-testid="stSpinner"] p::before {
        content: "" !important;
    }
    div[data-testid="stSpinner"] > div > div > p {
        display: none !important;
    }

    /* Hide "Press Enter to submit form" tooltip */
    [data-baseweb="input"] + div,
    [data-baseweb="base-input"] + div,
    small[class*="instructions"] {
        display: none !important;
    }

    /* Clean input borders */
    [data-baseweb="input"] {
        border: 1px solid rgba(148,163,184,0.3) !important;
        border-radius: 8px !important;
    }
    [data-baseweb="input"]:focus-within {
        border: 1px solid #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    }

    /* Remove border from password inner wrapper */
    [data-baseweb="base-input"] {
        border: none !important;
        box-shadow: none !important;
    }

    </style>
    """, unsafe_allow_html=True)


def ensure_auth(allowed_roles=None):
    """Handles session restoration, CSS hiding for non-logged users, and redirects."""
    from sheets_db import get_hotel_by_id
    
    if not st.session_state.get("logged_in"):
        # Aggressively hide UI
        st.markdown("""
            <style>
                section[data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none !important; }
                button[kind="headerNoPadding"] { display: none !important; }
            </style>
        """, unsafe_allow_html=True)

        # Restore from URL
        hid = st.query_params.get("hid")
        if hid:
            if hid == "ADMIN":
                st.session_state.logged_in = True
                st.session_state.hotel = {"hotel_id": "ADMIN", "name": "Administrator"}
                st.rerun()
            else:
                hotel = get_hotel_by_id(hid)
                if hotel:
                    st.session_state.logged_in = True
                    st.session_state.hotel = hotel
                    st.rerun()
        
        st.switch_page("app.py")
        st.stop()
    # Role-based access control
    hotel = st.session_state.hotel
    
    # Auto-hide admin pages for standard users to prevent flicker
    if hotel.get("hotel_id") != "ADMIN":
        hide_admin_pages()

    if allowed_roles and hotel.get("hotel_id") not in allowed_roles:
        if "ADMIN" in allowed_roles and hotel.get("hotel_id") != "ADMIN":
            st.switch_page("app.py")
            st.stop()
            
    # Persist ID in URL
    if st.query_params.get("hid") != hotel["hotel_id"]:
        st.query_params["hid"] = hotel["hotel_id"]
    return hotel


def sidebar_logo():
    st.sidebar.markdown("""
    <div style='display:flex;align-items:center;gap:10px;margin-bottom:6px'>
        <div style='width:36px;height:36px;
                    background:linear-gradient(135deg,#1e40af,#3b82f6);
                    border-radius:8px;display:flex;align-items:center;
                    justify-content:center;font-size:18px;flex-shrink:0;
                    box-shadow:0 3px 8px rgba(59,130,246,0.3)'>🏔️</div>
        <div>
            <div style='font-size:0.95rem;font-weight:700;letter-spacing:2px;
                        text-transform:uppercase;color:#3b82f6'>Kashmir</div>
            <div style='font-size:1.05rem;font-weight:600;
                        color:var(--text-color);line-height:1.2'>Analytics</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar(hotel):
    """Renders the standard sidebar for all pages."""
    with st.sidebar:
        sidebar_logo()
        st.divider()
        
        plan_info = ""
        if hotel.get("hotel_id") == "ADMIN":
            plan_info = "<div style='font-size:0.75rem;color:#3b82f6'>Full Access</div>"
        else:
            plan = hotel.get("plan", "Full Access").title()
            plan_info = f"<div style='font-size:0.75rem;color:#3b82f6'>{plan} Plan</div>"

        st.markdown(f"""
        <div style='background:var(--secondary-background-color);
                    border:1px solid rgba(148,163,184,0.2);
                    border-radius:10px;padding:12px 14px;margin-bottom:12px'>
            <div style='font-size:0.7rem;color:#64748b;text-transform:uppercase;
                        letter-spacing:1px;margin-bottom:4px'>Logged in as</div>
            <div style='font-size:0.95rem;font-weight:600;
                        color:var(--text-color)'>{hotel["name"]}</div>
            {plan_info}
        </div>
        """, unsafe_allow_html=True)
        
        # Static Support link and Logout Button
        st.divider()
        st.markdown("<div class='section-title'>Support</div>", unsafe_allow_html=True)
        st.markdown("<a href='https://wa.me/918491828292' target='_blank' style='text-decoration:none;'><button style='width:100%; border-radius:10px; padding:10px; background:#25d366; color:white; border:none; cursor:pointer; font-weight:600;'>💬 Contact Support</button></a>", unsafe_allow_html=True)
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.query_params.clear()
            st.cache_data.clear()
            st.rerun()

def hide_admin_pages():
    st.markdown("""
    <style>
    [data-testid="stSidebarNav"] a[href*="3_Admin"],
    [data-testid="stSidebarNav"] a[href*="Admin_Panel"],
    [data-testid="stSidebarNav"] a[href*="4_Setup"],
    [data-testid="stSidebarNav"] a[href*="setup_account"],
    [data-testid="stSidebarNav"] a[href*="Setup_Account"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)