import streamlit as st


def apply_style():
    # ── PURE CSS DYNAMIC FLASH LOCK ──────────────────────────────────────────
    # We hide the entire app view container by default. It is only revealed
    # (with a smooth fade-in) when the Python script successfully completes
    # execution and appends `<div class="app-unlocked"></div>` to the DOM.
    # This prevents any raw content flash during websocket updates or redirects.
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

    [data-testid="stAppViewContainer"] {
        opacity: 0 !important;
    }
    [data-testid="stAppViewContainer"]:has(.app-unlocked) {
        opacity: 1 !important;
        transition: opacity 0.3s ease-in-out !important;
    }

    /* Hard lock injected by ensure_auth() on redirect */
    .auth-redirect-lock [data-testid="stMain"],
    .auth-redirect-lock [data-testid="stMainBlockContainer"] {
        opacity: 0 !important;
        animation: none !important;
    }

    /* ═══════════════════════════════════════════════
       GLOBAL BASE
    ═══════════════════════════════════════════════ */
    *, *::before, *::after { box-sizing: border-box; }

    html, body, [data-testid="stAppViewContainer"] {
        background: #060b18 !important;
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif;
    }

    /* Animated background mesh */
    [data-testid="stAppViewContainer"]::before {
        content: '';
        position: fixed;
        inset: 0;
        background:
            radial-gradient(ellipse 80% 60% at 10% 0%, rgba(37, 99, 235, 0.08) 0%, transparent 60%),
            radial-gradient(ellipse 60% 50% at 90% 100%, rgba(139, 92, 246, 0.07) 0%, transparent 60%),
            radial-gradient(ellipse 40% 40% at 50% 50%, rgba(6, 182, 212, 0.04) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
    }

    /* ═══════════════════════════════════════════════
       THEME TOGGLE LOCKOUT
       Hides the Streamlit settings button so users
       cannot switch to light mode and break the design.
    ═══════════════════════════════════════════════ */
    [data-testid="stToolbarActions"] { display: none !important; }

    /* st.page_link() — sidebar navigation link text colors */
    [data-testid="stPageLink"] a,
    [data-testid="stPageLink"] a p,
    [data-testid="stPageLink"] a span,
    [data-testid="stPageLink"] p,
    [data-testid="stPageLink"] span {
        color: #cbd5e1 !important;
        text-decoration: none !important;
    }
    [data-testid="stPageLink"]:hover a,
    [data-testid="stPageLink"]:hover a p,
    [data-testid="stPageLink"]:hover a span {
        color: #93c5fd !important;
    }
    [data-testid="stPageLink"][aria-current="page"] a,
    [data-testid="stPageLink"][aria-current="page"] a p,
    [data-testid="stPageLink"][aria-current="page"] a span {
        color: #60a5fa !important;
        font-weight: 600 !important;
    }

    /* ═══════════════════════════════════════════════
       SIDEBAR
    ═══════════════════════════════════════════════ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #080e1f 0%, #0a1228 60%, #080e1f 100%) !important;
        border-right: 1px solid rgba(59, 130, 246, 0.08) !important;
        box-shadow: 4px 0 30px rgba(0, 0, 0, 0.4);
    }
    [data-testid="stSidebarNav"] { padding-top: 10px; }
    [data-testid="stSidebarNav"] li a {
        border-radius: 10px;
        margin: 3px 10px;
        padding: 10px 14px;
        font-weight: 500;
        font-size: 0.88rem;
        color: #cbd5e1 !important;
        transition: all 0.25s ease;
    }
    [data-testid="stSidebarNav"] li a:hover {
        background: rgba(59, 130, 246, 0.1) !important;
        color: #93c5fd !important;
        transform: translateX(3px);
    }
    [data-testid="stSidebarNav"] li a[data-selected="true"] {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.25), rgba(59, 130, 246, 0.12)) !important;
        color: #60a5fa !important;
        border-left: 3px solid #3b82f6;
        font-weight: 600;
    }


    /* ═══════════════════════════════════════════════
       LAYOUT
    ═══════════════════════════════════════════════ */
    .block-container {
        padding-top: 4rem !important;
        padding-bottom: 3rem;
        max-width: 1280px;
    }

    /* ═══════════════════════════════════════════════
       TABS — Premium Pill Style
    ═══════════════════════════════════════════════ */
    [data-testid="stTabs"] {
        margin-top: 4px;
    }
    [data-testid="stTabs"] > div:first-child {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 5px;
        gap: 4px;
        backdrop-filter: blur(10px);
    }
    [data-testid="stTabs"] button[role="tab"] {
        background: transparent !important;
        border: none !important;
        border-radius: 10px !important;
        color: #64748b !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.84rem !important;
        padding: 9px 18px !important;
        transition: all 0.25s ease !important;
        box-shadow: none !important;
        transform: none !important;
        letter-spacing: 0.2px;
    }
    [data-testid="stTabs"] button[role="tab"]:hover {
        background: rgba(59, 130, 246, 0.08) !important;
        color: #93c5fd !important;
        transform: none !important;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #1e40af, #2563eb) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.35) !important;
    }
    /* Remove default tab underline indicator */
    [data-testid="stTabs"] [role="tablist"] > div[data-baseweb="tab-highlight"] {
        display: none !important;
    }
    [data-testid="stTabContent"] {
        padding-top: 24px;
    }

    /* ═══════════════════════════════════════════════
       TYPOGRAPHY
    ═══════════════════════════════════════════════ */
    .page-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 40%, #93c5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        padding-top: 8px;
        letter-spacing: -1px;
        line-height: 1.1;
    }
    .page-sub {
        font-size: 0.87rem;
        color: #64748b;
        margin-top: 8px;
        letter-spacing: 0.3px;
    }
    .section-title {
        font-family: 'Outfit', sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        color: #3b82f6;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 20px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-title::before {
        content: '';
        display: inline-block;
        width: 3px;
        height: 14px;
        background: linear-gradient(180deg, #3b82f6, #8b5cf6);
        border-radius: 2px;
        flex-shrink: 0;
    }

    /* ═══════════════════════════════════════════════
       METRIC CARDS — Glassmorphism with glow
    ═══════════════════════════════════════════════ */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(20, 30, 55, 0.9)) !important;
        border: 1px solid rgba(59, 130, 246, 0.15) !important;
        border-radius: 16px !important;
        padding: 20px 24px !important;
        box-shadow:
            0 1px 0 rgba(255, 255, 255, 0.04) inset,
            0 8px 32px rgba(0, 0, 0, 0.25),
            0 0 0 0px rgba(59, 130, 246, 0) !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease !important;
        position: relative;
        overflow: hidden;
    }
    [data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4);
        opacity: 0.8;
    }
    [data-testid="metric-container"]:hover {
        transform: translateY(-3px) !important;
        border-color: rgba(59, 130, 246, 0.3) !important;
        box-shadow:
            0 1px 0 rgba(255, 255, 255, 0.05) inset,
            0 16px 48px rgba(0, 0, 0, 0.35),
            0 0 30px rgba(59, 130, 246, 0.1) !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Outfit', sans-serif !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        letter-spacing: -0.5px !important;
        margin-top: 6px !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        color: #64748b !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
    }

    /* ═══════════════════════════════════════════════
       CARDS & PANELS
    ═══════════════════════════════════════════════ */
    .card-wrap {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 22px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    .card-wrap:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
    }

    .badge {
        font-size: 0.7rem;
        font-weight: 700;
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 20px;
        padding: 4px 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .insight-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 11px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        font-size: 0.85rem;
        color: #94a3b8;
        transition: background 0.15s;
    }
    .insight-row:last-child { border-bottom: none; }
    .insight-row:hover { background: rgba(255,255,255,0.02); border-radius: 6px; padding-left: 6px; padding-right: 6px; }
    .insight-val {
        font-weight: 700;
        color: #e2e8f0;
        font-size: 0.9rem;
    }

    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
        margin: 28px 0;
    }

    /* ═══════════════════════════════════════════════
       INPUTS & SELECTS
    ═══════════════════════════════════════════════ */
    [data-baseweb="input"], [data-baseweb="textarea"] {
        background: rgba(15, 23, 42, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        transition: all 0.2s ease !important;
    }
    [data-baseweb="input"]:focus-within,
    [data-baseweb="textarea"]:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
    }
    [data-baseweb="select"] > div {
        background: rgba(15, 23, 42, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
    }
    [data-testid="stTextArea"] textarea {
        background: rgba(15, 23, 42, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.88rem !important;
    }

    /* ═══════════════════════════════════════════════
       CURSOR ON DROPDOWNS
    ═══════════════════════════════════════════════ */
    [data-testid="stSelectbox"] *, [data-testid="stMultiSelect"] *,
    [data-baseweb="select"] *, [data-baseweb="popover"] *,
    [role="listbox"] *, [role="option"] *,
    ul[data-testid="stSelectboxVirtualDropdown"] *,
    .stSelectbox div, .stMultiSelect div { cursor: pointer !important; }

    /* ═══════════════════════════════════════════════
       BUTTONS — Gradient with glow
    ═══════════════════════════════════════════════ */
    .stButton > button,
    [data-testid="stFormSubmitButton"] > button {
        cursor: pointer !important;
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.87rem !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.25) !important;
        transition: all 0.25s ease !important;
        letter-spacing: 0.3px !important;
        position: relative !important;
        overflow: hidden !important;
    }
    .stButton > button::before,
    [data-testid="stFormSubmitButton"] > button::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
        transition: left 0.4s ease;
    }
    .stButton > button:hover::before { left: 100%; }
    .stButton > button:hover,
    [data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.4) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* ═══════════════════════════════════════════════
       RADIO BUTTONS
    ═══════════════════════════════════════════════ */
    [data-testid="stRadio"] label {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        border-radius: 8px !important;
        padding: 6px 14px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        font-size: 0.83rem !important;
    }
    [data-testid="stRadio"] label:hover {
        border-color: rgba(59, 130, 246, 0.3) !important;
        background: rgba(59, 130, 246, 0.08) !important;
    }

    /* ═══════════════════════════════════════════════
       DATAFRAME / TABLES
    ═══════════════════════════════════════════════ */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        border-radius: 14px !important;
        overflow: hidden !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2) !important;
    }
    [data-testid="stDataFrame"] table {
        border-collapse: separate !important;
        border-spacing: 0 !important;
    }

    /* ═══════════════════════════════════════════════
       INFO / WARNING / ERROR ALERTS
    ═══════════════════════════════════════════════ */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        backdrop-filter: blur(8px) !important;
    }

    /* ═══════════════════════════════════════════════
       SELECTBOX DROPDOWN
    ═══════════════════════════════════════════════ */
    [data-testid="stSelectbox"] > div > div > div {
        font-size: 0.88rem !important;
    }

    /* ═══════════════════════════════════════════════
       SPINNER
    ═══════════════════════════════════════════════ */
    [data-testid="stSpinner"] > div {
        border-color: #3b82f6 transparent transparent transparent !important;
    }

    /* ═══════════════════════════════════════════════
       PLOTLY CHART CONTAINERS
       NOTE: overflow must NOT be hidden — Plotly renders
       bar/pie labels outside the SVG frame; clipping them
       causes text to hide behind the card border.
    ═══════════════════════════════════════════════ */
    [data-testid="stPlotlyChart"] {
        border-radius: 14px !important;
        overflow: visible !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        background: rgba(10, 15, 30, 0.5) !important;
        backdrop-filter: blur(10px);
    }
    /* The inner SVG/canvas must still stay clipped to its own bounds */
    [data-testid="stPlotlyChart"] > div {
        overflow: visible !important;
    }

    /* ═══════════════════════════════════════════════
       MOBILE RESPONSIVE — OTA REVIEWS & GENERAL
    ═══════════════════════════════════════════════ */

    /* Sentiment bar label row: wrap on small screens */
    @media (max-width: 600px) {
        /* Sentiment distribution label row */
        div[style*="justify-content:space-between"],
        div[style*="justify-content: space-between"] {
            flex-wrap: wrap !important;
            gap: 4px !important;
        }

        /* Aspect cards header row: let score wrap below title */
        .aspect-card-header {
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 4px !important;
        }

        /* Review card footer: let source/date stack below badges */
        .review-card-footer {
            flex-wrap: wrap !important;
            gap: 4px !important;
        }

        /* Prevent any inline text from overflowing its container */
        [data-testid="stMarkdownContainer"] *,
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] span,
        [data-testid="stMarkdownContainer"] div {
            word-break: break-word !important;
            overflow-wrap: break-word !important;
        }

        /* Tab bar: allow horizontal scroll on tiny screens */
        [data-testid="stTabs"] > div:first-child {
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
        }

        /* Block container padding reduction */
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }

    /* ═══════════════════════════════════════════════
       SCROLLBAR
    ═══════════════════════════════════════════════ */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.25); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(59,130,246,0.5); }

    /* ═══════════════════════════════════════════════
       GLOW PULSE ANIMATION (for critical badges)
    ═══════════════════════════════════════════════ */
    @keyframes glow-pulse {
        0%, 100% { box-shadow: 0 0 8px rgba(239, 68, 68, 0.3); }
        50%       { box-shadow: 0 0 20px rgba(239, 68, 68, 0.6); }
    }
    .glow-red { animation: glow-pulse 2.5s ease-in-out infinite; }

    @keyframes shimmer {
        0%   { background-position: -200% center; }
        100% { background-position: 200% center; }
    }

    </style>
    """, unsafe_allow_html=True)


def ensure_auth(allowed_roles=None):
    """Handles session restoration, CSS hiding for non-logged users, and redirects.
    
    Injects an instant content-lock style BEFORE any redirect so the page
    content never becomes visible during the switch — preventing the flash
    of dashboard content that appears before the login page.
    """
    from sheets_db import get_hotel_by_id

    if not st.session_state.get("logged_in"):
        # INSTANT LOCK: kill the reveal animation and freeze opacity at 0
        # This fires synchronously before st.switch_page(), so no content flash.
        st.markdown("""
            <style>
                [data-testid="stMain"],
                [data-testid="stMainBlockContainer"] {
                    opacity: 0 !important;
                    animation: none !important;
                    visibility: hidden !important;
                }
                section[data-testid="stSidebar"],
                [data-testid="stSidebarNav"] { display: none !important; }
                button[kind="headerNoPadding"] { display: none !important; }
            </style>
        """, unsafe_allow_html=True)

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

    hotel = st.session_state.hotel
    if hotel.get("hotel_id") != "ADMIN":
        hide_admin_pages()
    if allowed_roles and hotel.get("hotel_id") not in allowed_roles:
        if "ADMIN" in allowed_roles and hotel.get("hotel_id") != "ADMIN":
            st.switch_page("app.py")
            st.stop()
    if st.query_params.get("hid") != hotel["hotel_id"]:
        st.query_params["hid"] = hotel["hotel_id"]
    return hotel


def sidebar_logo():
    st.sidebar.markdown("""
    <div style='display:flex;align-items:center;gap:12px;padding:4px 0 8px 0;'>
        <div style='
            width:40px;height:40px;
            background:linear-gradient(135deg,#1e3a8a,#3b82f6);
            border-radius:12px;display:flex;align-items:center;
            justify-content:center;font-size:20px;flex-shrink:0;
            box-shadow:0 4px 16px rgba(59,130,246,0.4);
        '>🏔️</div>
        <div>
            <div style='font-size:0.7rem;font-weight:700;letter-spacing:3px;
                        text-transform:uppercase;color:#3b82f6;line-height:1;'>Kashmir</div>
            <div style='font-size:1.1rem;font-weight:800;
                        color:#f1f5f9;line-height:1.3;letter-spacing:-0.3px;'>Analytics</div>
        </div>
    </div>
    <div style='height:1px;background:linear-gradient(90deg,rgba(59,130,246,0.4),transparent);margin-bottom:4px;'></div>
    """, unsafe_allow_html=True)


def render_custom_navigation():
    st.markdown("""
    <div style='margin-top:14px;margin-bottom:6px;'>
        <span style='font-size:0.65rem;color:#475569;text-transform:uppercase;letter-spacing:1.5px;font-weight:600;'>Navigation</span>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("app.py", label="Dashboard", icon="📊")
    st.page_link("pages/1_Add_Booking.py", label="Add Booking", icon="📝")
    st.page_link("pages/2_View_Bookings.py", label="View Bookings", icon="📋")
    
    # Only show Admin Panel to ADMIN role
    if st.session_state.get("hotel", {}).get("hotel_id") == "ADMIN":
        st.page_link("pages/3_Admin_Panel.py", label="Admin Panel", icon="⚙️")

def render_sidebar(hotel):
    """Renders the standard sidebar for all pages."""
    with st.sidebar:
        sidebar_logo()
        render_custom_navigation()
        st.divider()

        plan_label = "Full Access" if hotel.get("hotel_id") == "ADMIN" else hotel.get("plan", "Basic").title()
        st.markdown(f"""
        <div style='
            background:linear-gradient(135deg,rgba(15,23,42,0.9),rgba(20,30,60,0.8));
            border:1px solid rgba(59,130,246,0.15);
            border-radius:12px;padding:14px 16px;margin:12px 0;
            box-shadow:0 4px 20px rgba(0,0,0,0.2);
        '>
            <div style='font-size:0.65rem;color:#475569;text-transform:uppercase;
                        letter-spacing:1.5px;margin-bottom:5px;'>Logged in as</div>
            <div style='font-size:0.95rem;font-weight:700;color:#f1f5f9;'>{hotel["name"]}</div>
            <div style='
                display:inline-block;margin-top:5px;font-size:0.65rem;font-weight:700;
                background:linear-gradient(135deg,rgba(37,99,235,0.2),rgba(59,130,246,0.1));
                color:#60a5fa;border:1px solid rgba(59,130,246,0.25);
                border-radius:20px;padding:2px 10px;text-transform:uppercase;letter-spacing:1px;
            '>{plan_label} Plan</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown("""<a href='https://wa.me/918491828292' target='_blank' style='text-decoration:none;'>
            <button style='width:100%;border-radius:10px;padding:11px;
                           background:linear-gradient(135deg,#16a34a,#25d366);
                           color:white;border:none;cursor:pointer;font-weight:600;
                           font-size:0.85rem;box-shadow:0 4px 14px rgba(37,211,102,0.25);
                           transition:all 0.2s;'>
                💬 Contact Support
            </button></a>""", unsafe_allow_html=True)
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
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