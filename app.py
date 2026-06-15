import streamlit as st
import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from login import show_login
from style import apply_style, render_sidebar, ensure_auth
from sheets_db import get_hotel_by_id, load_bookings

st.set_page_config(page_title="Kashmir Hotel Analytics", page_icon="🏔️", layout="wide")
apply_style()
# ── Hide admin pages from non-admin users ─────────────────
if st.session_state.get("logged_in"):
    if st.session_state.hotel.get("hotel_id") != "ADMIN":
        st.markdown("""
        <style>
        /* Hide Admin Panel and Setup Account from sidebar */
        [data-testid="stSidebarNav"] a[href*="3_Admin"],
        [data-testid="stSidebarNav"] a[href*="Admin_Panel"],
        [data-testid="stSidebarNav"] a[href*="4_Setup"],
        [data-testid="stSidebarNav"] a[href*="setup_account"],
        [data-testid="stSidebarNav"] a[href*="Setup_Account"] {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
if not st.session_state.get("logged_in"):
    # ── Handle Invite Links ──────────────────────────────
    invite_token = st.query_params.get("invite")
    if invite_token:
        st.session_state["invite_token"] = invite_token
        st.switch_page("pages/4_Setup_Account.py")
        st.stop()

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
    
    show_login()
    st.stop()

hotel = ensure_auth()
render_sidebar(hotel)

# ── Dashboard Overview ────────────────────────────────────
st.markdown(f"<p class='page-title'>🏔️ {hotel['name']}</p>", unsafe_allow_html=True)
st.markdown("<p class='page-sub'>Real-time hotel performance overview.</p>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

if hotel["hotel_id"] == "ADMIN":
    st.info("👋 Welcome, Administrator. Use the sidebar to navigate to the Admin Panel.")
else:
    df = load_bookings(hotel["hotel_id"])
    if df.empty:
        st.info("No bookings recorded yet.")
    else:
        m1, m2 = st.columns(2)
        m1.metric("Total Bookings", len(df))
        m2.metric("Total Revenue", f"₹{int(df['Amount (₹)'].sum()):,}")