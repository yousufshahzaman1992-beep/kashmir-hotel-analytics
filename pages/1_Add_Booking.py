import streamlit as st

st.set_page_config(page_title="Add Booking", page_icon="📝", layout="centered")

from datetime import date
import sys, os
# Add the project root to sys.path to allow importing modules from the root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from sheets_db import save_booking, get_hotel_by_id
from style import apply_style, sidebar_logo

# ── Restore session from query params on refresh ──────────
apply_style()
from style import ensure_auth, render_sidebar

hotel = ensure_auth()
hotel_id = hotel["hotel_id"]
render_sidebar(hotel)

# ── Sidebar ───────────────────────────────────────────────
# ── Header ────────────────────────────────────────────────
st.markdown("<p class='page-title'>📝 Add New Booking</p>", unsafe_allow_html=True)
st.markdown("<p class='page-sub'>Fill in the details to record a new booking.</p>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── Form ──────────────────────────────────────────────────
with st.form("booking_form"):
    # Comprehensive list of Guest Sources (States, UTs, and major Indian Cities)
    SOURCE_OPTIONS = sorted(list(set([
        "Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Ahmedabad", "Chennai", "Kolkata", "Surat", "Pune", "Jaipur", 
        "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane", "Bhopal", "Visakhapatnam", "Patna", "Vadodara", "Ghaziabad", 
        "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut", "Rajkot", "Varanasi", "Srinagar", "Amritsar", "Ranchi", 
        "Howrah", "Jabalpur", "Gwalior", "Vijayawada", "Jodhpur", "Madurai", "Raipur", "Kota", "Guwahati", "Mysore", 
        "Gurgaon", "Aligarh", "Jalandhar", "Bhubaneswar", "Noida", "Kochi", "Dehradun", "Jammu", "Udaipur", "Shimla", 
        "Darjeeling", "Gangtok", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", 
        "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", 
        "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", 
        "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", "Chandigarh", 
        "Dadra and Nagar Haveli and Daman and Diu", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry",
        "Foreign", "Local", "Other"
    ])))

    # Initialize optional variables
    guests = 2
    source = "Delhi"
    notes  = ""

    col1, col2 = st.columns(2)
    with col1:
        guest_name = st.text_input("Guest Name *")
        phone      = st.text_input("Phone Number *", placeholder="e.g. 918491828292")
        checkin    = st.date_input("Check-in *",  value=date.today())
        checkout   = st.date_input("Check-out *", value=date.today())
    with col2:
        amount    = st.number_input("Amount Paid (₹) *", min_value=0, step=500, value=5000)
        room_type = st.selectbox("Room Type",
                        ["Standard","Deluxe","Suite","Houseboat"])
        status    = st.selectbox("Status",
                        ["Confirmed","Pending","Cancelled"])

    # New Mandatory Booking Source Dropdown
    booking_source = st.selectbox("Booking Source / Channel *", 
                                 ["Direct Website", "Walk-In", "Local Travel Agent", "MakeMyTrip", 
                                  "Booking.com", "Agoda", "Goibibo", "Yatra", "EaseMyTrip"])

    with st.expander("➕ More Details (optional)"):
        col3, col4 = st.columns(2)
        with col3:
            guests = st.number_input("Number of Guests", min_value=1, max_value=10, value=2)
            source = st.selectbox("Guest Source", options=SOURCE_OPTIONS, index=SOURCE_OPTIONS.index("Delhi") if "Delhi" in SOURCE_OPTIONS else 0)
        with col4:
            notes = st.text_area("Notes", height=80)

    submit = st.form_submit_button("💾 Save Booking", use_container_width=True)

# ── Save Logic ────────────────────────────────────────────
if submit:
    if not guest_name or not phone:
        st.session_state["form_error"] = "❌ Please enter guest name and phone number."
    elif checkout <= checkin:
        st.session_state["form_error"] = "❌ Check-out must be after check-in."
    else:
        # Dynamic Backend Commission Calculation
        commission_map = {
            "MakeMyTrip": 0.20,
            "Booking.com": 0.15,
            "Agoda": 0.15,
            "Goibibo": 0.15,
            "Yatra": 0.15,
            "EaseMyTrip": 0.12
        }
        
        commission_rate = commission_map.get(booking_source, 0.00)
        commission_paid = amount * commission_rate

        st.session_state["form_error"] = None
        nights  = (checkout - checkin).days
        booking = {
            "Guest Name":  guest_name,
            "Phone":       phone,
            "Check-in":    str(checkin),
            "Check-out":   str(checkout),
            "Nights":      nights,
            "Room Type":   room_type,
            "Guests":      guests,
            "Source":      source,
            "Amount (₹)":  amount,
            "Status":      status,
            "Notes":       notes,
            "hotel_id":    hotel_id,
            "booking_source": booking_source,
            "commission_paid": commission_paid,
            "status":      "active"
        }
        save_booking(booking)
        if "form_error" in st.session_state:
            del st.session_state["form_error"]
        st.session_state["form_success"] = guest_name
        st.balloons()

# ── Show messages ─────────────────────────────────────────
if st.session_state.get("form_error"):
    st.error(st.session_state["form_error"])

if st.session_state.get("form_success"):
    st.success(f"✅ Booking saved for **{st.session_state['form_success']}**!")
    st.session_state["form_success"] = None

# CSS Unlock — triggers the dynamic has-selector to reveal the page
st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)