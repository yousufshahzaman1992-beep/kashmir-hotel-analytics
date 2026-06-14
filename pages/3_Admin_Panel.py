import streamlit as st
import pandas as pd
import sys, os

from sheets_db import get_hotel_by_id, load_hotels, load_all_bookings, add_hotel, get_db
from style import apply_style, sidebar_logo

# ── Restore session from query params on refresh ──────────
st.set_page_config(page_title="Admin Panel", page_icon="⚙️", layout="wide")
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
        if hid == "ADMIN":
            st.session_state["logged_in"] = True
            st.session_state["hotel"]     = {"hotel_id": "ADMIN", "name": "Administrator"}
            st.rerun()
        else:
            hotel = get_hotel_by_id(hid)
            if hotel:
                st.session_state["logged_in"] = True
                st.session_state["hotel"]     = hotel
                st.rerun()

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

if st.session_state.hotel["hotel_id"] != "ADMIN":
    st.switch_page("app.py")

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
    if st.button("🚪 Logout", width="stretch"):
        st.session_state.logged_in = False
        st.session_state.hotel     = None
        st.query_params.clear()
        st.cache_data.clear() # Added: Clear cache on admin logout
        st.rerun()

# ── Header ────────────────────────────────────────────────
st.markdown("<p class='page-title'>⚙️ Admin Panel</p>", unsafe_allow_html=True)
st.markdown("<p class='page-sub'>Manage all hotels and accounts.</p>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────
hotels_df   = load_hotels()
bookings_df = load_all_bookings()
hotels_df   = hotels_df[hotels_df["hotel_id"] != "ADMIN"]

# ── Platform KPIs ─────────────────────────────────────────
st.markdown("<div class='section-title'>Platform Overview</div>", unsafe_allow_html=True)

total_hotels   = len(hotels_df)
total_bookings = len(bookings_df)
total_revenue  = int(bookings_df["Amount (₹)"].sum()) \
                 if "Amount (₹)" in bookings_df.columns and len(bookings_df) > 0 else 0
active_hotels  = len(bookings_df["hotel_id"].unique()) \
                 if "hotel_id" in bookings_df.columns and len(bookings_df) > 0 else 0

k1,k2,k3,k4 = st.columns(4)
k1.metric("🏨 Total Hotels",   total_hotels)
k2.metric("📋 Total Bookings", total_bookings)
k3.metric("💰 Total Revenue",  f"₹{total_revenue:,}")
k4.metric("✅ Active Hotels",  active_hotels)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── Hotel Breakdown ───────────────────────────────────────
st.markdown("<div class='section-title'>Hotel Breakdown</div>", unsafe_allow_html=True)

if len(bookings_df) > 0 and "hotel_id" in bookings_df.columns:
    summary = (
        bookings_df.groupby("hotel_id")
        .agg(Bookings=("hotel_id","count"),
             Revenue=("Amount (₹)","sum"),
             Avg_Nights=("Nights","mean"))
        .reset_index()
    )
    merged = hotels_df[["hotel_id","name","plan","email"]].merge(
        summary, on="hotel_id", how="left").fillna(0)
    merged["Revenue"]    = merged["Revenue"].astype(int)
    merged["Bookings"]   = merged["Bookings"].astype(int)
    merged["Avg_Nights"] = merged["Avg_Nights"].round(1)
    merged.columns       = ["Hotel ID","Name","Plan","Email",
                             "Bookings","Revenue (₹)","Avg Nights"]
    st.dataframe(merged, width="stretch", hide_index=True)
else:
    st.dataframe(hotels_df[["hotel_id","name","plan","email"]],
                 width="stretch", hide_index=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── Tabs for Add / Edit / Delete ──────────────────────────
tab1, tab2, tab3 = st.tabs(["➕ Add Hotel", "✏️ Edit Hotel", "🗑️ Delete Hotel"])

# ── ADD ───────────────────────────────────────────────────
with tab1:
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
        add = st.form_submit_button("➕ Add Hotel", width="stretch")

    if add:
        if not all([new_id, new_name, new_username, new_password, new_email]):
            st.error("❌ Please fill in all fields.")
        elif new_id in hotels_df["hotel_id"].values:
            st.error("❌ Hotel ID already exists.")
        else:
            add_hotel(new_id, new_name, new_username, new_password, new_email, new_plan)
            st.success(f"✅ Hotel **{new_name}** added successfully!")
            st.cache_data.clear()
            st.rerun()

# ── EDIT ──────────────────────────────────────────────────
with tab2:
    st.markdown("<div class='section-title'>Edit Hotel</div>", unsafe_allow_html=True)

    if len(hotels_df) == 0:
        st.info("No hotels to edit.")
    else:
        hotel_options = {row["name"]: row["hotel_id"] for _, row in hotels_df.iterrows()}
        selected_name = st.selectbox("Select Hotel to Edit", list(hotel_options.keys()))
        selected_id   = hotel_options[selected_name]
        selected_data = hotels_df[hotels_df["hotel_id"] == selected_id].iloc[0]

        with st.form("edit_hotel_form"):
            c1, c2 = st.columns(2)
            with c1:
                edit_name     = st.text_input("Hotel Name",   value=selected_data["name"])
                edit_username = st.text_input("Username",     value=selected_data["username"])
                edit_password = st.text_input("Password (leave blank to keep current)", type="password") # Modified: Don't pre-fill password
            with c2:
                edit_email = st.text_input("Email",           value=selected_data["email"])
                edit_plan  = st.selectbox("Plan",
                                ["basic","pro","enterprise"],
                                index=["basic","pro","enterprise"].index(
                                    selected_data.get("plan","basic")))

            save = st.form_submit_button("💾 Save Changes", width="stretch")

        if save:
            db = get_db()
            db.collection("hotels").document(selected_id).update({
                "name":     edit_name,
                "username": edit_username,
                "email":    edit_email,
                "plan":     edit_plan
            })
            if edit_password: # Added: Only update password if a new one is provided
                db.collection("hotels").document(selected_id).update({"password": edit_password})
            st.success(f"✅ **{edit_name}** updated successfully!")
            st.cache_data.clear()
            st.rerun()

# ── DELETE ────────────────────────────────────────────────
with tab3:
    st.markdown("<div class='section-title'>Delete Hotel</div>", unsafe_allow_html=True)

    if len(hotels_df) == 0:
        st.info("No hotels to delete.")
    else:
        hotel_options_del = {row["name"]: row["hotel_id"] for _, row in hotels_df.iterrows()}
        del_name = st.selectbox("Select Hotel to Delete", list(hotel_options_del.keys()))
        del_id   = hotel_options_del[del_name]

        st.warning(f"⚠️ Deleting **{del_name}** will remove their account. "
                   f"Their bookings will NOT be deleted.")

        confirm = st.checkbox(f"Yes, I want to delete **{del_name}**")

        if confirm:
            if st.button("🗑️ Delete Hotel", width="stretch"):
                db = get_db()
                db.collection("hotels").document(del_id).delete()
                st.success(f"✅ **{del_name}** deleted successfully!")
                st.cache_data.clear()
                st.rerun()