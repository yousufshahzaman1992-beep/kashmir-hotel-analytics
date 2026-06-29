import streamlit as st

st.set_page_config(page_title="View Bookings", page_icon="📋", layout="wide")

import sys, os
import pandas as pd
import plotly.express as px
import urllib.parse
from fpdf import FPDF
from fpdf.enums import XPos, YPos
# Add the project root to sys.path to allow importing modules from the root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from sheets_db import load_bookings, get_hotel_by_id, update_booking, delete_booking
from style import apply_style, ensure_auth, render_sidebar

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
hotel = ensure_auth()
hotel_id = hotel["hotel_id"]
render_sidebar(hotel)

# ── Header ────────────────────────────────────────────────
st.markdown("<p class='page-title'>📋 All Bookings</p>", unsafe_allow_html=True)
st.markdown("<p class='page-sub'>View, filter, modify and export your booking records.</p>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────
df = load_bookings(hotel_id)

if df is None or len(df) == 0:
    st.info("No bookings yet. Go to **Add Booking** to enter your first one.")
    st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)
    st.stop()

tab1, tab2 = st.tabs(["📊 View & Filter", "✏️ Edit / Delete"])

with tab1:
    st.markdown("<div class='section-title'>Overview</div>", unsafe_allow_html=True)
    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric("Total Bookings", len(df))
    k2.metric("Total Revenue",  f"₹{int(df['Amount (₹)'].sum()):,}")
    k3.metric("Commission",     f"₹{int(df['commission_paid'].sum()):,}")
    k4.metric("Avg Nights",     f"{round(df['Nights'].mean(),1)}")
    k5.metric("Avg Booking",    f"₹{int(df['Amount (₹)'].mean()):,}")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Filters</div>", unsafe_allow_html=True)
    col1,col2,col3,col4 = st.columns(4)
    with col1:
        sf  = st.multiselect("Status",    options=df["Status"].unique(),    default=df["Status"].unique())
    with col2:
        rf  = st.multiselect("Source",    options=df["Source"].unique(),    default=df["Source"].unique())
    with col3:
        rmf = st.multiselect("Room Type", options=df["Room Type"].unique(), default=df["Room Type"].unique())
    with col4:
        bsf = st.multiselect("Booking Channel", options=df["booking_source"].unique(), default=df["booking_source"].unique())

    filtered = df[df["Status"].isin(sf) & df["Source"].isin(rf) & df["Room Type"].isin(rmf) & df["booking_source"].isin(bsf)].copy()

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-title'>Showing {len(filtered)} of {len(df)} bookings</div>",
                unsafe_allow_html=True)

    def generate_wa_link(row):
        phone = str(row.get("Phone", "")).replace('+', '')
        if not phone: return None
        guest = row.get("Guest Name", "Guest")
        msg = f"Hello {guest}, this is {hotel['name']} regarding your booking."
        return f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"

    filtered["WhatsApp"] = filtered.apply(generate_wa_link, axis=1)

    # ── Table ─────────────────────────────────────────────────
    # Hide internal IDs and helper columns from display
    display_cols = [c for c in filtered.columns if c not in ["id", "hotel_id", "Month_Num", "selector"]]
    st.dataframe(filtered[display_cols], width='stretch', hide_index=True, column_config={
        "WhatsApp": st.column_config.LinkColumn("Contact Guest", display_text="💬 WhatsApp"),
        "commission_paid": st.column_config.NumberColumn("Commission Paid (₹)", format="₹%.2f")
    })

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # ── Revenue Distribution Analysis ─────────────────────────
    st.markdown("<div class='section-title'>Revenue Leakage vs Direct Sales</div>", unsafe_allow_html=True)
    
    if not filtered.empty:
        # Aggregate gross revenue by booking source
        source_revenue = filtered.groupby("booking_source", as_index=False)["Amount (₹)"].sum()

        if source_revenue["Amount (₹)"].sum() > 0:
            fig_source = px.pie(source_revenue, values="Amount (₹)", names="booking_source",
                               hole=0.4,
                               color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_source.update_traces(textposition='inside', textinfo='percent+label')
            fig_source.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                height=350,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter, sans-serif", color="#64748b", size=11)
            )
            st.plotly_chart(fig_source, width='stretch')
        else:
            st.info("Insufficient revenue data to generate distribution chart.")
    else:
        st.info("No bookings match your current filters.")
    
    c_csv, c_pdf = st.columns(2)
    with c_csv:
        csv_data = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export to CSV",
            data=csv_data,
            file_name=f"{hotel_id}_bookings.csv",
            mime="text/csv",
            width='stretch'
        )
    
    with c_pdf:
        def create_pdf(data, h_name):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("helvetica", "B", 16)
            pdf.cell(0, 10, f"Booking Report: {h_name}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
            pdf.set_font("helvetica", "", 10)
            pdf.cell(0, 10, f"Generated: {pd.Timestamp.now().strftime('%d %b %Y')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
            pdf.ln(10)
            pdf.set_font("helvetica", "B", 9)
            pdf.set_fill_color(240, 240, 240)
            headers = ["Guest Name", "Check-in", "Amount", "Status"]
            widths = [60, 40, 40, 50]
            for i, h in enumerate(headers): pdf.cell(widths[i], 10, h, border=1, fill=True, align="C")
            pdf.ln()
            pdf.set_font("helvetica", "", 8)
            for _, row in data.iterrows():
                pdf.cell(widths[0], 8, str(row["Guest Name"])[:30], border=1)
                pdf.cell(widths[1], 8, row["Check-in"].strftime('%Y-%m-%d'), border=1, align="C")
                pdf.cell(widths[2], 8, f"{int(row['Amount (₹)']):,}", border=1, align="R")
                pdf.cell(widths[3], 8, str(row["Status"]), border=1, align="C")
                pdf.ln()
            return bytes(pdf.output())

        pdf_bytes = create_pdf(filtered, hotel['name'])
        st.download_button(
            label="📄 Export to PDF",
            data=pdf_bytes,
            file_name=f"{hotel_id}_report.pdf",
            mime="application/pdf",
            width='stretch'
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
            e_source = st.selectbox("Booking Source / Channel *", 
                                    ["Direct Website", "Walk-In", "Local Travel Agent", "MakeMyTrip", 
                                     "Booking.com", "Agoda", "Goibibo", "Yatra", "EaseMyTrip"],
                                    index=["Direct Website", "Walk-In", "Local Travel Agent", "MakeMyTrip", 
                                           "Booking.com", "Agoda", "Goibibo", "Yatra", "EaseMyTrip"].index(b["booking_source"]))
        with c2:
            e_amt   = st.number_input("Amount Paid (₹)", value=int(b["Amount (₹)"]), step=500)
            e_room  = st.selectbox("Room Type", ["Standard","Deluxe","Suite","Houseboat"], 
                                   index=["Standard","Deluxe","Suite","Houseboat"].index(b["Room Type"]))
            e_status = st.selectbox("Status", ["Confirmed","Pending","Cancelled"],
                                    index=["Confirmed","Pending","Cancelled"].index(b["Status"]))
            e_guests = st.number_input("Number of Guests", value=int(b["Guests"]), min_value=1)
            st.info(f"Current Commission: ₹{b['commission_paid']:.2f}")

        e_notes = st.text_area("Notes", value=b["Notes"])
        save_btn = st.form_submit_button("💾 Update Booking Details", width='stretch')

    if save_btn:
        if e_out <= e_in:
            st.error("Check-out date must be after check-in date.")
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
            commission_rate = commission_map.get(e_source, 0.00)
            e_commission = e_amt * commission_rate

            nights = (e_out - e_in).days
            up_data = {
                "Guest Name": e_guest, "Phone": e_phone, "Check-in": str(e_in),
                "Check-out": str(e_out), "Nights": nights, "Room Type": e_room,
                "Amount (₹)": e_amt, "Status": e_status, "Guests": e_guests, "Notes": e_notes,
                "booking_source": e_source, "commission_paid": e_commission
            }
            update_booking(selected_id, up_data, hotel_id)
            st.success("Booking updated successfully!")
            st.rerun()

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    with st.expander("🗑️ Delete Booking"):
        st.warning(f"Caution: This will permanently remove the booking for **{b['Guest Name']}**.")
        confirm_del = st.checkbox("I confirm I want to delete this booking")
        if st.button("🗑️ Delete Permanently", width='stretch', disabled=not confirm_del):
            delete_booking(selected_id, hotel_id)
            st.success("Booking deleted!")
            st.rerun()

# CSS Unlock — triggers the dynamic has-selector to reveal the page
st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)