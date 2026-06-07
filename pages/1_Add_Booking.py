import streamlit as st
from datetime import date
import sys, os

from sheets_db import save_booking, get_hotel_by_id
from style import apply_style, sidebar_logo

st.set_page_config(page_title="Add Booking", page_icon="📝", layout="centered")
apply_style()

# ── Login guard ───────────────────────────────────────────
# Try to recover session from URL if state is lost
if not st.session_state.get("logged_in") and "hid" in st.query_params:
    recovered_hotel = get_hotel_by_id(st.query_params["hid"])
    if recovered_hotel:
        st.session_state.logged_in = True
        st.session_state.hotel = recovered_hotel

if not st.session_state.get("logged_in"):
    st.warning("Please log in first.")
    st.page_link("app.py", label="Go to Login", icon="🔐")
    st.stop()

hotel    = st.session_state.hotel
hotel_id = hotel["hotel_id"]

# Ensure query param is set for persistence on refresh
st.query_params["hid"] = hotel_id

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    sidebar_logo()
    st.divider()
    st.markdown(f"""
    <div style='background:var(--secondary-background-color);
                border:1px solid rgba(148,163,184,0.2);
                border-radius:10px;padding:12px 14px;margin-bottom:12px'>
        <div style='font-size:0.7rem;color:#64748b;text-transform:uppercase;
                    letter-spacing:1px;margin-bottom:4px'>Logged in as</div>
        <div style='font-size:0.95rem;font-weight:600;
                    color:var(--text-color)'>{hotel["name"]}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.hotel     = None
        st.query_params.clear()
        st.rerun()

# ── Header ────────────────────────────────────────────────
st.markdown("<p class='page-title'>📝 Add New Booking</p>",
            unsafe_allow_html=True)
st.markdown("<p class='page-sub'>Fill in the details to record a new booking.</p>",
            unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── Form ──────────────────────────────────────────────────
with st.form("booking_form"):
    col1, col2 = st.columns(2)

    with col1:
        guest_name = st.text_input("Guest Name")
        checkin    = st.date_input("Check-in Date",  value=date.today())
        room_type  = st.selectbox("Room Type",
                        ["Standard","Deluxe","Suite","Houseboat"])
        source     = st.selectbox("Guest Source",
                        ["Delhi","Mumbai","Punjab","Gujarat",
                         "Foreign","Local","Other"])
    with col2:
        guests   = st.number_input("Number of Guests", min_value=1, max_value=10, value=2)
        checkout = st.date_input("Check-out Date", value=date.today())
        amount   = st.number_input("Amount Paid (₹)", min_value=0, step=500, value=5000)
        status   = st.selectbox("Booking Status",
                        ["Confirmed","Pending","Cancelled"])

    notes  = st.text_area("Notes (optional)")
    submit = st.form_submit_button("💾 Save Booking", use_container_width=True)

if submit:
    if not guest_name:
        st.error("❌ Please enter guest name.")
    elif checkout <= checkin:
        st.error("❌ Check-out must be after check-in.")
    else:
        nights  = (checkout - checkin).days
        booking = {
            "Guest Name":  guest_name,
            "Check-in":    str(checkin),
            "Check-out":   str(checkout),
            "Nights":      nights,
            "Room Type":   room_type,
            "Guests":      guests,
            "Source":      source,
            "Amount (₹)":  amount,
            "Status":      status,
            "Notes":       notes,
            "Hotel ID":    hotel_id      # ← uses logged-in hotel's ID
        }
        with st.spinner("Saving to database..."):
            save_booking(booking)
        st.success(f"✅ Booking saved for **{guest_name}**!")
        st.balloons()