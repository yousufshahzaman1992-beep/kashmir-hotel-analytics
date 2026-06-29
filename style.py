import streamlit as st


def apply_style():
    # ── PURE CSS DYNAMIC FLASH LOCK ──────────────────────────────────────────
    # We hide the entire app view container by default. It is only revealed
    # (with a smooth fade-in) when the Python script successfully completes
    # execution and appends `<div class="app-unlocked"></div>` to the DOM.
    # This prevents any raw content flash during websocket updates or redirects.
    # ── JS: detect Streamlit's active theme and stamp data-theme on <html> ────
    # Streamlit injects --background-color on :root via its own <style> tag.
    # We read that computed value (luminance test) to decide dark vs light
    # and set data-theme, which drives our [data-theme] CSS variable blocks.
    st.markdown("""
<script>
(function(){
  'use strict';
  var _last = null;

  function _lum(hex) {
    hex = hex.replace('#','');
    if (hex.length===3) hex=hex[0]+hex[0]+hex[1]+hex[1]+hex[2]+hex[2];
    var r=parseInt(hex.substr(0,2),16),
        g=parseInt(hex.substr(2,2),16),
        b=parseInt(hex.substr(4,2),16);
    return (0.299*r+0.587*g+0.114*b)/255;
  }

  function _detect(){
    // Streamlit injects --background-color on :root; we do NOT set that var,
    // so getComputedStyle gives us Streamlit's raw value.
    var bg='';
    try{ bg=getComputedStyle(document.documentElement)
            .getPropertyValue('--background-color').trim(); }catch(e){}

    var theme='dark';
    if(bg && bg.startsWith('#')){
      theme = _lum(bg) > 0.5 ? 'light' : 'dark';
    } else if(bg && bg.startsWith('rgb')){
      var m=bg.match(/\\d+/g);
      if(m && m.length>=3){
        var l=(0.299*+m[0]+0.587*+m[1]+0.114*+m[2])/255;
        theme = l>0.5?'light':'dark';
      }
    }

    if(theme!==_last){
      _last=theme;
      document.documentElement.setAttribute('data-theme',theme);
    }
  }

  // Run immediately & after short delays to catch Streamlit's style injection
  _detect();
  [50,150,400,800,1500,3000].forEach(function(d){setTimeout(_detect,d);});

  // Watch head for Streamlit re-injecting its theme <style>
  var obs=new MutationObserver(function(){setTimeout(_detect,30);});
  obs.observe(document.head,{childList:true,subtree:true});

  // Also catch localStorage changes (Streamlit theme toggle writes localStorage)
  window.addEventListener('storage',function(){setTimeout(_detect,50);});
})();
</script>
""", unsafe_allow_html=True)

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
       GLOBAL BASE & THEMES
    ═══════════════════════════════════════════════ */
    *, *::before, *::after { box-sizing: border-box; }


    /* ── Dark mode variables (default — JS will confirm via data-theme) ── */
    :root,
    html[data-theme="dark"] {
        color-scheme: dark;
        --bg-color:           #050e0b;
        --secondary-bg-color: #0a1814;
        --text-color:         #e2e8f0;
        --primary-color:      #10b981;
        --text-muted:         #647974;
        --text-highlight:     #fbbf24;
        --text-active:        #34d399;
        --border-color:       rgba(255,255,255,0.07);
        --border-card:        rgba(16,185,129,0.15);
        --card-bg:            rgba(11,26,22,0.95);
        --card-bg-glow:       rgba(11,26,22,0.9);
        --card-hover-shadow:  rgba(0,0,0,0.4);
        --tab-bar-bg:         rgba(11,26,22,0.7);
        --tab-button-text:    #647974;
        --tab-button-active-bg:   linear-gradient(135deg,#047857,#10b981);
        --tab-button-active-text: #ffffff;
        --sidebar-bg:         linear-gradient(180deg,#06120e 0%,#0a1814 60%,#06120e 100%);
        --sidebar-border:     rgba(16,185,129,0.08);
        --dropdown-bg:        #0a1814;
        --dropdown-text:      #e2e8f0;
        --dropdown-hover-bg:  #047857;
        --dropdown-hover-text:#ffffff;
        --button-bg:          linear-gradient(135deg,#064e3b 0%,#10b981 50%,#047857 100%);
        --button-text:        #ffffff;
        --button-shadow:      rgba(16,185,129,0.2);
        --button-hover-shadow:rgba(16,185,129,0.35);
        --title-gradient:     linear-gradient(135deg,#ffffff 0%,#e2e8f0 40%,#a7f3d0 100%);
        --metric-value:       #ffffff;
        --input-bg:           #0a1814;
        --input-border:       rgba(255,255,255,0.1);
        --input-text:         #e2e8f0;
        --input-focus-shadow: rgba(16, 185, 129, 0.2);
        --mesh-bg-gradient:
            radial-gradient(ellipse 80% 60% at 10% 0%,rgba(16,185,129,0.08) 0%,transparent 60%),
            radial-gradient(ellipse 60% 50% at 90% 100%,rgba(245,158,11,0.06) 0%,transparent 60%),
            radial-gradient(ellipse 40% 40% at 50% 50%,rgba(16,185,129,0.03) 0%,transparent 70%);
    }

    /* ── Light mode variables — pure white / dark text ── */
    html[data-theme="light"] {
        color-scheme: light;
        --bg-color:           #ffffff;
        --secondary-bg-color: #f4f7f6;
        --text-color:         #0f172a;
        --primary-color:      #047857;
        --text-muted:         #64748b;
        --text-highlight:     #b45309;
        --text-active:        #059669;
        --border-color:       rgba(0,0,0,0.09);
        --border-card:        rgba(4,120,87,0.15);
        --card-bg:            #ffffff;
        --card-bg-glow:       #ffffff;
        --card-hover-shadow:  rgba(0,0,0,0.07);
        --tab-bar-bg:         rgba(244,247,246,0.9);
        --tab-button-text:    #475569;
        --tab-button-active-bg:   linear-gradient(135deg,#047857,#059669);
        --tab-button-active-text: #ffffff;
        --sidebar-bg:         linear-gradient(180deg,#f4f7f6 0%,#eef2f1 60%,#f4f7f6 100%);
        --sidebar-border:     rgba(4,120,87,0.08);
        --dropdown-bg:        #ffffff;
        --dropdown-text:      #0f172a;
        --dropdown-hover-bg:  #d1fae5;
        --dropdown-hover-text:#065f46;
        --button-bg:          linear-gradient(135deg,#047857 0%,#10b981 50%,#059669 100%);
        --button-text:        #ffffff;
        --button-shadow:      rgba(4,120,87,0.15);
        --button-hover-shadow:rgba(4,120,87,0.25);
        --title-gradient:     linear-gradient(135deg,#0f172a 0%,#064e3b 60%,#047857 100%);
        --metric-value:       #0f172a;
        --input-bg:           #ffffff;
        --input-border:       rgba(0,0,0,0.12);
        --input-text:         #0f172a;
        --input-focus-shadow: rgba(4, 120, 87, 0.12);
        --mesh-bg-gradient:   none;
    }

    /* ── Base element resets for both themes ── */
    html, body,
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    .main, .stApp {
        background-color: var(--bg-color) !important;
        background:       var(--bg-color) !important;
        color:            var(--text-color) !important;
        font-family: 'Inter', sans-serif;
    }

    /* ── Light-mode total-white hardening ─────────────────────────── */
    /* Every panel, column, and container in light mode gets white bg  */
    html[data-theme="light"] [data-testid="stApp"],
    html[data-theme="light"] [data-testid="stAppViewContainer"],
    html[data-theme="light"] [data-testid="stMain"],
    html[data-theme="light"] [data-testid="stMainBlockContainer"],
    html[data-theme="light"] [data-testid="stVerticalBlock"],
    html[data-theme="light"] [data-testid="stHorizontalBlock"],
    html[data-theme="light"] [data-testid="column"],
    html[data-theme="light"] .block-container,
    html[data-theme="light"] .element-container,
    html[data-theme="light"] section[data-testid="stSidebar"],
    html[data-theme="light"] [data-testid="stSidebarContent"] {
        background-color: var(--bg-color) !important;
        background:       var(--bg-color) !important;
        color:            var(--text-color) !important;
    }
    html[data-theme="light"] section[data-testid="stSidebar"],
    html[data-theme="light"] [data-testid="stSidebarContent"] {
        background-color: var(--secondary-bg-color) !important;
        background:       var(--secondary-bg-color) !important;
    }
    /* All text elements in light mode */
    html[data-theme="light"] p,
    html[data-theme="light"] h1, html[data-theme="light"] h2,
    html[data-theme="light"] h3, html[data-theme="light"] h4,
    html[data-theme="light"] h5, html[data-theme="light"] h6,
    html[data-theme="light"] span, html[data-theme="light"] label,
    html[data-theme="light"] div,
    html[data-theme="light"] [data-testid="stMarkdownContainer"],
    html[data-theme="light"] [data-testid="stMarkdownContainer"] p,
    html[data-theme="light"] [data-testid="stMarkdownContainer"] span,
    html[data-theme="light"] [data-testid="stMarkdownContainer"] li,
    html[data-theme="light"] [data-testid="stWidgetLabel"] p,
    html[data-theme="light"] [data-testid="stMetricLabel"],
    html[data-theme="light"] [data-testid="stMetricLabel"] p,
    html[data-theme="light"] [data-testid="stMetricDelta"] {
        color: var(--text-color) !important;
    }
    /* Light mode metric values */
    html[data-theme="light"] [data-testid="stMetricValue"],
    html[data-theme="light"] [data-testid="stMetricValue"] div {
        color: var(--metric-value) !important;
    }
    /* Light mode inputs */
    html[data-theme="light"] input,
    html[data-theme="light"] textarea,
    html[data-theme="light"] select,
    html[data-theme="light"] [data-baseweb="input"] input,
    html[data-theme="light"] [data-baseweb="textarea"] textarea,
    html[data-theme="light"] [data-baseweb="select"] input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border-color: rgba(0,0,0,0.15) !important;
    }
    html[data-theme="light"] [data-baseweb="input"],
    html[data-theme="light"] [data-baseweb="textarea"],
    html[data-theme="light"] [data-baseweb="select"],
    html[data-theme="light"] [data-baseweb="popover"],
    html[data-theme="light"] [data-testid="stTextInput"] > div,
    html[data-theme="light"] [data-testid="stTextArea"] > div,
    html[data-theme="light"] [data-testid="stSelectbox"] > div > div {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }
    /* Light mode autofill */
    html[data-theme="light"] input:-webkit-autofill,
    html[data-theme="light"] input:-webkit-autofill:hover,
    html[data-theme="light"] input:-webkit-autofill:focus {
        -webkit-box-shadow: 0 0 0 1000px #ffffff inset !important;
        -webkit-text-fill-color: #0f172a !important;
        box-shadow: 0 0 0 1000px #ffffff inset !important;
    }
    /* Light mode tabs */
    html[data-theme="light"] [data-testid="stTabs"] > div:first-child {
        background: rgba(241,245,249,0.9) !important;
    }
    html[data-theme="light"] [data-testid="stTabs"] button[role="tab"] {
        color: #475569 !important;
    }
    html[data-theme="light"] [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: #ffffff !important;
        background: linear-gradient(135deg,#2563eb,#3b82f6) !important;
    }
    /* Light mode expander */
    html[data-theme="light"] [data-testid="stExpander"],
    html[data-theme="light"] details,
    html[data-theme="light"] summary {
        background-color: #ffffff !important;
        border-color: rgba(0,0,0,0.09) !important;
        color: #0f172a !important;
    }
    /* Light mode dataframe */
    html[data-theme="light"] [data-testid="stDataFrame"],
    html[data-theme="light"] [data-testid="stDataFrame"] * {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }
    /* Light mode metric cards */
    html[data-theme="light"] [data-testid="stMetric"] {
        background: #f8fafc !important;
        border-color: rgba(0,0,0,0.08) !important;
    }
    /* Light mode header */
    html[data-theme="light"] [data-testid="stHeader"],
    html[data-theme="light"] header {
        background-color: #ffffff !important;
        background: #ffffff !important;
        border-bottom-color: rgba(0,0,0,0.08) !important;
    }
    html[data-theme="light"] [data-testid="stHeader"] button,
    html[data-theme="light"] header button,
    html[data-theme="light"] [data-testid="stHeader"] svg,
    html[data-theme="light"] header svg {
        color: #0f172a !important;
        fill: #0f172a !important;
    }
    /* Light mode dividers */
    html[data-theme="light"] hr { border-color: rgba(0,0,0,0.1) !important; }
    /* Light mode selectbox dropdown popup */
    html[data-theme="light"] [data-testid="stSelectbox"] ul,
    html[data-theme="light"] [role="listbox"],
    html[data-theme="light"] [role="option"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }
    /* Light mode plotly chart containers */
    html[data-theme="light"] [data-testid="stPlotlyChart"] {
        background: #ffffff !important;
        border-color: rgba(0,0,0,0.09) !important;
    }
    /* Light mode page links */
    html[data-theme="light"] [data-testid="stPageLink"] a,
    html[data-theme="light"] [data-testid="stPageLink"] p,
    html[data-theme="light"] [data-testid="stPageLink"] span {
        color: #0f172a !important;
    }
    html[data-theme="light"] [data-testid="stPageLink"][aria-current="page"] a,
    html[data-theme="light"] [data-testid="stPageLink"][aria-current="page"] p {
        color: #2563eb !important;
    }
    /* Light mode buttons */
    html[data-theme="light"] [data-testid="stBaseButton-secondary"] {
        background: #f1f5f9 !important;
        color: #0f172a !important;
        border-color: rgba(0,0,0,0.12) !important;
    }
    html[data-theme="light"] [data-testid="stBaseButton-secondary"]:hover {
        background: #e2e8f0 !important;
    }
    /* Light mode alerts */
    html[data-theme="light"] [data-testid="stAlert"] {
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }


    /* Background mesh - promoted to composite layer for scrolling performance */
    [data-testid="stAppViewContainer"]::before {
        content: '';
        position: fixed;
        inset: 0;
        background: var(--mesh-bg-gradient);
        pointer-events: none;
        z-index: 0;
        transform: translate3d(0, 0, 0);
        will-change: transform;
    }

    /* ═══════════════════════════════════════════════
       HEADER & MOBILE TOP STRIP
    ═══════════════════════════════════════════════ */
    [data-testid="stHeader"], header {
        background: var(--bg-color) !important;
        background-color: var(--bg-color) !important;
        border-bottom: 1px solid var(--border-color) !important;
        color: var(--text-color) !important;
    }
    [data-testid="stHeader"] button, header button,
    [data-testid="stHeader"] svg, header svg {
        color: var(--text-color) !important;
        fill: var(--text-color) !important;
    }

    /* st.page_link() — sidebar navigation link text colors */
    [data-testid="stPageLink"] a,
    [data-testid="stPageLink"] a p,
    [data-testid="stPageLink"] a span,
    [data-testid="stPageLink"] p,
    [data-testid="stPageLink"] span {
        color: var(--text-color) !important;
        text-decoration: none !important;
        opacity: 0.8;
    }
    [data-testid="stPageLink"]:hover a,
    [data-testid="stPageLink"]:hover a p,
    [data-testid="stPageLink"]:hover a span {
        color: var(--text-highlight) !important;
        opacity: 1;
    }
    [data-testid="stPageLink"][aria-current="page"] a,
    [data-testid="stPageLink"][aria-current="page"] a p,
    [data-testid="stPageLink"][aria-current="page"] a span {
        color: var(--text-active) !important;
        font-weight: 600 !important;
        opacity: 1;
    }

    /* ═══════════════════════════════════════════════
       SIDEBAR
    ═══════════════════════════════════════════════ */
    [data-testid="stSidebar"] {
        background: var(--sidebar-bg) !important;
        border-right: 1px solid var(--sidebar-border) !important;
        box-shadow: 4px 0 30px var(--card-hover-shadow);
    }
    [data-testid="stSidebarNav"] { padding-top: 10px; }
    [data-testid="stSidebarNav"] li a {
        border-radius: 10px;
        margin: 3px 10px;
        padding: 10px 14px;
        font-weight: 500;
        font-size: 0.88rem;
        color: var(--text-color) !important;
        transition: all 0.25s ease;
        opacity: 0.8;
    }
    [data-testid="stSidebarNav"] li a:hover {
        background: rgba(59, 130, 246, 0.1) !important;
        color: var(--text-highlight) !important;
        transform: translateX(3px);
        opacity: 1;
    }
    [data-testid="stSidebarNav"] li a[data-selected="true"] {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.25), rgba(59, 130, 246, 0.12)) !important;
        color: var(--text-active) !important;
        border-left: 3px solid var(--primary-color);
        font-weight: 600;
        opacity: 1;
    }

    /* Custom sidebar elements */
    .sidebar-logo-container {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 4px 0 8px 0;
    }
    .sidebar-logo-icon {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #064e3b, #10b981);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        flex-shrink: 0;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3);
    }
    .sidebar-logo-sub {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: var(--primary-color);
        line-height: 1;
    }
    .sidebar-logo-main {
        font-size: 1.1rem;
        font-weight: 800;
        color: var(--text-color);
        line-height: 1.3;
        letter-spacing: -0.3px;
    }
    .sidebar-logo-divider {
        height: 1px;
        background: linear-gradient(90deg, rgba(59, 130, 246, 0.4), transparent);
        margin-bottom: 4px;
    }

    .logged-in-box {
        background: var(--secondary-bg-color);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 14px 16px;
        margin: 12px 0;
        box-shadow: 0 4px 20px var(--card-hover-shadow);
    }
    .logged-in-box-label {
        font-size: 0.65rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 5px;
    }
    .logged-in-box-name {
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--text-color);
    }
    .logged-in-box-plan {
        display: inline-block;
        margin-top: 5px;
        font-size: 0.65rem;
        font-weight: 700;
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.2), rgba(59, 130, 246, 0.1));
        color: var(--primary-color);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 20px;
        padding: 2px 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .support-btn {
        width: 100%;
        border-radius: 10px;
        padding: 11px;
        background: linear-gradient(135deg, #16a34a, #25d366);
        color: white !important;
        border: none;
        cursor: pointer;
        font-weight: 600;
        font-size: 0.85rem;
        box-shadow: 0 4px 14px rgba(37, 211, 102, 0.25);
        transition: all 0.2s;
    }
    .support-btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(37, 211, 102, 0.4);
    }

    /* ═══════════════════════════════════════════════
       LAYOUT
    ═══════════════════════════════════════════════ */
    /* Narrow sidebar so the dashboard gets maximum horizontal space */
    [data-testid="stSidebar"] {
        min-width: 220px !important;
        max-width: 220px !important;
        width:     220px !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        width: 220px !important;
    }

    .block-container {
        padding-top:    3rem !important;
        padding-bottom: 2rem !important;
        padding-left:   1.5rem !important;
        padding-right:  1.5rem !important;
        max-width:      100% !important;
    }

    /* ═══════════════════════════════════════════════
       TABS — Premium Pill Style
    ═══════════════════════════════════════════════ */
    [data-testid="stTabs"] {
        margin-top: 4px;
    }
    [data-testid="stTabs"] > div:first-child {
        background: var(--tab-bar-bg);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 5px;
        gap: 4px;
    }
    [data-testid="stTabs"] button[role="tab"] {
        background: transparent !important;
        border: none !important;
        border-radius: 10px !important;
        color: var(--tab-button-text) !important;
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
        color: var(--text-highlight) !important;
        transform: none !important;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: var(--tab-button-active-bg) !important;
        color: var(--tab-button-active-text) !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 16px var(--button-shadow) !important;
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
        background: var(--title-gradient);
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
        color: var(--text-muted);
        margin-top: 8px;
        letter-spacing: 0.3px;
    }
    .section-title {
        font-family: 'Outfit', sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        color: var(--primary-color);
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
        background: linear-gradient(180deg, var(--primary-color), #8b5cf6);
        border-radius: 2px;
        flex-shrink: 0;
    }

    /* ═══════════════════════════════════════════════
       METRIC CARDS — Glassmorphism with glow
    ═══════════════════════════════════════════════ */
    [data-testid="metric-container"] {
        background: var(--card-bg) !important;
        border: 1px solid var(--border-card) !important;
        border-radius: 16px !important;
        padding: 20px 24px !important;
        box-shadow:
            0 1px 0 rgba(255, 255, 255, 0.04) inset,
            0 8px 32px var(--card-hover-shadow),
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
        background: linear-gradient(90deg, var(--primary-color), #8b5cf6, #06b6d4);
        opacity: 0.8;
    }
    [data-testid="metric-container"]:hover {
        transform: translateY(-3px) !important;
        border-color: rgba(59, 130, 246, 0.3) !important;
        box-shadow:
            0 1px 0 rgba(255, 255, 255, 0.05) inset,
            0 16px 48px var(--card-hover-shadow),
            0 0 30px rgba(59, 130, 246, 0.1) !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Outfit', sans-serif !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: var(--metric-value) !important;
        letter-spacing: -0.5px !important;
        margin-top: 6px !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        color: var(--text-muted) !important;
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
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0 8px 32px var(--card-hover-shadow);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    .card-wrap:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px var(--card-hover-shadow);
    }

    .badge {
        font-size: 0.7rem;
        font-weight: 700;
        background: rgba(59, 130, 246, 0.15);
        color: var(--primary-color);
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
        border-bottom: 1px solid var(--border-color);
        font-size: 0.85rem;
        color: var(--text-muted);
        transition: background 0.15s;
    }
    .insight-row:last-child { border-bottom: none; }
    .insight-row:hover { background: rgba(59, 130, 246, 0.05); border-radius: 6px; padding-left: 6px; padding-right: 6px; }
    .insight-val {
        font-weight: 700;
        color: var(--text-color);
        font-size: 0.9rem;
    }

    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 28px 0;
    }

    /* ═══════════════════════════════════════════════
       INPUTS & SELECTS
    ═══════════════════════════════════════════════ */
    /* Target both BaseWeb and general Streamlit input container wrappers to lock background */
    [data-baseweb="base-input"],
    [data-baseweb="input"],
    [data-baseweb="textarea"],
    [data-baseweb="select"] > div,
    .stTextInput > div > div,
    .stNumberInput > div > div,
    .stTextArea > div > div,
    .stDateInput > div > div,
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: var(--secondary-bg-color) !important;
        background-color: var(--secondary-bg-color) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
        color: var(--text-color) !important;
        transition: all 0.2s ease !important;
    }
    
    /* Focus styles */
    [data-baseweb="base-input"]:focus-within,
    [data-baseweb="input"]:focus-within,
    [data-baseweb="textarea"]:focus-within,
    [data-baseweb="select"]:focus-within,
    .stTextInput > div > div:focus-within,
    .stNumberInput > div > div:focus-within,
    .stTextArea > div > div:focus-within,
    .stDateInput > div > div:focus-within,
    .stSelectbox > div > div:focus-within,
    .stMultiSelect > div > div:focus-within {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px var(--input-focus-shadow) !important;
    }

    /* Target raw HTML input and textarea elements inside Streamlit widgets and force dynamic styling */
    [data-baseweb="base-input"] input,
    [data-baseweb="input"] input, 
    [data-baseweb="textarea"] textarea,
    [data-testid="stTextArea"] textarea,
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    .stDateInput input,
    input, 
    textarea,
    select {
        background-color: var(--secondary-bg-color) !important;
        background: var(--secondary-bg-color) !important;
        color: var(--text-color) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.88rem !important;
    }

    /* Prevent browser autofill / autocomplete changing input background to white/yellow */
    input:-webkit-autofill,
    input:-webkit-autofill:hover, 
    input:-webkit-autofill:focus, 
    input:-webkit-autofill:active,
    input:-internal-autofill-selected {
        -webkit-box-shadow: 0 0 0px 1000px var(--secondary-bg-color) inset !important;
        -webkit-text-fill-color: var(--text-color) !important;
        box-shadow: 0 0 0px 1000px var(--secondary-bg-color) inset !important;
        transition: background-color 5000s ease-in-out 0s !important;
    }

    /* Placeholder text style override */
    input::placeholder, textarea::placeholder, [data-baseweb="input"] input::placeholder {
        color: var(--text-muted) !important;
        opacity: 0.8 !important;
    }

    /* Dropdown popover container & options list (selectbox & multiselect options) */
    [data-baseweb="popover"], 
    [role="listbox"], 
    [role="option"], 
    ul[data-testid="stSelectboxVirtualDropdown"],
    ul[data-testid="stSelectboxVirtualDropdown"] *,
    div[data-baseweb="popover"] * {
        background-color: var(--dropdown-bg) !important;
        background: var(--dropdown-bg) !important;
        color: var(--dropdown-text) !important;
    }

    /* Dropdown option hover & selected states */
    [role="option"]:hover,
    [role="option"][aria-selected="true"],
    [data-baseweb="popover"] li:hover {
        background-color: var(--dropdown-hover-bg) !important;
        background: var(--dropdown-hover-bg) !important;
        color: var(--dropdown-hover-text) !important;
    }

    /* Date picker calendar */
    [data-baseweb="calendar"] *,
    [data-baseweb="calendar"] {
        background-color: var(--secondary-bg-color) !important;
        background: var(--secondary-bg-color) !important;
        color: var(--text-color) !important;
    }
    [data-baseweb="calendar"] [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: #ffffff !important;
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
        background: var(--button-bg) !important;
        color: var(--button-text) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.87rem !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        box-shadow: 0 4px 15px var(--button-shadow) !important;
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
        box-shadow: 0 8px 25px var(--button-hover-shadow) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* ═══════════════════════════════════════════════
       RADIO BUTTONS
    ═══════════════════════════════════════════════ */
    [data-testid="stRadio"] label {
        background: var(--card-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 6px 14px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        font-size: 0.83rem !important;
        color: var(--text-color) !important;
    }
    [data-testid="stRadio"] label:hover {
        border-color: var(--primary-color) !important;
        background: rgba(59, 130, 246, 0.08) !important;
    }

    /* ═══════════════════════════════════════════════
       DATAFRAME / TABLES
    ═══════════════════════════════════════════════ */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border-color) !important;
        border-radius: 14px !important;
        overflow: hidden !important;
        box-shadow: 0 8px 30px var(--card-hover-shadow) !important;
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
        border: 1px solid var(--border-color) !important;
        color: var(--text-color) !important;
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
        border-color: var(--primary-color) transparent transparent transparent !important;
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
        border: 1px solid var(--border-color) !important;
        background: var(--card-bg) !important;
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
    ::-webkit-scrollbar-track { background: rgba(59,130,246,0.02); border-radius: 10px; }
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

    /* ═══════════════════════════════════════════════
       PREMIUM ENHANCEMENTS — Page entry animations,
       richer cards, styled progress, checkboxes
    ═══════════════════════════════════════════════ */

    /* Smooth page-entry fade+slide for main block */
    [data-testid="stMainBlockContainer"] {
        animation: pageEntry 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
    }
    @keyframes pageEntry {
        from { opacity: 0; transform: translateY(14px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* Stagger-fade for vertical blocks inside main */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        animation: fadeUp 0.4s ease both;
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── Metric cards: bigger glow, animated top stripe ── */
    [data-testid="metric-container"] {
        position: relative;
        overflow: hidden;
        transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1),
                    box-shadow 0.3s ease, border-color 0.3s ease !important;
    }
    [data-testid="metric-container"]::after {
        content: '';
        position: absolute;
        inset: 0;
        background: radial-gradient(ellipse 80% 60% at 50% 0%,
            rgba(59,130,246,0.06) 0%, transparent 70%);
        pointer-events: none;
    }
    [data-testid="metric-container"]:hover {
        transform: translateY(-5px) scale(1.012) !important;
        border-color: rgba(59,130,246,0.35) !important;
        box-shadow:
            0 1px 0 rgba(255,255,255,0.06) inset,
            0 20px 60px rgba(0,0,0,0.4),
            0 0 40px rgba(59,130,246,0.15) !important;
    }

    /* ── Streamlit native st.progress() — make it premium ── */
    [data-testid="stProgressBar"] > div {
        height: 10px !important;
        border-radius: 6px !important;
        background: var(--border-color) !important;
        overflow: hidden !important;
    }
    [data-testid="stProgressBar"] > div > div {
        height: 10px !important;
        border-radius: 6px !important;
        background: linear-gradient(90deg,
            #059669 0%, #10b981 50%, #fbbf24 100%) !important;
        background-size: 200% 100% !important;
        animation: progressShimmer 2.5s linear infinite !important;
        box-shadow: 0 0 12px rgba(16,185,129,0.4) !important;
        transition: width 0.6s cubic-bezier(0.4,0,0.2,1) !important;
    }
    @keyframes progressShimmer {
        0%   { background-position: 200% center; }
        100% { background-position: -200% center; }
    }

    /* ── Checkboxes — larger, coloured, satisfying ── */
    [data-testid="stCheckbox"] > label {
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        padding: 9px 12px !important;
        border-radius: 10px !important;
        border: 1px solid transparent !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        font-size: 0.87rem !important;
    }
    [data-testid="stCheckbox"] > label:hover {
        background: rgba(16,185,129,0.07) !important;
        border-color: rgba(16,185,129,0.2) !important;
    }
    [data-testid="stCheckbox"] input[type="checkbox"] {
        width: 18px !important;
        height: 18px !important;
        accent-color: var(--primary-color) !important;
        cursor: pointer !important;
    }

    /* ── Section titles — animated left-bar glow ── */
    .section-title {
        position: relative;
    }
    .section-title::before {
        background: linear-gradient(180deg, var(--primary-color), var(--text-highlight)) !important;
        box-shadow: 0 0 8px rgba(16,185,129,0.4) !important;
        transition: height 0.3s ease !important;
    }

    /* ── Sidebar — premium glow accent at top ── */
    [data-testid="stSidebar"]::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #064e3b, #10b981, #fbbf24);
        border-radius: 0 0 4px 4px;
        opacity: 0.9;
    }
    [data-testid="stSidebar"] {
        position: relative;
        box-shadow: 4px 0 40px rgba(0,0,0,0.4), 0 0 1px rgba(16,185,129,0.2) !important;
    }

    /* ── Sidebar nav links — pill with glow on active ── */
    [data-testid="stPageLink"][aria-current="page"] a {
        box-shadow: 0 0 16px rgba(59,130,246,0.15) !important;
    }

    /* ── Alert boxes with coloured left border ── */
    [data-testid="stAlert"][data-baseweb="notification"] {
        border-left: 4px solid var(--primary-color) !important;
        border-radius: 10px !important;
        padding-left: 16px !important;
    }

    /* ── Divider — glowing gradient ── */
    .divider {
        background: linear-gradient(90deg,
            transparent 0%, rgba(59,130,246,0.4) 30%,
            rgba(139,92,246,0.4) 70%, transparent 100%) !important;
        height: 1px !important;
    }

    /* ── Expander — polished header ── */
    [data-testid="stExpander"] summary {
        border-radius: 10px !important;
        padding: 12px 16px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        transition: background 0.2s ease !important;
    }
    [data-testid="stExpander"] summary:hover {
        background: rgba(59,130,246,0.06) !important;
    }
    [data-testid="stExpander"] {
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    /* ── Floating background orb (static & hardware accelerated for scrolling performance) ── */
    [data-testid="stAppViewContainer"]::after {
        content: '';
        position: fixed;
        width: 600px;
        height: 600px;
        border-radius: 50%;
        background: radial-gradient(circle,
            rgba(16,185,129,0.04) 0%, transparent 70%);
        bottom: -200px; right: -100px;
        pointer-events: none;
        z-index: 0;
        transform: translate3d(0, 0, 0);
        will-change: transform;
    }

    /* ── Success message styling ── */
    [data-testid="stSuccess"] {
        border-left: 4px solid #10b981 !important;
        background: rgba(16,185,129,0.08) !important;
        border-radius: 10px !important;
    }
    [data-testid="stWarning"] {
        border-left: 4px solid #f59e0b !important;
        background: rgba(245,158,11,0.08) !important;
        border-radius: 10px !important;
    }
    [data-testid="stError"] {
        border-left: 4px solid #ef4444 !important;
        background: rgba(239,68,68,0.08) !important;
        border-radius: 10px !important;
    }
    [data-testid="stInfo"] {
        border-left: 4px solid #10b981 !important;
        background: rgba(16,185,129,0.08) !important;
        border-radius: 10px !important;
    }

    /* ── Tabs — hover lift ── */
    [data-testid="stTabs"] button[role="tab"]:hover {
        transform: translateY(-1px) !important;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        box-shadow: 0 4px 20px var(--button-shadow) !important;
    }

    /* ── Badge in sidebar logged-in-box ── */
    .logged-in-box {
        background: linear-gradient(135deg,
            rgba(11,26,22,0.9) 0%,
            rgba(16,185,129,0.1) 100%) !important;
        border-color: rgba(16,185,129,0.15) !important;
        position: relative;
        overflow: hidden;
    }
    .logged-in-box::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(16,185,129,0.4), transparent);
    }

    /* ── Button secondary style ── */
    [data-testid="stBaseButton-secondary"] {
        background: transparent !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-color) !important;
    }
    [data-testid="stBaseButton-secondary"]:hover {
        border-color: rgba(16,185,129,0.3) !important;
        background: rgba(16,185,129,0.05) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Tooltip / help icon ── */
    [data-testid="stTooltipHoverTarget"] svg {
        color: var(--text-muted) !important;
        opacity: 0.6;
        transition: opacity 0.2s;
    }
    [data-testid="stTooltipHoverTarget"]:hover svg { opacity: 1; }

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
    <div class='sidebar-logo-container'>
        <div class='sidebar-logo-icon'>🏔️</div>
        <div>
            <div class='sidebar-logo-sub'>Kashmir</div>
            <div class='sidebar-logo-main'>Analytics</div>
        </div>
    </div>
    <div class='sidebar-logo-divider'></div>
    """, unsafe_allow_html=True)


def render_custom_navigation():
    st.markdown("""
    <div style='margin-top:14px;margin-bottom:6px;'>
        <span style='font-size:0.65rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1.5px;font-weight:600;'>Navigation</span>
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
        <div class='logged-in-box'>
            <div class='logged-in-box-label'>Logged in as</div>
            <div class='logged-in-box-name'>{hotel["name"]}</div>
            <div class='logged-in-box-plan'>{plan_label} Plan</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown("""<a href='https://wa.me/918491828292' target='_blank' style='text-decoration:none;'>
            <button class='support-btn'>
                💬 Contact Support
            </button></a>""", unsafe_allow_html=True)
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Logout", width='stretch'):
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