import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
import urllib.parse
import sys
from datetime import date

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sheets_db import (
    load_bookings,
    get_hotel_by_id,
    get_google_reviews,
    load_reviews,
    save_review_to_firebase,
    get_srinagar_live_risk_data,
    load_checklist,
    save_checklist,
    sync_hotel_reviews,
    update_hotel_ota_links,
    verify_session_token,
    generate_session_token,
)
from login import show_login
from style import apply_style, sidebar_logo, render_custom_navigation

# ── Init session state ────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ── Restore session from secure URL token if present ─────
if not st.session_state.logged_in:
    session_token = st.query_params.get("session")
    if session_token:
        hotel = verify_session_token(session_token)
        if hotel:
            st.session_state.logged_in = True
            st.session_state.hotel = hotel
        else:
            # Token invalid or expired, clear it
            st.query_params.pop("session", None)
if "hotel" not in st.session_state:
    st.session_state.hotel = None

st.set_page_config(
    page_title="Kashmir Hotel Analytics",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded" if st.session_state.get("logged_in") else "collapsed"
)

# ── Flash prevention: hide sidebar & nav instantly on every load ──
# This runs synchronously before any Python auth logic, preventing
# the sidebar from flickering visible for a frame on page refresh.
if not st.session_state.get("logged_in"):
    st.markdown("""
        <style>
            section[data-testid="stSidebar"],
            [data-testid="stSidebarNav"],
            [data-testid="stSidebarNavSeparator"],
            header[data-testid="stHeader"] button[kind="headerNoPadding"],
            [data-testid="stToolbar"] {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
                pointer-events: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

apply_style()

CHART = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    autosize=True,
    font=dict(family="Inter, sans-serif", color="#64748b", size=11),
    xaxis=dict(
        showgrid=False, showline=False, zeroline=False,
        tickfont=dict(color="#475569", size=11),
    ),
    yaxis=dict(
        showgrid=True, gridcolor="rgba(255,255,255,0.04)",
        showline=False, zeroline=False,
        tickfont=dict(color="#475569", size=11),
    ),
    margin=dict(t=30, b=20, l=10, r=10),
    hoverlabel=dict(
        bgcolor="#0f172a", font_size=13,
        font_family="Inter", bordercolor="rgba(59,130,246,0.3)"
    ),
)
BLUES      = [[0, "#bfdbfe"], [1, "#2563eb"]]
VIBRANT_PURPLE = "#8b5cf6"
COLOR_SEQ  = ["#3b82f6", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"]

# ══════════════════════════════════════════════════════════
# NOT LOGGED IN — handle invite links + session restore
# ══════════════════════════════════════════════════════════
if not st.session_state.get("logged_in"):

    # Hide sidebar while not logged in
    st.markdown("""
        <style>
            section[data-testid="stSidebar"],
            [data-testid="stSidebarNav"] { display: none !important; }
        </style>
    """, unsafe_allow_html=True)

    # Handle invite link
    invite_token = st.query_params.get("invite")
    if invite_token:
        st.session_state["invite_token"] = invite_token
        st.switch_page("pages/4_Setup_Account.py")
        st.stop()

    # Handle password reset link
    reset_token = st.query_params.get("reset")
    if reset_token:
        st.session_state["reset_token"] = reset_token
        st.switch_page("pages/4_Setup_Account.py")
        st.stop()

    # NOTE: ?hid= in URL is intentionally NOT used to restore auth.
    # Granting login from a URL parameter alone (no password) is a critical
    # security vulnerability — any person with the URL would get full access.
    # Users must always authenticate via the login form.
    show_login()
    st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════
# LOGGED IN — dashboard
# ══════════════════════════════════════════════════════════
hotel      = st.session_state.hotel
hotel_id   = hotel["hotel_id"]
hotel_name = hotel["name"]

# Persist session in URL securely
if "session" not in st.query_params:
    st.query_params["session"] = generate_session_token(hotel_id)
if "hid" in st.query_params:
    st.query_params.pop("hid", None)

# Hide admin pages from non-admin users
if hotel_id != "ADMIN":
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

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    sidebar_logo()
    render_custom_navigation()
    st.divider()

    plan_label = "Full Access" if hotel_id == "ADMIN" else hotel.get("plan", "Basic").title()
    st.markdown(f"""
    <div class='logged-in-box'>
        <div class='logged-in-box-label'>Logged in as</div>
        <div class='logged-in-box-name'>{hotel_name}</div>
        <div class='logged-in-box-plan'>{plan_label} Plan</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("↻ Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    season = st.selectbox("Season",
        ["Full Year","Winter (Jan–Mar)","Spring (Apr–Jun)",
         "Summer (Jul–Sep)","Autumn (Oct–Dec)"])

    st.divider()

    support_link = "https://wa.me/918491828292?text=Hello, I need help with my hotel analytics dashboard."
    st.markdown(f"""
        <a href='{support_link}' target='_blank' style='text-decoration:none;'>
            <button class='support-btn'>
                💬 Contact Support
            </button>
        </a>
    """, unsafe_allow_html=True)

    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.hotel     = None
        st.query_params.clear()
        st.cache_data.clear()
        st.rerun()

# ── Admin welcome screen ──────────────────────────────────
if hotel_id == "ADMIN":
    st.markdown("<p class='page-title'>⚙️ Administrator</p>", unsafe_allow_html=True)
    st.markdown("<p class='page-sub'>Welcome to Kashmir Hotel Analytics Admin.</p>",
                unsafe_allow_html=True)
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.info("👋 Use the sidebar to navigate to the **Admin Panel** to manage hotels.")
    st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)
    st.stop()

# ── Load data ─────────────────────────────────────────────
df = load_bookings(hotel_id)

# ── Header ────────────────────────────────────────────────
hc1, hc2 = st.columns([5,1])
with hc1:
    st.markdown(f"<p class='page-title'>{hotel_name}</p>", unsafe_allow_html=True)
    st.markdown("<p class='page-sub'>Revenue & Occupancy Dashboard</p>",
                unsafe_allow_html=True)
with hc2:
    st.markdown(f"<br><span class='badge'>{season}</span>", unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

SM = {
    "Full Year":        [1,2,3,4,5,6,7,8,9,10,11,12],
    "Winter (Jan–Mar)": [1,2,3],
    "Spring (Apr–Jun)": [4,5,6],
    "Summer (Jul–Sep)": [7,8,9],
    "Autumn (Oct–Dec)": [10,11,12],
}

if len(df) == 0:
    st.info("No bookings yet. Go to **Add Booking** to add your first booking.")
    st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)
    st.stop()

fdf = df[df["Month_Num"].isin(SM[season])]

total_rev    = int(fdf["Amount (₹)"].sum())
total_book   = len(fdf)
total_nights = int(fdf["Nights"].sum())
avg_nights   = round(fdf["Nights"].mean(), 1) if total_book else 0
avg_book     = int(fdf["Amount (₹)"].mean())  if total_book else 0

# ── Premium KPIs ──────────────────────────────────────────
total_commission = fdf["commission_paid"].sum()
net_revenue      = total_rev - total_commission
adr              = net_revenue / total_nights if total_nights > 0 else 0

# Dynamic occupancy rate divisor based on rooms and selected season days
ASSUMED_ROOMS = hotel.get("room_count", 30)
season_day_counts = {
    "Full Year": 365, "Winter (Jan–Mar)": 90, "Spring (Apr–Jun)": 91,
    "Summer (Jul–Sep)": 92, "Autumn (Oct–Dec)": 92
}
season_days = season_day_counts.get(season, 30)
occupancy_rate = (total_nights / (ASSUMED_ROOMS * season_days)) * 100 if ASSUMED_ROOMS > 0 else 0

# ── Create top-level dashboard tabs ──
tab_overview, tab_bookings, tab_reviews, tab_risk = st.tabs([
    "📊 Financial Overview",
    "📋 Bookings & Operations",
    "⭐ Reputation & Reviews",
    "✈️ Travel Risk & Demand"
])

with tab_overview:
    st.markdown("<div class='section-title'>Hospitality Performance Indicators</div>", unsafe_allow_html=True)
    with st.container():
        m1, m2, m3 = st.columns(3)
        m1.metric("💰 Net Revenue", f"₹{int(net_revenue):,}", help="Total Revenue minus OTA Commissions")
        m2.metric("📈 ADR (Net)", f"₹{int(adr):,}", help="Average Daily Rate (Net Revenue / Total Nights)")
        m3.metric("🏨 Occupancy Rate", f"{occupancy_rate:.1f}%", help="Based on 30 rooms baseline")

    st.markdown("<br>", unsafe_allow_html=True)

    if total_book == 0:
        st.info("No bookings for this season.")
    else:
        # ── Row 1: Revenue + Origins ──
        c1, c2 = st.columns([3,2], gap="small")
        with c1:
            st.markdown("<div class='section-title'>Monthly Revenue</div>", unsafe_allow_html=True)
            rev = (fdf.groupby(["Month_Num","Month"])["Amount (₹)"]
                      .sum().reset_index().sort_values("Month_Num"))
            fig1 = go.Figure(go.Bar(
                x=rev["Month"], y=rev["Amount (₹)"],
                marker=dict(color=rev["Amount (₹)"], colorscale="Sunset", line=dict(width=0)),
                text=rev["Amount (₹)"].apply(lambda x: f"₹{x/1000:.1f}k" if x >= 1000 else f"₹{x}"),
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>₹%{y:,}<extra></extra>"
            ))
            fig1.update_layout(**CHART)
            st.markdown("<div class='scroll-through-chart'>", unsafe_allow_html=True)
            st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown("<div class='section-title'>Guest Origins</div>", unsafe_allow_html=True)
            src = fdf["Source"].value_counts().reset_index()
            src.columns = ["Source","Guests"]
            fig2 = px.pie(src, names="Source", values="Guests", hole=0.6,
                          color_discrete_sequence=COLOR_SEQ)
            fig2.update_traces(
                textposition="outside", textinfo="label+percent",
                pull=[0.06 if i == 0 else 0 for i in range(len(src))],
                textfont=dict(size=11, color="#94a3b8"),
                marker=dict(line=dict(color="#060b18", width=3))
            )
            fig2.update_layout(**CHART, showlegend=False)
            st.markdown("<div class='scroll-through-chart'>", unsafe_allow_html=True)
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        # ── Row 2: Room Type + Trend ──
        c3, c4 = st.columns([2,3], gap="small")
        with c3:
            st.markdown("<div class='section-title'>Room Type</div>", unsafe_allow_html=True)
            rooms = fdf["Room Type"].value_counts().reset_index()
            rooms.columns = ["Room Type","Count"]
            fig3 = go.Figure(go.Bar(
                x=rooms["Count"], y=rooms["Room Type"], orientation="h",
                marker=dict(
                    color=COLOR_SEQ[:len(rooms)],
                    line=dict(width=0),
                    opacity=0.9,
                ),
                text=rooms["Count"],
                textposition="outside",
                textfont=dict(color="#94a3b8", size=12),
                hovertemplate="<b>%{y}</b>: %{x} bookings<extra></extra>"
            ))
            fig3.update_layout(**CHART)
            st.markdown("<div class='scroll-through-chart'>", unsafe_allow_html=True)
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)

        with c4:
            st.markdown("<div class='section-title'>Bookings Over Time</div>", unsafe_allow_html=True)
            trend = (fdf.groupby(["Month_Num","Month"])
                        .size().reset_index(name="Bookings").sort_values("Month_Num"))
            fig4 = go.Figure(go.Scatter(
                x=trend["Month"], y=trend["Bookings"],
                mode="lines+markers",
                line=dict(color=VIBRANT_PURPLE, width=3, shape="spline"),
                marker=dict(size=10, color=VIBRANT_PURPLE, line=dict(color="white", width=2)),
                fill="tozeroy", fillcolor="rgba(139, 92, 246, 0.15)",
                hovertemplate="<b>%{x}</b>: %{y}<extra></extra>"
            ))
            fig4.update_layout(**CHART)
            st.markdown("<div class='scroll-through-chart'>", unsafe_allow_html=True)
            st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)

with tab_bookings:
    if total_book == 0:
        st.info("No bookings for this season.")
    else:
        # ── Insights + Recent Bookings ──
        ci1, ci2 = st.columns([1,2])
        with ci1:
            st.markdown("<div class='section-title'>Quick Insights</div>", unsafe_allow_html=True)
            src = fdf["Source"].value_counts().reset_index()
            src.columns = ["Source","Guests"]
            rooms = fdf["Room Type"].value_counts().reset_index()
            rooms.columns = ["Room Type","Count"]

            top_src  = src.iloc[0]["Source"] if len(src) else "—"
            top_room = rooms.iloc[0]["Room Type"] if len(rooms) else "—"
            foreign  = src[src["Source"]=="Foreign"]["Guests"].sum() \
                       if "Foreign" in src["Source"].values else 0
            fp       = round(foreign/src["Guests"].sum()*100) \
                       if src["Guests"].sum()>0 else 0
            conf     = len(fdf[fdf["Status"]=="Confirmed"]) \
                       if "Confirmed" in fdf["Status"].values else 0
            rows = [
                ("Top guest market",  top_src),
                ("Most booked room",  top_room),
                ("Foreign guests",    f"{fp}%"),
                ("Confirmed bookings",str(conf)),
                ("Total revenue",     f"₹{total_rev:,}"),
            ]
            html = "<div class='card-wrap'>"
            for lbl,val in rows:
                html += f"<div class='insight-row'><span>{lbl}</span>" \
                        f"<span class='insight-val'>{val}</span></div>"
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)

        with ci2:
            st.markdown("<div class='section-title'>Recent Bookings</div>", unsafe_allow_html=True)
            recent = fdf.sort_values("Check-in", ascending=False).head(8).copy()

            def generate_wa_link(row):
                phone = str(row.get("Phone","")).replace("+","").strip()
                if not phone or phone == "nan":
                    return None
                guest = row.get("Guest Name","Guest")
                msg   = f"Hello {guest}, this is {hotel_name} regarding your booking."
                return f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"

            recent["WhatsApp"] = recent.apply(generate_wa_link, axis=1)
            st.dataframe(recent, use_container_width=True, hide_index=True, column_config={
                "WhatsApp": st.column_config.LinkColumn("Contact", display_text="💬 WhatsApp")
            })

with tab_reviews:
    # ── Row 3: OTA Reputation & Sentiment Analytics ──
    st.markdown("<p class='section-title'>⭐ OTA Reputation & Sentiment Analytics</p>", unsafe_allow_html=True)

    # Word lexicons for rule-based sentiment classifier
    POSITIVE_WORDS = {
        'excellent', 'amazing', 'great', 'beautiful', 'clean', 'friendly', 'helpful',
        'good', 'love', 'perfect', 'comfortable', 'wonderful', 'delicious', 'nice',
        'best', 'awesome', 'fantastic', 'superb', 'pleasant', 'warm', 'cozy', 'tasty',
        'exceptional', 'hospitable', 'polite', 'courteous', 'quick', 'fast', 'prompt',
        'outstanding', 'mesmerizing', 'spacious', 'fireplace'
    }

    NEGATIVE_WORDS = {
        'dirty', 'bad', 'worst', 'poor', 'rude', 'cold', 'unhelpful', 'slow', 'expensive',
        'noisy', 'disappointing', 'terrible', 'horrible', 'broken', 'smelly', 'hard',
        'old', 'uncomfortable', 'leak', 'freezing', 'delay', 'issue', 'problem', 'loud',
        'overpriced', 'average', 'fail', 'unpleasant', 'smell', 'dusty', 'cracked', 'forgot'
    }

    ASPECTS = {
        "Food & Dining": ['food', 'breakfast', 'dinner', 'lunch', 'buffet', 'taste', 'restaurant', 'chef', 'meal', 'delicious', 'rogan josh', 'kahwa', 'tea', 'mutton', 'eat'],
        "Heating & Plumbing": ['heating', 'heater', 'geyser', 'hot water', 'cold', 'freezing', 'water', 'plumbing', 'shower', 'bathroom', 'leak', 'warm'],
        "Service & Hospitality": ['service', 'staff', 'manager', 'hospitality', 'friendly', 'rude', 'polite', 'help', 'reception', 'unhelpful', 'wait', 'order', 'management'],
        "Room & Cleanliness": ['room', 'clean', 'dirty', 'sheet', 'blanket', 'bed', 'spacious', 'dusty', 'comfortable', 'view', 'garden', 'cabin', 'wooden', 'heritage']
    }

    # ── Live OTA Sync & Real-Time Sentiment Control Center ──
    with st.container():
        st.markdown("""
        <div style='background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.2); border-radius:12px; padding:18px; margin-bottom:20px;'>
            <h4 style='margin:0 0 6px 0; color:var(--primary-color); font-size:1.15rem;'>🔄 Live OTA Sync & Real-Time Sentiment Control Center</h4>
            <p style='font-size:0.8rem; color:var(--text-muted); margin:0;'>
                Reviews sync automatically from Booking.com, Agoda, MakeMyTrip, and Google on a schedule — or write a custom review below to perform instant sentiment analysis.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_sync, col_manual = st.columns(2)

        with col_sync:
            st.markdown("<p style='font-weight:600; color:var(--text-color); margin-bottom:8px; font-size:0.95rem;'>⚡ OTA Connection & Live Sync</p>", unsafe_allow_html=True)

            # Fetch current URLs from session state hotel info
            h_booking_url = hotel.get("booking_review_url", "")
            h_agoda_url = hotel.get("agoda_review_url", "")
            h_mmt_url = hotel.get("mmt_review_url", "") or hotel.get("mmt_url", "")
            h_google_place_id = hotel.get("google_place_id", "")

            with st.expander("⚙️ Configure OTA URLs & Place ID", expanded=False):
                u_booking = st.text_input("Booking.com Review URL", value=h_booking_url, placeholder="https://www.booking.com/hotel/...")
                u_agoda = st.text_input("Agoda Review URL", value=h_agoda_url, placeholder="https://www.agoda.com/...")
                u_mmt = st.text_input("MakeMyTrip Review URL", value=h_mmt_url, placeholder="https://www.makemytrip.com/...")
                u_google = st.text_input("Google Place ID", value=h_google_place_id, placeholder="e.g. ChIJ...")

                if st.button("💾 Save OTA URLs", use_container_width=True):
                    success = update_hotel_ota_links(hotel_id, u_booking, u_agoda, u_mmt, u_google)
                    if success:
                        st.success("OTA URLs updated successfully!")
                        # Update session state
                        st.session_state.hotel = get_hotel_by_id(hotel_id)
                        st.rerun()
                    else:
                        st.error("Failed to update URLs in database.")

            # Status Indicator for connected platforms
            status_items = []
            if h_booking_url: status_items.append("🟢 Booking.com")
            else: status_items.append("⚪ Booking.com")
            if h_agoda_url: status_items.append("🟢 Agoda")
            else: status_items.append("⚪ Agoda")
            if h_mmt_url: status_items.append("🟢 MakeMyTrip")
            else: status_items.append("⚪ MakeMyTrip")
            if h_google_place_id: status_items.append("🟢 Google Places")
            else: status_items.append("⚪ Google Places")

            st.markdown(f"""
            <div style='background:var(--secondary-bg-color); border:1px solid var(--border-color); border-radius:8px; padding:10px 12px; margin-bottom:12px;'>
                <div style='font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;'>Connected Platforms</div>
                <div style='font-size:0.8rem; display:flex; gap:10px; flex-wrap:wrap; color:var(--text-color);'>
                    {" | ".join(status_items)}
                </div>
            </div>
            """, unsafe_allow_html=True)

            sync_btn_label = "🔄 Sync Reviews Now"
            if st.button(sync_btn_label, type="primary", use_container_width=True):
                with st.spinner("Syncing reviews..."):
                    saved_count, msg, sync_logs = sync_hotel_reviews(hotel_id, hotel_name, only_google=True)
                    st.success(msg)
                    with st.expander("📄 View Sync Logs", expanded=True):
                        for log in sync_logs:
                            st.write(f"- {log}")
                    st.rerun()
        with col_manual:
            st.markdown("<p style='font-weight:600; color:var(--text-color); margin-bottom:8px; font-size:0.95rem;'>✍️ Real-Time Sentiment Analyzer Form</p>", unsafe_allow_html=True)

            # Real-time text area
            m_review_text = st.text_area("Review Text", height=82, placeholder="Type/paste a guest review to analyze sentiment in real time...", key="m_review_text_val")

            # Ratings — using select_slider instead of slider to avoid
            # scroll-event capture (st.slider intercepts mouse-wheel scrolling
            # and freezes the page while the cursor is anywhere near it)
            m_rating = st.select_slider(
                "Guest Rating Stars",
                options=[1, 2, 3, 4, 5],
                value=5,
                format_func=lambda x: "⭐" * x,
                key="m_rating_val"
            )

            # Interactive Real-Time Sentiment & Aspect Detection
            if m_review_text:
                # Live sentiment calculation
                words = m_review_text.lower().split()
                pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
                neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)
                score = (m_rating - 3) * 2 + (pos_count - neg_count)

                if score > 0:
                    live_sent = "🟢 Positive"
                    text_color = "#10b981"
                    bg_color = "rgba(16,185,129,0.1)"
                elif score < 0:
                    live_sent = "🔴 Negative"
                    text_color = "#ef4444"
                    bg_color = "rgba(239,68,68,0.1)"
                else:
                    live_sent = "🟡 Neutral"
                    text_color = "#f59e0b"
                    bg_color = "rgba(245,158,11,0.1)"

                # Live aspect detection
                text_lower = m_review_text.lower()
                live_aspects = []
                for aspect, keywords in ASPECTS.items():
                    if any(kw in text_lower for kw in keywords):
                        live_aspects.append(aspect)
                if not live_aspects:
                    live_aspects = ["General"]

                aspects_badges = " ".join([f"<span style='background:rgba(59,130,246,0.15);color:var(--primary-color);border-radius:4px;padding:2px 6px;font-size:0.7rem;'>{a}</span>" for a in live_aspects])

                st.markdown(f"""
                <div style='background:{bg_color}; border:1px solid {text_color}44; border-radius:8px; padding:12px; margin-bottom:12px;'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <span style='font-size:0.8rem; color:var(--text-muted);'>Live Sentiment Score: <b>{score}</b></span>
                        <span style='color:{text_color}; font-weight:700; font-size:0.9rem;'>{live_sent}</span>
                    </div>
                    <div style='margin-top:6px; font-size:0.8rem; color:var(--text-muted); display:flex; align-items:center; gap:6px;'>
                        <span>Aspects:</span>
                        <div style='display:flex; gap:4px; flex-wrap:wrap;'>{aspects_badges}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with st.expander("✏️ Guest Metadata & Save Document", expanded=False):
                m_guest_name = st.text_input("Guest Name", value="Guest Name", placeholder="e.g. John Doe")
                m_source = st.selectbox("Review Source", ["Google", "Booking.com", "Agoda", "MakeMyTrip", "Direct Customer"])
                m_date = st.date_input("Review Date", value=date.today())

                if st.button("📥 Save Review to Firebase", use_container_width=True):
                    if not m_review_text.strip():
                        st.error("Please enter some review text first.")
                    else:
                        review_data = {
                            "hotel_id": hotel_id,
                            "guest_name": m_guest_name.strip(),
                            "rating": int(m_rating),
                            "review_text": m_review_text.strip(),
                            "source": m_source,
                            "date": m_date.strftime("%Y-%m-%d")
                        }
                        save_review_to_firebase(review_data)
                        st.success("Review saved and live charts updated!")
                        st.rerun()

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # Fetch reviews from database (with mock fallback)
    reviews_raw = load_reviews(hotel_id)
    _using_mock_reviews = not bool(reviews_raw) or any(r.get("_is_mock", False) for r in reviews_raw)
    if _using_mock_reviews:
        st.markdown("""
        <div style='background:rgba(245,158,11,0.10); border:1px solid rgba(245,158,11,0.35); border-radius:10px;
                    padding:12px 16px; margin-bottom:18px; display:flex; align-items:center; gap:10px;'>
            <span style='font-size:1.2rem;'>🧪</span>
            <div>
                <div style='font-size:0.85rem; font-weight:700; color:#f59e0b;'>Demo Data — No Real Reviews Yet</div>
                <div style='font-size:0.78rem; color:var(--text-muted); margin-top:2px;'>
                    The reviews below are sample data for demonstration purposes.
                    Real guest reviews will appear here once your OTA platforms are connected and synced via the Admin Panel.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    processed_reviews = []
    for r in reviews_raw:
        text = r.get("review_text", "")
        rating = r.get("rating", 3)

        # Simple lexical sentiment analyzer
        words = str(text).lower().split()
        pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
        neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)
        score = (rating - 3) * 2 + (pos_count - neg_count)

        if score > 0:
            sentiment = "Positive"
        elif score < 0:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        # Simple aspect detection
        text_lower = str(text).lower()
        aspects_found = []
        for aspect, keywords in ASPECTS.items():
            if any(kw in text_lower for kw in keywords):
                aspects_found.append(aspect)
        if not aspects_found:
            aspects_found = ["General"]

        processed_reviews.append({
            "guest_name": r.get("guest_name", "Guest"),
            "rating": rating,
            "review_text": text,
            "source": r.get("source", "Google"),
            "date": r.get("date", "2026-06-01"),
            "sentiment": sentiment,
            "aspects": aspects_found
        })

    rdf = pd.DataFrame(processed_reviews)

    if not rdf.empty:
        # ── Summary KPIs ──
        total_count = len(rdf)
        avg_rating = rdf["rating"].mean()
        pos_count = len(rdf[rdf["sentiment"] == "Positive"])
        pos_pct = round((pos_count / total_count) * 100) if total_count > 0 else 0

        m1, m2, m3 = st.columns(3)
        m1.metric("⭐ Total OTA Reviews", total_count, help="Aggregate reviews from all sources")
        m2.metric("📈 Avg Rating Score", f"{avg_rating:.1f} / 5.0", help="Average guest rating")
        m3.metric("❤️ Positive Sentiment", f"{pos_pct}%", help="Percentage of overall positive feedback")

        # ── Sentiment Breakdown Bar ──
        neu_count = len(rdf[rdf["sentiment"] == "Neutral"])
        neg_count = len(rdf[rdf["sentiment"] == "Negative"])

        pos_bar = (pos_count / total_count * 100) if total_count > 0 else 0
        neu_bar = (neu_count / total_count * 100) if total_count > 0 else 0
        neg_bar = (neg_count / total_count * 100) if total_count > 0 else 0

        st.markdown(f"""
        <div style='margin: 15px 0 25px 0;'>
            <div style='display:flex; justify-content:space-between; align-items:center; font-size:0.8rem; color:var(--text-muted); margin-bottom:6px; flex-wrap:wrap; gap:4px;'>
                <span>Guest Sentiment Distribution</span>
                <span>🟢 Positive ({pos_bar:.0f}%) | 🟡 Neutral ({neu_bar:.0f}%) | 🔴 Negative ({neg_bar:.0f}%)</span>
            </div>
            <div style='display:flex; height:12px; border-radius:6px; overflow:hidden; background:var(--border-color);'>
                <div style='width:{pos_bar}%; background:#10b981;' title='Positive'></div>
                <div style='width:{neu_bar}%; background:#f59e0b;' title='Neutral'></div>
                <div style='width:{neg_bar}%; background:#ef4444;' title='Negative'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Aspect Breakdown Grid ──
        aspect_sentiment = {}
        for aspect in ASPECTS.keys():
            aspect_reviews = rdf[rdf["aspects"].apply(lambda x: aspect in x)]
            total_asp = len(aspect_reviews)
            if total_asp > 0:
                pos_asp = len(aspect_reviews[aspect_reviews["sentiment"] == "Positive"])
                pct = round((pos_asp / total_asp) * 100)
            else:
                pct = None
            aspect_sentiment[aspect] = (pct, total_asp)

        st.markdown("<div class='section-title'>Aspect-Based Guest Sentiment</div>", unsafe_allow_html=True)
        res_col1, res_col2 = st.columns(2)

        with res_col1:
            # Food & Dining
            score, count = aspect_sentiment["Food & Dining"]
            if score is not None:
                color = "#10b981" if score >= 70 else "#fbbf24"
                advice = ("Insulate room-service food carriers to prevent cold food. Review morning buffet temperature logs and conduct a chef taste-audit." 
                          if score < 70 else 
                          "Guests love the buffet and local Kashmiri Kahwa. Maintain current recipes and food safety standards.")
                st.markdown(f"""
                <div style='background:rgba(255,255,255,0.02); border:1px solid rgba(148,163,184,0.15); border-radius:10px; padding:15px; margin-bottom:15px;'>
                    <div style='font-weight:600; display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px; flex-wrap:wrap; gap:4px; min-width:0;'>
                        <span style='flex-shrink:0;'>🍴 Food & Dining</span>
                        <span style='color:{color}; font-weight:700; text-align:right;'>{score}% Positive ({count} reviews)</span>
                    </div>
                    <div style='height:6px; border-radius:3px; background:#334155; margin-bottom:8px; overflow:hidden;'>
                        <div style='width:{score}%; height:100%; background:{color};'></div>
                    </div>
                    <p style='font-size:0.8rem; opacity:0.8; margin:0;'><b>Operational Advice:</b> {advice}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='background:rgba(255,255,255,0.02); border:1px solid rgba(148,163,184,0.15); border-radius:10px; padding:15px; margin-bottom:15px; opacity:0.6;'>
                    <div style='font-weight:600;'>🍴 Food & Dining</div>
                    <p style='font-size:0.8rem; margin:0;'>No guest reviews available regarding the dining experience yet.</p>
                </div>
                """, unsafe_allow_html=True)

            # Heating & Plumbing
            score, count = aspect_sentiment["Heating & Plumbing"]
            if score is not None:
                color = "#10b981" if score >= 70 else "#ef4444"
                advice = ("Audit fuel limits for backup generators during freezing night hours. Ensure geyser timers are set 1 hour before peak guest wake-up times (6:00 AM)." 
                          if score < 70 else 
                          "Heating and hot water systems are operational and satisfying guests. Continue routine checks.")
                st.markdown(f"""
                <div style='background:rgba(255,255,255,0.02); border:1px solid rgba(148,163,184,0.15); border-radius:10px; padding:15px; margin-bottom:15px;'>
                    <div style='font-weight:600; display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px; flex-wrap:wrap; gap:4px; min-width:0;'>
                        <span style='flex-shrink:0;'>🔥 Heating & Plumbing</span>
                        <span style='color:{color}; font-weight:700; text-align:right;'>{score}% Positive ({count} reviews)</span>
                    </div>
                    <div style='height:6px; border-radius:3px; background:#334155; margin-bottom:8px; overflow:hidden;'>
                        <div style='width:{score}%; height:100%; background:{color};'></div>
                    </div>
                    <p style='font-size:0.8rem; opacity:0.8; margin:0;'><b>Operational Advice:</b> {advice}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='background:rgba(255,255,255,0.02); border:1px solid rgba(148,163,184,0.15); border-radius:10px; padding:15px; margin-bottom:15px; opacity:0.6;'>
                    <div style='font-weight:600;'>🔥 Heating & Plumbing</div>
                    <p style='font-size:0.8rem; margin:0;'>No guest reviews available regarding heating/plumbing yet.</p>
                </div>
                """, unsafe_allow_html=True)

        with res_col2:
            # Service & Hospitality
            score, count = aspect_sentiment["Service & Hospitality"]
            if score is not None:
                color = "#10b981" if score >= 70 else "#ef4444"
                advice = ("Proactively address room service delay complaints. Conduct front-desk logging checks and coordination reviews." 
                          if score < 70 else 
                          "Service hospitality levels are outstanding. Highlight polite and helpful staff members in the team meeting.")
                st.markdown(f"""
                <div style='background:rgba(255,255,255,0.02); border:1px solid rgba(148,163,184,0.15); border-radius:10px; padding:15px; margin-bottom:15px;'>
                    <div style='font-weight:600; display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px; flex-wrap:wrap; gap:4px; min-width:0;'>
                        <span style='flex-shrink:0;'>🛎️ Service & Hospitality</span>
                        <span style='color:{color}; font-weight:700; text-align:right;'>{score}% Positive ({count} reviews)</span>
                    </div>
                    <div style='height:6px; border-radius:3px; background:#334155; margin-bottom:8px; overflow:hidden;'>
                        <div style='width:{score}%; height:100%; background:{color};'></div>
                    </div>
                    <p style='font-size:0.8rem; opacity:0.8; margin:0;'><b>Operational Advice:</b> {advice}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='background:rgba(255,255,255,0.02); border:1px solid rgba(148,163,184,0.15); border-radius:10px; padding:15px; margin-bottom:15px; opacity:0.6;'>
                    <div style='font-weight:600;'>🛎️ Service & Hospitality</div>
                    <p style='font-size:0.8rem; margin:0;'>No guest reviews available regarding services yet.</p>
                </div>
                """, unsafe_allow_html=True)

            # Room & Cleanliness
            score, count = aspect_sentiment["Room & Cleanliness"]
            if score is not None:
                color = "#10b981" if score >= 70 else "#fbbf24"
                advice = ("Audit blanket cleanliness, sheet changing processes, and verify that dusty corners in wood heritage cabins are cleaned." 
                          if score < 70 else 
                          "Guests appreciate clean rooms, cozy linen, and garden/lake views. Maintain strict room inspection schedules.")
                st.markdown(f"""
                <div style='background:rgba(255,255,255,0.02); border:1px solid rgba(148,163,184,0.15); border-radius:10px; padding:15px; margin-bottom:15px;'>
                    <div style='font-weight:600; display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px; flex-wrap:wrap; gap:4px; min-width:0;'>
                        <span style='flex-shrink:0;'>🛏️ Room & Cleanliness</span>
                        <span style='color:{color}; font-weight:700; text-align:right;'>{score}% Positive ({count} reviews)</span>
                    </div>
                    <div style='height:6px; border-radius:3px; background:#334155; margin-bottom:8px; overflow:hidden;'>
                        <div style='width:{score}%; height:100%; background:{color};'></div>
                    </div>
                    <p style='font-size:0.8rem; opacity:0.8; margin:0;'><b>Operational Advice:</b> {advice}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='background:rgba(255,255,255,0.02); border:1px solid rgba(148,163,184,0.15); border-radius:10px; padding:15px; margin-bottom:15px; opacity:0.6;'>
                    <div style='font-weight:600;'>🛏️ Room & Cleanliness</div>
                    <p style='font-size:0.8rem; margin:0;'>No guest reviews available regarding rooms yet.</p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Full review list ──
        st.markdown("<div class='section-title'>All Guest Reviews</div>", unsafe_allow_html=True)
        for _, row in rdf.iterrows():
            stars = "⭐" * int(row["rating"])
            badge_color = {"Positive": "#10b981", "Neutral": "#f59e0b", "Negative": "#ef4444"}.get(row["sentiment"], "#64748b")
            aspects_html = " ".join([f"<span style='background:rgba(59,130,246,0.15);color:var(--primary-color);border-radius:4px;padding:2px 7px;font-size:0.7rem;margin-right:4px;'>{a}</span>" for a in row["aspects"]])
            st.markdown(f"""
            <div style='background:var(--secondary-bg-color);border:1px solid var(--border-color);border-radius:10px;padding:14px;margin-bottom:10px;overflow:hidden;'>
                <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;flex-wrap:wrap;gap:4px;'>
                    <span style='font-weight:600;color:var(--text-color);min-width:0;overflow:hidden;text-overflow:ellipsis;'>{row["guest_name"]}</span>
                    <span style='color:#f59e0b;font-size:0.9rem;flex-shrink:0;'>{stars}</span>
                </div>
                <p style='font-size:0.85rem;color:var(--text-muted);margin:0 0 8px 0;word-break:break-word;overflow-wrap:break-word;'>{row["review_text"]}</p>
                <div style='display:flex;align-items:center;gap:8px;flex-wrap:wrap;'>
                    <span style='background:{badge_color};color:white;border-radius:4px;padding:2px 8px;font-size:0.7rem;font-weight:600;flex-shrink:0;'>{row["sentiment"]}</span>
                    {aspects_html}
                    <span style='color:var(--text-muted);font-size:0.75rem;margin-left:auto;white-space:nowrap;'>{row["source"]} · {row["date"]}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No reviews found. Reviews will appear here once guests post on OTA platforms.")

# ── TAB 4: Travel Risk & Demand ──────────────────────────
with tab_risk:
    st.markdown("<div class='section-title'>✈️ Srinagar Air Connectivity & Demand Risk Matrix</div>", unsafe_allow_html=True)

    # Fetch live Srinagar air connectivity risk data — shown with spinner
    # so the rest of the dashboard is not blocked during API calls.
    with st.spinner("🌤️ Loading live weather & risk data..."):
        live_risk = get_srinagar_live_risk_data()
    risk_score = live_risk["risk_score"]
    weather = live_risk["weather"]

    # ── Live Airport Weather Status Card ──
    _w_snow = weather["snow"] if isinstance(weather["snow"], (int, float)) else 0
    _w_rain = weather["rain"] if isinstance(weather["rain"], (int, float)) else 0
    _w_vis  = weather["visibility_km"] if isinstance(weather["visibility_km"], (int, float)) else 10
    weather_icon = "❄️" if _w_snow > 0 else ("🌧️" if _w_rain > 0 else ("🌫️" if _w_vis < 2 else "☀️"))
    st.markdown(f"""
    <div style='background:var(--secondary-bg-color); border:1px solid var(--border-card); border-radius:12px; padding:16px; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;'>
        <div>
            <div style='font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:1px; font-weight:600;'>📍 Srinagar International Airport (SXR)</div>
            <div style='font-size:1.15rem; font-weight:700; color:var(--text-color); display:flex; align-items:center; gap:8px; margin-top:2px;'>
                <span>{weather_icon} {weather["desc"]}</span>
                <span style='color:var(--text-muted);'>•</span>
                <span style='color:var(--primary-color);'>{weather["temp"]}°C</span>
            </div>
        </div>
        <div style='display:flex; gap:20px; margin-top:10px;'>
            <div>
                <div style='font-size:0.7rem; color:var(--text-muted);'>Visibility</div>
                <div style='font-size:0.9rem; font-weight:600; color:var(--text-color);'>{weather["visibility_km"]} km</div>
            </div>
            <div>
                <div style='font-size:0.7rem; color:var(--text-muted);'>Wind Speed</div>
                <div style='font-size:0.9rem; font-weight:600; color:var(--text-color);'>{weather["wind_speed"]} km/h</div>
            </div>
            <div>
                <div style='font-size:0.7rem; color:var(--text-muted);'>Active Snow/Rain</div>
                <div style='font-size:0.9rem; font-weight:600; color:var(--text-color);'>{max(weather["snow"], weather["rain"])} mm</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Risk index gauge ──
    risk_label = "Moderate Risk" if 40 <= risk_score < 70 else ("High Risk" if risk_score >= 70 else "Low Risk")
    gauge_color = "#f59e0b" if risk_label == "Moderate Risk" else ("#ef4444" if risk_label == "High Risk" else "#10b981")

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=risk_score,
        title={"text": "Overall Demand Risk Index", "font": {"size": 14, "color": "#94a3b8"}},
        delta={"reference": 50, "increasing": {"color": "#ef4444"}, "decreasing": {"color": "#10b981"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#475569", "tickfont": {"color": "#94a3b8"}},
            "bar": {"color": gauge_color},
            "bgcolor": "#1e293b",
            "steps": [
                {"range": [0, 40], "color": "rgba(16,185,129,0.15)"},
                {"range": [40, 70], "color": "rgba(245,158,11,0.15)"},
                {"range": [70, 100], "color": "rgba(239,68,68,0.15)"},
            ],
            "threshold": {"line": {"color": "white", "width": 2}, "thickness": 0.75, "value": risk_score},
        },
        number={"font": {"size": 36, "color": gauge_color}, "suffix": "/100"}
    ))
    fig_gauge.update_layout(**CHART, height=280)

    g1, g2 = st.columns([2, 3], gap="small")
    with g1:
        st.markdown("<div class='scroll-through-chart'>", unsafe_allow_html=True)
        st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background:var(--secondary-bg-color);border:1px solid var(--border-color);border-radius:10px;padding:14px;margin-top:-10px;'>
            <div style='font-size:1rem;font-weight:700;color:{gauge_color};margin-bottom:4px;'>⚠️ {risk_label}</div>
            <div style='font-size:0.8rem;color:var(--text-muted);'>Composite score based on flight cancellations, weather events, political advisories, and seasonal demand patterns.</div>
        </div>
        """, unsafe_allow_html=True)

    with g2:
        st.markdown("<div class='section-title'>Route Cancellation Probability by Month</div>", unsafe_allow_html=True)
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        cancel_prob = [72, 68, 45, 20, 15, 10, 8, 12, 18, 30, 55, 78]
        _cur_month_idx = date.today().month - 1  # 0-indexed
        colors_bar = []
        for i, p in enumerate(cancel_prob):
            if i == _cur_month_idx:
                colors_bar.append("#8b5cf6")  # Highlight current month in purple
            elif p >= 60:
                colors_bar.append("#ef4444")
            elif p >= 30:
                colors_bar.append("#f59e0b")
            else:
                colors_bar.append("#10b981")
        fig_cancel = go.Figure(go.Bar(
            x=months, y=cancel_prob,
            marker_color=colors_bar,
            text=[f"{p}%" for p in cancel_prob],
            textposition="outside",
            hovertemplate="<b>%{x}</b>: %{y}% cancellation risk<extra></extra>"
        ))
        fig_cancel.update_layout(**CHART)
        fig_cancel.update_yaxes(range=[0, 100], ticksuffix="%", gridcolor="rgba(255,255,255,0.05)", showline=False, zeroline=False)
        st.markdown("<div class='scroll-through-chart'>", unsafe_allow_html=True)
        st.plotly_chart(fig_cancel, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
        st.caption("📊 Historical probability estimates based on Srinagar Airport seasonal patterns (SXR). Not live flight data. Current month highlighted in purple.")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # ── Risk matrix table ──
    st.markdown("<div class='section-title'>Risk Factor Matrix</div>", unsafe_allow_html=True)

    matrix_factors = []
    matrix_likelihood = []
    matrix_impact = []
    matrix_level = []
    matrix_mitigation = []

    for f in live_risk["active_factors"]:
        if f["factor"] == "☀️ Favorable Meteorological Conditions" and len(live_risk["active_factors"]) > 1:
            continue
        matrix_factors.append(f"⚡ Live: {f['factor']}")
        matrix_likelihood.append("Current")
        matrix_impact.append("High" if f["level"] in ["Critical", "High"] else "Medium")
        matrix_level.append("🔴 Critical" if f["level"] == "Critical" else ("🟠 High" if f["level"] == "High" else "🟡 Moderate"))
        matrix_mitigation.append(f["mitigation"])
        
    # Only show static risk factors that are relevant to the current month
    _cm = date.today().month  # 1–12
    _all_static = [
        # (factor, likelihood, impact, level, mitigation, relevant_months)
        ("❄️ Winter Fog (Dec–Feb)", "High",   "High",   "🔴 Critical",
         "Flexible cancellation policy + proactive guest SMS alerts",
         [12, 1, 2]),
        ("🌧️ Monsoon Disruptions (Jul–Sep)", "Medium", "Medium", "🟡 Moderate",
         "Monitor IMD forecasts 72 hrs ahead; maintain alternate road-trip packages",
         [7, 8, 9]),
        ("🔌 Airport Power Outage", "Low",    "High",   "🟠 High",
         "Backup generator protocols; pre-check-in communication via WhatsApp",
         list(range(1, 13))),  # year-round risk
        ("🌐 Political Advisory / Alerts", "Medium", "High", "🔴 Critical",
         "Subscribe to MEA alerts; issue reassurance emails to confirmed bookings",
         list(range(1, 13))),  # year-round risk
        ("📉 Off-Season Demand Drop", "High",  "Medium", "🟡 Moderate",
         "Launch winter packages & early-bird discounts by October",
         [11, 12, 1, 2, 3]),
        ("🛫 Single-Runway Bottleneck", "Medium", "High", "🟠 High",
         "Offer Jammu transfer packages as contingency for diverted flights",
         list(range(1, 13))),  # year-round risk
    ]
    for _sf, _sl, _si, _slv, _sm, _months in _all_static:
        if _cm in _months:
            matrix_factors.append(_sf)
            matrix_likelihood.append(_sl)
            matrix_impact.append(_si)
            matrix_level.append(_slv)
            matrix_mitigation.append(_sm)
    risk_data = {
        "Risk Factor": matrix_factors,
        "Likelihood/State": matrix_likelihood,
        "Impact": matrix_impact,
        "Risk Level": matrix_level,
        "Mitigation Strategy": matrix_mitigation,
    }

    risk_df = pd.DataFrame(risk_data)
    st.markdown("<div class='scroll-through-table'>", unsafe_allow_html=True)
    st.dataframe(risk_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # ── Operational Checklist (persisted per hotel in Firebase) ──
    st.markdown("<div class='section-title'>📋 Pre-Season Operational Checklist</div>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.82rem;color:var(--text-muted);margin-bottom:14px;'>"
        "Check off items as your team completes them — progress updates live and is saved per hotel.</p>",
        unsafe_allow_html=True
    )

    # Load saved state from Firebase
    _saved_chk = load_checklist(hotel_id)

    _chk_items = [
        ("chk_notam",      "Subscribe to airport NOTAM alerts"),
        ("chk_whatsapp",   "Set up 48-hr guest arrival reminders (WhatsApp)"),
        ("chk_ota_policy", "Update cancellation policy on all OTAs"),
        ("chk_supplies",   "Stock emergency supplies for weather disruptions"),
        ("chk_transport",  "Prepare alternate transport contacts (taxi/road)"),
        ("chk_staff",      "Train staff on flight delay handling protocol"),
        ("chk_tour_ops",   "Set up local partnership with tour operators"),
        ("chk_faq",        "Create weather-disruption guest FAQ sheet"),
        ("chk_refund",     "Configure auto-refund rules for force majeure"),
        ("chk_generator",  "Verify generator fuel stock for winter months"),
    ]

    # ── Step 1: Render checkboxes first → collect live state ──
    chk1, chk2 = st.columns(2)
    _new_state = {}
    for i, (key, label) in enumerate(_chk_items):
        col = chk1 if i < 5 else chk2
        with col:
            _new_state[key] = st.checkbox(
                label,
                value=bool(_saved_chk.get(key, False)),
                key=f"risk_chk_{key}"
            )

    # ── Step 2: Compute progress from live checkbox state ──
    _total_items = len(_chk_items)
    _done_items  = sum(1 for key, _ in _chk_items if _new_state.get(key, False))
    _pct         = int((_done_items / _total_items) * 100)
    _remaining   = _total_items - _done_items

    if _pct == 100:
        _bar_color = "#10b981"
        _milestone = "🏆 All tasks complete — your hotel is fully prepared!"
        _badge     = "  ✅ ACHIEVED"
    elif _pct >= 70:
        _bar_color = "#3b82f6"
        _milestone = f"⭐ Great progress — {_remaining} task{'s' if _remaining > 1 else ''} left"
        _badge     = ""
    elif _pct >= 40:
        _bar_color = "#f59e0b"
        _milestone = f"🔧 Getting there — {_remaining} tasks remaining"
        _badge     = ""
    else:
        _bar_color = "#ef4444"
        _milestone = f"⚠️ {_remaining} tasks need attention before season opens"
        _badge     = ""

    # ── Step 3: Render progress bar using native widgets ──
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    _col_label, _col_pct = st.columns([5, 1])
    with _col_label:
        st.markdown(
            f"<p style='font-size:0.75rem;font-weight:700;color:var(--text-muted);"
            f"text-transform:uppercase;letter-spacing:1px;margin:0;padding:0;'>"
            f"Season Readiness{_badge}</p>",
            unsafe_allow_html=True
        )
    with _col_pct:
        st.markdown(
            f"<p style='font-size:1.25rem;font-weight:800;color:{_bar_color};"
            f"text-align:right;margin:0;padding:0;'>{_pct}%</p>",
            unsafe_allow_html=True
        )

    st.progress(_pct / 100)

    # Tick labels under the bar
    _ticks = st.columns(5)
    for _i, _mark in enumerate([0, 25, 50, 75, 100]):
        with _ticks[_i]:
            _align = "left" if _i == 0 else ("right" if _i == 4 else "center")
            _col   = _bar_color if _pct >= _mark else "#475569"
            st.markdown(
                f"<p style='font-size:0.65rem;font-weight:600;color:{_col};"
                f"text-align:{_align};margin:0;'>{_mark}%</p>",
                unsafe_allow_html=True
            )

    st.markdown(
        f"<p style='font-size:0.8rem;color:var(--text-muted);margin-top:6px;'>"
        f"{_milestone} &nbsp;&nbsp;"
        f"<strong style='color:{_bar_color};'>{_done_items}/{_total_items} done</strong></p>",
        unsafe_allow_html=True
    )

    # ── Step 4: Save button ──
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    if st.button("💾 Save Checklist", key="save_checklist_btn"):
        save_checklist(hotel_id, _new_state)
        st.success("✅ Checklist saved!")


    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # ── WhatsApp Guest Outreach Panel ──
    st.markdown("<div class='section-title'>💬 Guest Outreach — Send WhatsApp Messages</div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.85rem;color:var(--text-muted);margin-bottom:16px;'>Select any guest to send them a proactive WhatsApp message. Upcoming bookings are shown first.</p>", unsafe_allow_html=True)

    today = date.today()
    arriving_bookings = pd.DataFrame()
    if not df.empty and "Check-in" in df.columns:
        try:
            df_outreach = df.copy()
            df_outreach["Check-in-dt"] = pd.to_datetime(df_outreach["Check-in"], errors="coerce")

            # Try upcoming (next 30 days) first
            upcoming = df_outreach[
                df_outreach["Check-in-dt"].dt.date >= today
            ].copy().sort_values("Check-in-dt")

            if not upcoming.empty:
                arriving_bookings = upcoming
            else:
                # Fallback: show all bookings sorted by most recent check-in
                arriving_bookings = df_outreach.dropna(subset=["Check-in-dt"]).copy().sort_values(
                    "Check-in-dt", ascending=False
                )
        except Exception:
            arriving_bookings = df.copy() if not df.empty else pd.DataFrame()

    if not arriving_bookings.empty:
        selected_guest = st.selectbox(
            "Select guest to contact:",
            options=arriving_bookings.index.tolist(),
            format_func=lambda i: (
                f"📅 {arriving_bookings.loc[i, 'Guest Name']} — Check-in: {arriving_bookings.loc[i, 'Check-in']}"
            )
        )
        guest_row = arriving_bookings.loc[selected_guest]
        guest_name = guest_row.get("Guest Name", "Guest")
        guest_checkin = guest_row.get("Check-in", "soon")
        guest_phone = str(guest_row.get("Phone", "")).replace("+", "").strip()

        msg_type = st.radio(
            "Message type:",
            ["✈️ Flight Delay Alert", "🌡️ Weather Warning", "🏨 Arrival Reminder", "✏️ Custom"],
            horizontal=True
        )

        if msg_type == "✈️ Flight Delay Alert":
            custom_message = (
                f"Dear {guest_name}, we at {hotel_name} wanted to inform you that Srinagar airport "
                f"is experiencing flight delays due to adverse weather. Please contact your airline directly. "
                f"We are ready to accommodate your adjusted arrival. Stay safe! 🏔️"
            )
        elif msg_type == "🌡️ Weather Warning":
            custom_message = (
                f"Dear {guest_name}, Srinagar is experiencing heavy snowfall this week. Your room at "
                f"{hotel_name} is warm and fully prepared for your stay. We recommend packing thermal wear. "
                f"Looking forward to hosting you on {guest_checkin}! ❄️"
            )
        elif msg_type == "🏨 Arrival Reminder":
            custom_message = (
                f"Dear {guest_name}, this is a friendly reminder from {hotel_name}. "
                f"We are excited to welcome you on {guest_checkin}. "
                f"Our team is ready to ensure a memorable stay. Please let us know your ETA. 🙏"
            )
        else:
            custom_message = f"Dear {guest_name}, "

        edited_message = st.text_area("✏️ Edit before sending:", value=custom_message, height=120)

        if guest_phone and guest_phone != "nan":
            encoded_msg = urllib.parse.quote(edited_message)
            wa_url = f"https://wa.me/{guest_phone}?text={encoded_msg}"
            st.markdown(f"""
                <a href="{wa_url}" target="_blank" style="text-decoration:none;">
                    <button style="width:100%; border-radius:10px; padding:12px; background:#25d366;
                                   color:white; border:none; cursor:pointer; font-weight:600;
                                   font-size:0.95rem; margin-top:8px;
                                   box-shadow:0 4px 14px rgba(37,211,102,0.25);">
                        💬 Send via WhatsApp to {guest_name}
                    </button>
                </a>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ This guest has no valid phone number on record.")
    else:
        st.info("No bookings found. Add your first booking via the **Add Booking** page to enable guest outreach.")

# CSS Unlock — triggers the dynamic has-selector to reveal the page
st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)