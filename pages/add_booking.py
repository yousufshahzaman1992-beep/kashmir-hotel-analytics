"""
Add Booking Page
"""
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from sheets_db import save_booking, load_hotels
from style import apply_style

# Page config
st.set_page_config(
    page_title="Add Booking - Kashmir Hotel Analytics",
    page_icon="🏔️",
    layout="wide"
)

apply_style()

# Check if user is logged in
if not st.session_state.get("logged_in"):
    st.error("❌ Please login first!")
    st.stop()

hotel = st.session_state.hotel
hotel_id = hotel["hotel_id"]
hotel_name = hotel["name"]

# Page title
st.markdown(f"<p class='page-title'>Add Booking</p>", unsafe_allow_html=True)
st.markdown("<p class='page-sub'>Add a new guest booking to your hotel</p>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# Form
with st.form("add_booking_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        guest_name = st.text_input("Guest Name", placeholder="John Doe")
        check_in = st.date_input("Check-in Date", value=datetime.now())
        room_type = st.selectbox("Room Type", ["Deluxe", "Standard", "Suite", "Budget", "Premium"])
    
    with col2:
        check_out = st.date_input("Check-out Date", value=datetime.now() + timedelta(days=1))
        nights = (check_out - check_in).days
        guests = st.number_input("Number of Guests", min_value=1, max_value=10, value=1)
    
    st.divider()
    
    col3, col4 = st.columns(2)
    
    with col3:
        source = st.selectbox("Booking Source", ["Direct", "OTA", "Foreign", "Local", "Walk-in"])
        amount = st.number_input("Amount (₹)", min_value=0, value=0, step=100)
    
    with col4:
        status = st.selectbox("Status", ["Confirmed", "Pending", "Cancelled"])
        notes = st.text_area("Notes (optional)", placeholder="Any special requests or notes...", height=100)
    
    st.divider()
    
    submit = st.form_submit_button("➕ Add Booking", use_container_width=True)
    
    if submit:
        # Validation
        if not guest_name:
            st.error("❌ Please enter guest name")
        elif nights <= 0:
            st.error("❌ Check-out date must be after check-in date")
        elif amount == 0:
            st.error("❌ Please enter booking amount")
        else:
            # Create booking dict
            booking = {
                "Guest Name": guest_name,
                "Check-in": check_in.strftime("%Y-%m-%d"),
                "Check-out": check_out.strftime("%Y-%m-%d"),
                "Nights": nights,
                "Room Type": room_type,
                "Guests": guests,
                "Source": source,
                "Amount (₹)": amount,
                "Status": status,
                "Notes": notes,
                "Hotel ID": hotel_id
            }
            
            # Save booking
            if save_booking(booking):
                st.success(f"✅ Booking added successfully for {guest_name}!")
                st.balloons()
                # Clear cache to refresh dashboard
                st.cache_data.clear()
                st.session_state.clear_dashboard_cache = True
            else:
                st.error("❌ Error adding booking. Please try again.")

# Info box
st.markdown("""
<div style='background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:10px;padding:15px;margin-top:20px'>
    <p style='margin:0;color:#3b82f6;font-weight:600'>💡 Tip</p>
    <p style='margin:5px 0 0 0;color:#64748b;font-size:0.9rem'>
    Bookings are automatically saved to Google Sheets and will appear on your dashboard within seconds.
    </p>
</div>
""", unsafe_allow_html=True)
