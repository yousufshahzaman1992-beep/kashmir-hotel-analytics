import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sheets_db import get_hotel_by_id, load_hotels, load_all_bookings, add_hotel, get_db, update_hotel_ota_links
from style import apply_style, sidebar_logo, ensure_auth, render_custom_navigation

st.set_page_config(page_title="Admin Panel · Kashmir Analytics", page_icon="⚙️", layout="wide")
apply_style()

hotel = ensure_auth(allowed_roles=["ADMIN"])

# ── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    sidebar_logo()
    render_custom_navigation()
    st.divider()
    st.markdown("""
    <div class='logged-in-box'>
        <div class='logged-in-box-label'>Session</div>
        <div class='logged-in-box-name'>Administrator</div>
        <div class='logged-in-box-plan' style='background:rgba(239,68,68,0.15);color:#f87171;border:1px solid rgba(239,68,68,0.3);'>⚡ Full Access</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("""<a href='https://wa.me/918491828292' target='_blank' style='text-decoration:none;'>
        <button class='support-btn'>💬 Contact Support</button></a>""", unsafe_allow_html=True)
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.hotel     = None
        st.query_params.clear()
        st.cache_data.clear()
        st.rerun()

# ── Header ─────────────────────────────────────────────────
st.markdown("<p class='page-title'>⚙️ Admin Panel</p>", unsafe_allow_html=True)
st.markdown("<p class='page-sub'>Manage hotels, accounts, OTA connections, and monitor platform-wide performance.</p>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── Load data ───────────────────────────────────────────────
hotels_df   = load_hotels()
bookings_df = load_all_bookings()
hotels_df   = hotels_df[hotels_df["hotel_id"] != "ADMIN"]

# ── Platform KPIs ────────────────────────────────────────────
total_hotels   = len(hotels_df)
total_bookings = len(bookings_df)
total_revenue  = int(bookings_df["Amount (₹)"].sum()) if "Amount (₹)" in bookings_df.columns and len(bookings_df) > 0 else 0
active_hotels  = len(bookings_df["hotel_id"].unique()) if "hotel_id" in bookings_df.columns and len(bookings_df) > 0 else 0
total_commission = int(bookings_df["commission_paid"].sum()) if "commission_paid" in bookings_df.columns and len(bookings_df) > 0 else 0

st.markdown("<div class='section-title'>Platform Overview</div>", unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("🏨 Total Hotels",   total_hotels)
k2.metric("📋 Total Bookings", total_bookings)
k3.metric("💰 Gross Revenue",  f"₹{total_revenue:,}")
k4.metric("💸 Commissions",    f"₹{total_commission:,}")
k5.metric("✅ Active Hotels",  active_hotels)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── Hotel Breakdown Table ─────────────────────────────────────
st.markdown("<div class='section-title'>Hotel Breakdown</div>", unsafe_allow_html=True)
if len(bookings_df) > 0 and "hotel_id" in bookings_df.columns:
    summary = (
        bookings_df.groupby("hotel_id")
        .agg(Bookings=("hotel_id","count"), Revenue=("Amount (₹)","sum"), Avg_Nights=("Nights","mean"))
        .reset_index()
    )
    merged = hotels_df[["hotel_id","name","username","plan","email"]].merge(summary, on="hotel_id", how="left").fillna(0)
    merged["Revenue"]    = merged["Revenue"].astype(int)
    merged["Bookings"]   = merged["Bookings"].astype(int)
    merged["Avg_Nights"] = merged["Avg_Nights"].round(1)
    merged.columns       = ["Hotel ID","Name","Username","Plan","Email","Bookings","Revenue (₹)","Avg Nights"]
    st.dataframe(merged, use_container_width=True, hide_index=True,
                 column_config={"Revenue (₹)": st.column_config.NumberColumn("Revenue (₹)", format="₹%d")})
else:
    st.dataframe(hotels_df[["hotel_id","name","username","plan","email"]], use_container_width=True, hide_index=True)

# ── Revenue by Hotel ──────────────────────────────────────────
if len(bookings_df) > 0 and "hotel_id" in bookings_df.columns:
    rev_by_hotel = bookings_df.groupby("hotel_id")["Amount (₹)"].sum().reset_index().sort_values("Amount (₹)", ascending=False)
    CHART = dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#64748b", size=11),
        xaxis=dict(showgrid=False, showline=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", showline=False, zeroline=False),
        margin=dict(t=30, b=20, l=10, r=10),
        hoverlabel=dict(bgcolor="#0f172a", font_size=13, font_family="Inter", bordercolor="rgba(59,130,246,0.3)"),
    )
    COLOR_SEQ = ["#3b82f6","#8b5cf6","#06b6d4","#10b981","#f59e0b","#ef4444"]
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
tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Hotel", "✏️ Edit Hotel", "🗑️ Delete Hotel", "🔗 OTA URLs"])

# ── ADD ────────────────────────────────────────────────────────
with tab1:
    st.markdown("<div class='section-title'>Register New Hotel</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);
                border-radius:12px;padding:14px 18px;margin-bottom:20px;'>
        <div style='font-size:0.85rem;color:var(--primary-color);font-weight:600;margin-bottom:4px;'>📧 How it works</div>
        <div style='font-size:0.82rem;color:var(--text-muted);line-height:1.6;'>
            Fill in the hotel details and click <b style='color:var(--text-color);'>Add Hotel &amp; Send Invite</b>.
            The hotel owner will receive an email with a link to set up their account.
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
            new_plan  = st.selectbox("Subscription Plan", ["basic","pro","enterprise"])
        app_url = st.text_input("App URL", value="https://kashmir-hotel-analytics.streamlit.app",
                                help="The public URL of your deployed app")
        add = st.form_submit_button("➕ Add Hotel & Send Invite", use_container_width=True)
    if add:
        if not all([new_id, new_name, new_email]):
            st.error("❌ Please fill in all required fields.")
        elif new_id in hotels_df["hotel_id"].values:
            st.error("❌ Hotel ID already exists.")
        else:
            add_hotel(new_id, new_name, "", "", new_email, new_plan)
            try:
                from email_utils import generate_invite_token, save_invite_token, send_invite_email
                token            = generate_invite_token()
                save_invite_token(token, new_id, new_email)
                success, message = send_invite_email(new_name, new_email, token, app_url)
                if success:
                    st.success(f"✅ **{new_name}** added and invite sent to **{new_email}**!")
                else:
                    st.success(f"✅ **{new_name}** added!")
                    st.error(f"❌ Email failed: {message}")
            except Exception:
                st.success(f"✅ **{new_name}** added successfully!")
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
        <div style='background:var(--secondary-bg-color);border:1px solid var(--border-color);
                    border-radius:10px;padding:12px 16px;margin-bottom:16px;display:flex;gap:24px;flex-wrap:wrap;'>
            <div><span style='color:var(--text-muted);font-size:0.75rem;'>Hotel ID</span>
                 <div style='color:var(--primary-color);font-weight:600;'>{selected_id}</div></div>
            <div><span style='color:var(--text-muted);font-size:0.75rem;'>Current Plan</span>
                 <div style='color:var(--text-color);font-weight:600;'>{selected_data.get("plan","basic").title()}</div></div>
            <div><span style='color:var(--text-muted);font-size:0.75rem;'>Email</span>
                 <div style='color:var(--text-color);font-weight:600;'>{selected_data.get("email","—")}</div></div>
        </div>
        """, unsafe_allow_html=True)
        with st.form("edit_hotel_form"):
            c1, c2 = st.columns(2)
            with c1:
                edit_name     = st.text_input("Hotel Name",   value=selected_data["name"])
                edit_username = st.text_input("Username",     value=selected_data["username"])
                edit_password = st.text_input("New Password (leave blank to keep current)", type="password")
            with c2:
                edit_email = st.text_input("Email", value=selected_data["email"])
                edit_plan  = st.selectbox("Plan", ["basic","pro","enterprise"],
                                          index=["basic","pro","enterprise"].index(selected_data.get("plan","basic")))
            save = st.form_submit_button("💾 Save Changes", use_container_width=True)
        if save:
            db = get_db()
            db.collection("hotels").document(selected_id).update({
                "name": edit_name, "username": edit_username, "email": edit_email, "plan": edit_plan,
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
        <div style='background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);
                    border-radius:12px;padding:14px 18px;margin:16px 0;'>
            <div style='font-size:0.85rem;color:#f87171;font-weight:600;margin-bottom:4px;'>⚠️ Destructive Action</div>
            <div style='font-size:0.82rem;color:var(--text-muted);line-height:1.6;'>
                Deleting <b style='color:var(--text-color);'>{del_name}</b> will permanently remove their account.
                Booking records will <b>NOT</b> be deleted. This cannot be undone.
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

# ── OTA URLS (Admin Only) ──────────────────────────────────────
with tab4:
    st.markdown("<div class='section-title'>🔗 OTA URL Configuration</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);
                border-radius:12px;padding:14px 18px;margin-bottom:20px;'>
        <div style='font-size:0.85rem;color:var(--primary-color);font-weight:600;margin-bottom:4px;'>
            🤖 Auto-Sync System
        </div>
        <div style='font-size:0.82rem;color:var(--text-muted);line-height:1.6;'>
            Set the OTA URLs for each hotel here. A scheduled GitHub Actions job picks these up
            automatically every 6 hours and saves Booking.com / Agoda / MakeMyTrip reviews to Firebase.
            Hotel users never wait — reviews load instantly from Firebase.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if len(hotels_df) == 0:
        st.info("No hotels found.")
    else:
        hotel_options_ota = {
            f"{row['name']} ({row['hotel_id']})": row["hotel_id"]
            for _, row in hotels_df.iterrows()
        }
        selected_ota_label = st.selectbox("Select Hotel to Configure", list(hotel_options_ota.keys()), key="ota_sel")
        selected_ota_id    = hotel_options_ota[selected_ota_label]

        db   = get_db()
        doc  = db.collection("hotels").document(selected_ota_id).get()
        hdata = doc.to_dict() if doc.exists else {}

        # Status indicators
        statuses = [
            ("Booking.com", hdata.get("booking_review_url", "")),
            ("Agoda",       hdata.get("agoda_review_url", "")),
            ("MakeMyTrip",  hdata.get("mmt_review_url", "") or hdata.get("mmt_url", "")),
            ("Google",      hdata.get("google_place_id", "")),
        ]
        cols = st.columns(4)
        for col, (platform, val) in zip(cols, statuses):
            with col:
                icon  = "🟢" if val else "⚪"
                state = "Configured" if val else "Not set"
                color = "#10b981" if val else "var(--text-muted)"
                st.markdown(f"""
                <div style='background:var(--secondary-bg-color);border:1px solid var(--border-color);
                            border-radius:8px;padding:10px;text-align:center;'>
                    <div style='font-size:1.2rem;'>{icon}</div>
                    <div style='font-size:0.8rem;font-weight:600;color:var(--text-color);'>{platform}</div>
                    <div style='font-size:0.7rem;color:{color};'>{state}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        with st.form(f"ota_form_{selected_ota_id}"):
            st.markdown(f"**Configuring:** {hdata.get('name', selected_ota_id)}")

            u_booking = st.text_input(
                "🏨 Booking.com Hotel URL",
                value=hdata.get("booking_review_url", ""),
                placeholder="https://www.booking.com/hotel/in/hotel-name.en-gb.html"
            )
            u_agoda = st.text_input(
                "🌏 Agoda Hotel URL",
                value=hdata.get("agoda_review_url", ""),
                placeholder="https://www.agoda.com/hotel-name/hotel/city-in.html"
            )
            u_mmt = st.text_input(
                "✈️ MakeMyTrip Hotel URL",
                value=hdata.get("mmt_review_url", ""),
                placeholder="https://www.makemytrip.com/hotels/hotel-details/?hotelId=..."
            )
            u_google = st.text_input(
                "📍 Google Place ID",
                value=hdata.get("google_place_id", ""),
                placeholder="ChIJxxxxxxxxxxxxxxxx"
            )
            st.caption("💡 Find Google Place ID at: https://developers.google.com/maps/documentation/places/web-service/place-id")

            submitted = st.form_submit_button("💾 Save OTA URLs", use_container_width=True, type="primary")
            if submitted:
                ok = update_hotel_ota_links(selected_ota_id, u_booking, u_agoda, u_mmt, u_google)
                if ok:
                    st.success(f"✅ OTA URLs saved for {hdata.get('name', selected_ota_id)}")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("❌ Failed to save. Check Firebase connection.")

        st.divider()

        # Manual sync trigger (Google Places only — OTA scraping runs via GitHub Actions)
        st.markdown("#### ⚡ Manual Sync — Google Places Only")
        st.caption(
            "This button only fetches Google Places reviews. "
            "Booking.com, Agoda, and MakeMyTrip reviews are scraped by a separate GitHub Actions workflow."
        )
        if st.button("🔄 Sync Google Reviews Now", use_container_width=True, key="manual_sync_btn"):
            with st.spinner("Fetching Google Places reviews and saving to Firebase..."):
                from sheets_db import sync_hotel_reviews
                saved, msg, logs = sync_hotel_reviews(selected_ota_id, hdata.get("name", ""))
                st.success(msg)
                with st.expander("📄 Sync Logs", expanded=True):
                    for line in logs:
                        st.write(f"- {line}")

        st.divider()

        # All hotels OTA status overview
        st.markdown("#### 📊 All Hotels OTA Status")
        rows = []
        for _, row in hotels_df.iterrows():
            hid  = row["hotel_id"]
            hdoc = db.collection("hotels").document(hid).get()
            hd   = hdoc.to_dict() if hdoc.exists else {}
            rows.append({
                "Hotel": row["name"],
                "Hotel ID": hid,
                "Booking.com": "✅" if hd.get("booking_review_url") else "❌",
                "Agoda":       "✅" if hd.get("agoda_review_url")    else "❌",
                "MakeMyTrip":  "✅" if (hd.get("mmt_review_url") or hd.get("mmt_url")) else "❌",
                "Google":      "✅" if hd.get("google_place_id")     else "❌",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)
