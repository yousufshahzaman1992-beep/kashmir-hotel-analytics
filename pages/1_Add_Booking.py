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
# ── Hide admin pages from non-admin users ─────────────────
if st.session_state.get("hotel", {}).get("hotel_id") != "ADMIN":
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
# ── Aggressively hide sidebar if not logged in ────────────
if not st.session_state.get("logged_in"):
    st.markdown("""
        <style>
            /* Hide entire sidebar and the collapse button (hamburger menu) */
            section[data-testid="stSidebar"], 
            [data-testid="stSidebarNav"] { display: none !important; }
            button[kind="headerNoPadding"] { display: none !important; }
        </style>
    """, unsafe_allow_html=True)

    # ── Restore session from query params ────────────────
    hid = st.query_params.get("hid")
    if hid:
        hotel = get_hotel_by_id(hid)
        if hotel:
            st.session_state["logged_in"] = True
            st.session_state["hotel"]     = hotel
            st.rerun()

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

hotel    = st.session_state.hotel
hotel_id = hotel["hotel_id"]

if st.query_params.get("hid") != hotel_id:
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

    st.divider()
    st.markdown("<div class='section-title'>Support</div>", unsafe_allow_html=True)
    support_no = "918491828292"
    support_link = f"https://wa.me/{support_no}?text=Hello, I need help with my hotel analytics dashboard."
    st.markdown(f"""
        <a href='{support_link}' target='_blank' style='text-decoration:none;'>
            <button style='width:100%; border-radius:10px; padding:10px; background:#25d366; color:white; border:none; cursor:pointer; font-weight:600;'>
                💬 Contact Support
            </button>
        </a>
    """, unsafe_allow_html=True)

    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.hotel     = None
        st.query_params.clear()
        st.cache_data.clear() # Added: Clear cache on logout
        st.rerun()

# ── Header ────────────────────────────────────────────────
st.markdown("<p class='page-title'>📝 Add New Booking</p>", unsafe_allow_html=True)
st.markdown("<p class='page-sub'>Fill in the details to record a new booking.</p>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── Form ──────────────────────────────────────────────────
with st.form("booking_form"):
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

    with st.expander("➕ More Details (optional)"):
        col3, col4 = st.columns(2)
        with col3:
            guests = st.number_input("Number of Guests", min_value=1, max_value=10, value=2)
            source = st.selectbox("Guest Source",
                        ["Delhi","Mumbai","Punjab","Gujarat",
                         "Foreign","Local","Other"])
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
            "hotel_id":    hotel_id    # ← lowercase, no space
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
from style import apply_style, sidebar_logo, hide_admin_pages

apply_style()

# Hide admin pages for non-admin users
if st.session_state.get("hotel", {}).get("hotel_id") != "ADMIN":
    hide_admin_pages()
