import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sheets_db import get_hotel_by_id, load_hotels, load_all_bookings, add_hotel, get_db
from style import apply_style, sidebar_logo, ensure_auth

st.set_page_config(page_title="Admin Panel · Kashmir Analytics", page_icon="⚙️", layout="wide")
apply_style()

hotel = ensure_auth(allowed_roles=["ADMIN"])

# ── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    sidebar_logo()
    st.divider()
    st.markdown("""
    <div style='
        background:linear-gradient(135deg,rgba(15,23,42,0.9),rgba(20,30,60,0.8));
        border:1px solid rgba(239,68,68,0.2);border-radius:12px;
        padding:14px 16px;margin-bottom:12px;
    '>
        <div style='font-size:0.65rem;color:#475569;text-transform:uppercase;
                    letter-spacing:1.5px;margin-bottom:5px;'>Session</div>
        <div style='font-size:0.95rem;font-weight:700;color:#f1f5f9;'>Administrator</div>
        <div style='
            display:inline-block;margin-top:5px;font-size:0.65rem;font-weight:700;
            background:rgba(239,68,68,0.15);color:#f87171;
            border:1px solid rgba(239,68,68,0.3);
            border-radius:20px;padding:2px 10px;text-transform:uppercase;letter-spacing:1px;
        '>⚡ Full Access</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("""<a href='https://wa.me/918491828292' target='_blank' style='text-decoration:none;'>
        <button style='width:100%;border-radius:10px;padding:11px;
                       background:linear-gradient(135deg,#16a34a,#25d366);
                       color:white;border:none;cursor:pointer;font-weight:600;
                       font-size:0.85rem;box-shadow:0 4px 14px rgba(37,211,102,0.25);'>
            💬 Contact Support
        </button></a>""", unsafe_allow_html=True)
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.hotel     = None
        st.query_params.clear()
        st.cache_data.clear()
        st.rerun()

# ── Header ─────────────────────────────────────────────────
st.markdown("<p class='page-title'>⚙️ Admin Panel</p>", unsafe_allow_html=True)
st.markdown("<p class='page-sub'>Manage hotels, accounts, and monitor platform-wide performance.</p>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── Load data ───────────────────────────────────────────────
hotels_df   = load_hotels()
bookings_df = load_all_bookings()
hotels_df   = hotels_df[hotels_df["hotel_id"] != "ADMIN"]

# ── Platform KPIs ────────────────────────────────────────────
total_hotels   = len(hotels_df)
total_bookings = len(bookings_df)
total_revenue  = int(bookings_df["Amount (₹)"].sum()) \
                 if "Amount (₹)" in bookings_df.columns and len(bookings_df) > 0 else 0
active_hotels  = len(bookings_df["hotel_id"].unique()) \
                 if "hotel_id" in bookings_df.columns and len(bookings_df) > 0 else 0
total_commission = int(bookings_df["commission_paid"].sum()) \
                   if "commission_paid" in bookings_df.columns and len(bookings_df) > 0 else 0

st.markdown("<div class='section-title'>Platform Overview</div>", unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("🏨 Total Hotels",    total_hotels)
k2.metric("📋 Total Bookings",  total_bookings)
k3.metric("💰 Gross Revenue",   f"₹{total_revenue:,}")
k4.metric("💸 Commissions",     f"₹{total_commission:,}")
k5.metric("✅ Active Hotels",   active_hotels)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── Hotel Breakdown Table ─────────────────────────────────────
st.markdown("<div class='section-title'>Hotel Breakdown</div>", unsafe_allow_html=True)

if len(bookings_df) > 0 and "hotel_id" in bookings_df.columns:
    summary = (
        bookings_df.groupby("hotel_id")
        .agg(
            Bookings=("hotel_id", "count"),
            Revenue=("Amount (₹)", "sum"),
            Avg_Nights=("Nights", "mean"),
        )
        .reset_index()
    )
    merged = hotels_df[["hotel_id", "name", "username", "plan", "email"]].merge(
        summary, on="hotel_id", how="left"
    ).fillna(0)
    merged["Revenue"]    = merged["Revenue"].astype(int)
    merged["Bookings"]   = merged["Bookings"].astype(int)
    merged["Avg_Nights"] = merged["Avg_Nights"].round(1)
    merged.columns       = ["Hotel ID", "Name", "Username", "Plan", "Email",
                             "Bookings", "Revenue (₹)", "Avg Nights"]
    st.dataframe(merged, use_container_width=True, hide_index=True,
                 column_config={
                     "Revenue (₹)": st.column_config.NumberColumn("Revenue (₹)", format="₹%d"),
                 })
else:
    st.dataframe(hotels_df[["hotel_id", "name", "username", "plan", "email"]],
                 use_container_width=True, hide_index=True)

# ── Revenue by Hotel bar chart ────────────────────────────────
if len(bookings_df) > 0 and "hotel_id" in bookings_df.columns:
    rev_by_hotel = (
        bookings_df.groupby("hotel_id")["Amount (₹)"]
        .sum().reset_index()
        .sort_values("Amount (₹)", ascending=False)
    )
    import plotly.graph_objects as go
    CHART = dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#64748b", size=11),
        xaxis=dict(showgrid=False, showline=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", showline=False, zeroline=False),
        margin=dict(t=30, b=20, l=10, r=10),
        hoverlabel=dict(bgcolor="#0f172a", font_size=13, font_family="Inter",
                        bordercolor="rgba(59,130,246,0.3)"),
    )
    COLOR_SEQ = ["#3b82f6", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"]
    fig_rev = go.Figure(go.Bar(
        x=rev_by_hotel["hotel_id"], y=rev_by_hotel["Amount (₹)"],
        marker=dict(color=COLOR_SEQ[:len(rev_by_hotel)], line=dict(width=0), opacity=0.9),
        text=rev_by_hotel["Amount (₹)"].apply(lambda v: f"₹{v/1000:.1f}k"),
        textposition="outside",
        hovertemplate="<b>%{x}</b>: ₹%{y:,}<extra></extra>"
    ))
    fig_rev.update_layout(**CHART, height=260)
    st.markdown("<div class='section-title'>Revenue by Hotel</div>", unsafe_allow_html=True)
    st.plotly_chart(fig_rev, use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── Management Tabs ────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["➕ Add Hotel", "✏️ Edit Hotel", "🗑️ Delete Hotel"])

# ── ADD ────────────────────────────────────────────────────────
with tab1:
    st.markdown("<div class='section-title'>Register New Hotel</div>", unsafe_allow_html=True)

    # Info card
    st.markdown("""
    <div style='background:rgba(59,130,246,0.06);border:1px solid rgba(59,130,246,0.2);
                border-radius:12px;padding:14px 18px;margin-bottom:20px;'>
        <div style='font-size:0.85rem;color:#93c5fd;font-weight:600;margin-bottom:4px;'>
            📧 How it works
        </div>
        <div style='font-size:0.82rem;color:#64748b;line-height:1.6;'>
            Fill in the hotel details below and click <b style='color:#e2e8f0;'>Add Hotel &amp; Send Invite</b>.
            The hotel owner will receive an email with a link to set up their username and password.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("add_hotel_form"):
        c1, c2 = st.columns(2)
        with c1:
            new_id   = st.text_input("Hotel ID (unique)", placeholder="e.g. HOTEL003")
            new_name = st.text_input("Hotel Name",        placeholder="e.g. Pine View Resort")
        with c2:
            new_email = st.text_input("Hotel Email", placeholder="owner@hotel.com")
            new_plan  = st.selectbox("Subscription Plan", ["basic", "pro", "enterprise"])

        app_url = st.text_input(
            "App URL",
            value="https://kashmir-hotel-analytics.streamlit.app",
            help="The public URL of your deployed app"
        )
        add = st.form_submit_button("➕ Add Hotel & Send Invite", use_container_width=True)

    if add:
        if not all([new_id, new_name, new_email]):
            st.error("❌ Please fill in all required fields.")
        elif new_id in hotels_df["hotel_id"].values:
            st.error("❌ Hotel ID already exists. Choose a unique ID.")
        else:
            add_hotel(new_id, new_name, "", "", new_email, new_plan)
            from email_utils import generate_invite_token, save_invite_token, send_invite_email
            token            = generate_invite_token()
            save_invite_token(token, new_id, new_email)
            success, message = send_invite_email(new_name, new_email, token, app_url)
            if success:
                st.success(f"✅ **{new_name}** added and invite sent to **{new_email}**!")
            else:
                st.success(f"✅ **{new_name}** added successfully!")
                st.error(f"❌ Email failed: {message}")
            st.cache_data.clear()

# ── EDIT ────────────────────────────────────────────────────────
with tab2:
    st.markdown("<div class='section-title'>Update Hotel Details</div>", unsafe_allow_html=True)

    if len(hotels_df) == 0:
        st.info("No hotels to edit.")
    else:
        hotel_options = {row["name"]: row["hotel_id"] for _, row in hotels_df.iterrows()}
        selected_name = st.selectbox("Select Hotel", list(hotel_options.keys()), key="edit_sel")
        selected_id   = hotel_options[selected_name]
        selected_data = hotels_df[hotels_df["hotel_id"] == selected_id].iloc[0]

        st.markdown(f"""
        <div style='background:rgba(15,23,42,0.6);border:1px solid rgba(255,255,255,0.06);
                    border-radius:10px;padding:12px 16px;margin-bottom:16px;
                    display:flex;gap:24px;flex-wrap:wrap;'>
            <div><span style='color:#475569;font-size:0.75rem;'>Hotel ID</span>
                 <div style='color:#93c5fd;font-weight:600;'>{selected_id}</div></div>
            <div><span style='color:#475569;font-size:0.75rem;'>Current Plan</span>
                 <div style='color:#e2e8f0;font-weight:600;'>{selected_data.get("plan","basic").title()}</div></div>
            <div><span style='color:#475569;font-size:0.75rem;'>Email</span>
                 <div style='color:#e2e8f0;font-weight:600;'>{selected_data.get("email","—")}</div></div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("edit_hotel_form"):
            c1, c2 = st.columns(2)
            with c1:
                edit_name     = st.text_input("Hotel Name",   value=selected_data["name"])
                edit_username = st.text_input("Username",     value=selected_data["username"])
                edit_password = st.text_input("New Password (leave blank to keep current)",
                                              type="password")
            with c2:
                edit_email = st.text_input("Email", value=selected_data["email"])
                edit_plan  = st.selectbox(
                    "Plan", ["basic", "pro", "enterprise"],
                    index=["basic", "pro", "enterprise"].index(
                        selected_data.get("plan", "basic"))
                )
            save = st.form_submit_button("💾 Save Changes", use_container_width=True)

        if save:
            db = get_db()
            db.collection("hotels").document(selected_id).update({
                "name":     edit_name,
                "username": edit_username,
                "email":    edit_email,
                "plan":     edit_plan,
            })
            if edit_password:
                db.collection("hotels").document(selected_id).update({"password": edit_password})
            st.success(f"✅ **{edit_name}** updated successfully!")
            st.cache_data.clear()
            st.rerun()

# ── DELETE ────────────────────────────────────────────────────────
with tab3:
    st.markdown("<div class='section-title'>Remove Hotel Account</div>", unsafe_allow_html=True)

    if len(hotels_df) == 0:
        st.info("No hotels to delete.")
    else:
        hotel_options_del = {row["name"]: row["hotel_id"] for _, row in hotels_df.iterrows()}
        del_name = st.selectbox("Select Hotel to Delete", list(hotel_options_del.keys()), key="del_sel")
        del_id   = hotel_options_del[del_name]

        st.markdown(f"""
        <div style='background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.2);
                    border-radius:12px;padding:14px 18px;margin:16px 0;'>
            <div style='font-size:0.85rem;color:#f87171;font-weight:600;margin-bottom:4px;'>
                ⚠️ Destructive Action
            </div>
            <div style='font-size:0.82rem;color:#94a3b8;line-height:1.6;'>
                Deleting <b style='color:#e2e8f0;'>{del_name}</b> will permanently remove their account
                and login access. Their booking records will <b>NOT</b> be deleted.
                This cannot be undone.
            </div>
        </div>
        """, unsafe_allow_html=True)

        confirm = st.checkbox(f"I understand — delete **{del_name}** permanently")

        if confirm:
            if st.button("🗑️ Delete Hotel Account", use_container_width=True):
                db = get_db()
                db.collection("hotels").document(del_id).delete()
                st.success(f"✅ **{del_name}** deleted successfully!")
                st.cache_data.clear()
                st.rerun()