import streamlit as st
import pandas as pd
import sys, os

from sheets_db import get_hotels_sheet, get_bookings_sheet, get_hotel_by_id
from style import apply_style, sidebar_logo

# ── Restore session from query params on refresh ──────────
if not st.session_state.get("logged_in"):
    hid = st.query_params.get("hid")
    if hid:
        hotel = get_hotel_by_id(hid)
        if hotel:
            st.session_state["logged_in"] = True
            st.session_state["hotel"]     = hotel

st.set_page_config(page_title="Admin Panel", page_icon="⚙️", layout="wide")
apply_style()

# ── Guard: must be logged in AND be admin ─────────────────
if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

if st.session_state.hotel["hotel_id"] != "ADMIN":
    st.switch_page("app.py")

# Persist session in URL
st.query_params["hid"] = "ADMIN"

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    sidebar_logo()
    st.divider()
    st.markdown("""
    <div style='background:var(--secondary-background-color);
                border:1px solid rgba(148,163,184,0.2);
                border-radius:10px;padding:12px 14px;margin-bottom:12px'>
        <div style='font-size:0.7rem;color:#64748b;text-transform:uppercase;
                    letter-spacing:1px;margin-bottom:4px'>Logged in as</div>
        <div style='font-size:0.95rem;font-weight:600;
                    color:var(--text-color)'>Administrator</div>
        <div style='font-size:0.75rem;color:#3b82f6'>Full Access</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.hotel     = None
        st.query_params.clear()
        st.rerun()

# ── Header ────────────────────────────────────────────────
st.markdown("<p class='page-title'>⚙️ Admin Panel</p>", unsafe_allow_html=True)
st.markdown("<p class='page-sub'>Manage all hotels and accounts.</p>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── Load all data ─────────────────────────────────────────
@st.cache_data(ttl=30, show_spinner=False)
def load_all():
    hotels   = pd.DataFrame(get_hotels_sheet().get_all_records())
    bookings = pd.DataFrame(get_bookings_sheet().get_all_records())
    return hotels, bookings

hotels_df, bookings_df = load_all()
hotels_df = hotels_df[hotels_df["hotel_id"] != "ADMIN"]

# ── Platform KPIs ─────────────────────────────────────────
st.markdown("<div class='section-title'>Platform Overview</div>", unsafe_allow_html=True)

total_hotels   = len(hotels_df)
total_bookings = len(bookings_df)
total_revenue  = int(bookings_df["Amount (₹)"].sum()) \
                 if "Amount (₹)" in bookings_df.columns and len(bookings_df) > 0 else 0
active_hotels  = len(bookings_df["Hotel ID"].unique()) \
                 if "Hotel ID" in bookings_df.columns and len(bookings_df) > 0 else 0

k1,k2,k3,k4 = st.columns(4)
k1.metric("🏨 Total Hotels",   total_hotels)
k2.metric("📋 Total Bookings", total_bookings)
k3.metric("💰 Total Revenue",  f"₹{total_revenue:,}")
k4.metric("✅ Active Hotels",  active_hotels)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── Per Hotel Breakdown ───────────────────────────────────
st.markdown("<div class='section-title'>Hotel Breakdown</div>", unsafe_allow_html=True)

if len(bookings_df) > 0 and "Hotel ID" in bookings_df.columns:
    summary = (
        bookings_df.groupby("Hotel ID")
        .agg(Bookings=("Hotel ID","count"),
             Revenue=("Amount (₹)","sum"),
             Avg_Nights=("Nights","mean"))
        .reset_index()
        .rename(columns={"Hotel ID":"hotel_id"})
    )
    merged = hotels_df[["hotel_id","name","plan","email"]].merge(
        summary, on="hotel_id", how="left").fillna(0)
    merged["Revenue"]    = merged["Revenue"].astype(int)
    merged["Bookings"]   = merged["Bookings"].astype(int)
    merged["Avg_Nights"] = merged["Avg_Nights"].round(1)
    merged.columns       = ["Hotel ID","Name","Plan","Email",
                             "Bookings","Revenue (₹)","Avg Nights"]
    st.dataframe(merged, use_container_width=True, hide_index=True)
else:
    st.dataframe(hotels_df[["hotel_id","name","plan","email"]],
                 use_container_width=True, hide_index=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── Add New Hotel ─────────────────────────────────────────
st.markdown("<div class='section-title'>Add New Hotel</div>", unsafe_allow_html=True)

with st.form("add_hotel_form"):
    c1, c2 = st.columns(2)
    with c1:
        new_id       = st.text_input("Hotel ID (unique)", placeholder="e.g. HOTEL003")
        new_name     = st.text_input("Hotel Name",        placeholder="e.g. Pine View Resort")
        new_username = st.text_input("Username")
    with c2:
        new_password = st.text_input("Password", type="password")
        new_email    = st.text_input("Email")
        new_plan     = st.selectbox("Plan", ["basic","pro","enterprise"])
    add = st.form_submit_button("➕ Add Hotel", use_container_width=True)

if add:
    if not all([new_id, new_name, new_username, new_password, new_email]):
        st.error("❌ Please fill in all fields.")
    elif new_id in hotels_df["hotel_id"].values:
        st.error("❌ Hotel ID already exists.")
    else:
        get_hotels_sheet().append_row(
            [new_id, new_name, new_username, new_password, new_email, new_plan])
        st.success(f"✅ Hotel **{new_name}** added successfully!")
        st.cache_data.clear()
        st.rerun()