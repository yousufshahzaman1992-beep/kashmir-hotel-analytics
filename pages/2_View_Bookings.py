import streamlit as st
import sys, os

from sheets_db import load_bookings, get_hotel_by_id
from style import apply_style, sidebar_logo

# ── Restore session from query params on refresh ──────────
if not st.session_state.get("logged_in"):
    hid = st.query_params.get("hid")
    if hid:
        hotel = get_hotel_by_id(hid)
        if hotel:
            st.session_state["logged_in"] = True
            st.session_state["hotel"]     = hotel

st.set_page_config(page_title="View Bookings", page_icon="📋", layout="wide")
apply_style()

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

hotel    = st.session_state.hotel
hotel_id = hotel["hotel_id"]
st.query_params["hid"] = hotel_id

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

st.markdown("<p class='page-title'>📋 All Bookings</p>", unsafe_allow_html=True)
st.markdown("<p class='page-sub'>View, filter and export your booking records.</p>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

df = load_bookings(hotel_id)

if df is None or len(df) == 0:
    st.info("No bookings yet. Go to **Add Booking** to enter your first one.")
    st.stop()

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

filtered = df[df["Status"].isin(sf) & df["Source"].isin(rf) & df["Room Type"].isin(rmf)]

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown(f"<div class='section-title'>Showing {len(filtered)} of {len(df)} bookings</div>", unsafe_allow_html=True)
st.dataframe(filtered, use_container_width=True, hide_index=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
csv_data = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download as CSV",
    data=csv_data,
    file_name=f"{hotel_id}_bookings.csv",
    mime="text/csv",
    use_container_width=True
)