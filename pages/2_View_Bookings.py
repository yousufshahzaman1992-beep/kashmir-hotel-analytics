import streamlit as st

st.set_page_config(page_title="View Bookings", page_icon="📋", layout="wide")

import sys, os
# Add the project root to sys.path to allow importing modules from the root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from sheets_db import load_bookings, get_hotel_by_id, update_booking, delete_booking
from style import apply_style, sidebar_logo

# ── Restore session from query params on refresh ──────────
apply_style()

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
st.markdown("<p class='page-title'>📋 All Bookings</p>", unsafe_allow_html=True)
st.markdown("<p class='page-sub'>View, filter, modify and export your booking records.</p>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────
df = load_bookings(hotel_id)

if df is None or len(df) == 0:
    st.info("No bookings yet. Go to **Add Booking** to enter your first one.")
    st.stop()

tab1, tab2 = st.tabs(["📊 View & Filter", "✏️ Edit / Delete"])

with tab1:
    st.markdown("<div class='section-title'>Overview</div>", unsafe_allow_html=True)
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Total Bookings", len(df))
    k2.metric("Total Revenue",  f"₹{int(df['Amount (₹)'].sum()):,}")
    k3.metric("Avg Nights",     f"{round(df['Nights'].mean(),1)}")
    k4.metric("Avg Booking",    f"₹{int(df['Amount (₹)'].mean()):,}")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Filters</div>", unsafe_allow_html=True)
    col1,col2,col3 = st.columns(3)
    with col1:
        sf  = st.multiselect("Status",    options=df["Status"].unique(),    default=df["Status"].unique())
    with col2:
        rf  = st.multiselect("Source",    options=df["Source"].unique(),    default=df["Source"].unique())
    with col3:
        rmf = st.multiselect("Room Type", options=df["Room Type"].unique(), default=df["Room Type"].unique())

    filtered = df[df["Status"].isin(sf) & df["Source"].isin(rf) & df["Room Type"].isin(rmf)].copy()

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-title'>Showing {len(filtered)} of {len(df)} bookings</div>",
                unsafe_allow_html=True)

    def generate_wa_link(row):
        phone = str(row.get("Phone", "")).replace('+', '')
        if not phone: return None
        guest = row.get("Guest Name", "Guest")
        msg = f"Hello {guest}, this is {hotel['name']} regarding your booking."
        import urllib.parse
        return f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"

    filtered["WhatsApp"] = filtered.apply(generate_wa_link, axis=1)

    # ── Table ─────────────────────────────────────────────────
    # Hide internal IDs and helper columns from display
    display_cols = [c for c in filtered.columns if c not in ["id", "hotel_id", "Month_Num"]]
    st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True, column_config={
        "WhatsApp": st.column_config.LinkColumn("Contact Guest", display_text="💬 WhatsApp")
    })

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    csv_data = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download as CSV",
        data=csv_data,
        file_name=f"{hotel_id}_bookings.csv",
        mime="text/csv",
        use_container_width=True
    )

with tab2:
    st.markdown("<div class='section-title'>Modify or Delete Booking</div>", unsafe_allow_html=True)
    
    # Create descriptive labels for selection
    df['selector'] = df.apply(lambda r: f"{r['Guest Name']} (In: {r['Check-in'].strftime('%d %b')})", axis=1)
    booking_map = {row['selector']: row['id'] for _, row in df.iterrows()}
    
    selected_label = st.selectbox("Select Booking to Edit", options=list(booking_map.keys()))
    selected_id = booking_map[selected_label]
    b = df[df['id'] == selected_id].iloc[0]

    with st.form("edit_booking_form"):
        c1, c2 = st.columns(2)
        with c1:
            e_guest = st.text_input("Guest Name", value=b["Guest Name"])
            e_phone = st.text_input("Phone Number", value=b["Phone"])
            e_in    = st.date_input("Check-in Date", value=b["Check-in"])
            e_out   = st.date_input("Check-out Date", value=b["Check-out"])
        with c2:
            e_amt   = st.number_input("Amount Paid (₹)", value=int(b["Amount (₹)"]), step=500)
            e_room  = st.selectbox("Room Type", ["Standard","Deluxe","Suite","Houseboat"], 
                                   index=["Standard","Deluxe","Suite","Houseboat"].index(b["Room Type"]))
            e_status = st.selectbox("Status", ["Confirmed","Pending","Cancelled"],
                                    index=["Confirmed","Pending","Cancelled"].index(b["Status"]))
            e_guests = st.number_input("Number of Guests", value=int(b["Guests"]), min_value=1)

        e_notes = st.text_area("Notes", value=b["Notes"])
        save_btn = st.form_submit_button("💾 Update Booking Details", use_container_width=True)

    if save_btn:
        if e_out <= e_in:
            st.error("Check-out date must be after check-in date.")
        else:
            nights = (e_out - e_in).days
            up_data = {
                "Guest Name": e_guest, "Phone": e_phone, "Check-in": str(e_in),
                "Check-out": str(e_out), "Nights": nights, "Room Type": e_room,
                "Amount (₹)": e_amt, "Status": e_status, "Guests": e_guests, "Notes": e_notes
            }
            update_booking(selected_id, up_data, hotel_id)
            st.success("Booking updated successfully!")
            st.rerun()

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    with st.expander("🗑️ Delete Booking"):
        st.warning(f"Caution: This will permanently remove the booking for **{b['Guest Name']}**.")
        confirm_del = st.checkbox("I confirm I want to delete this booking")
        if st.button("🗑️ Delete Permanently", use_container_width=True, disabled=not confirm_del):
            delete_booking(selected_id, hotel_id)
            st.success("Booking deleted!")
            st.rerun()