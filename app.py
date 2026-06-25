import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
import urllib.parse
import sys
from datetime import date, datetime

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sheets_db import (
    load_bookings,
    get_hotel_by_id,
    get_google_reviews,
    load_reviews,
    save_review_to_firebase,
    update_hotel_ota_links,
    sync_hotel_reviews,
    get_srinagar_live_risk_data,
    load_checklist,
    save_checklist,
)
from login import show_login
from style import apply_style, sidebar_logo, render_custom_navigation

# ── Init session state ────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "hotel" not in st.session_state:
    st.session_state.hotel = None

st.set_page_config(
    page_title="Kashmir Hotel Analytics",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded" if st.session_state.get("logged_in") else "collapsed"
)

# ── Flash prevention: hide sidebar & nav instantly on every load ──
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
    font=dict(family="Inter, sans-serif", color="#64748b", size=11),
    xaxis=dict(
        showgrid=False,
        showline=False,
        zeroline=False,
        tickfont=dict(color="#475569", size=11),
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.04)",
        showline=False,
        zeroline=False,
        tickfont=dict(color="#475569", size=11),
    ),
    margin=dict(t=30, b=20, l=10, r=10),
    hoverlabel=dict(
        bgcolor="#0f172a",
        font_size=13,
        font_family="Inter",
        bordercolor="rgba(59,130,246,0.3)"
    ),
)

BLUES = [[0, "#bfdbfe"], [1, "#2563eb"]]
VIBRANT_PURPLE = "#8b5cf6"
COLOR_SEQ = ["#3b82f6", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"]

# ══════════════════════════════════════════════════════════
# NOT LOGGED IN — handle invite links + session restore
# ══════════════════════════════════════════════════════════
if not st.session_state.get("logged_in"):
    st.markdown("""
        <style>
        section[data-testid="stSidebar"],
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    invite_token = st.query_params.get("invite")
    if invite_token:
        st.session_state["invite_token"] = invite_token
        st.switch_page("pages/4_Setup_Account.py")
        st.stop()

    hid = st.query_params.get("hid")
    if hid:
        if hid == "ADMIN":
            st.session_state["logged_in"] = True
            st.session_state["hotel"] = {"hotel_id": "ADMIN", "name": "Administrator", "plan": "admin"}
            st.rerun()
        else:
            hotel = get_hotel_by_id(hid)
            if hotel:
                st.session_state["logged_in"] = True
                st.session_state["hotel"] = hotel
                st.rerun()

    show_login()
    st.stop()

# ══════════════════════════════════════════════════════════
# LOGGED IN — dashboard
# ══════════════════════════════════════════════════════════
hotel = st.session_state.hotel
hotel_id = hotel["hotel_id"]
hotel_name = hotel["name"]
st.query_params["hid"] = hotel_id

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

    season = st.selectbox("Season", ["Full Year","Winter (Jan–Mar)","Spring (Apr–Jun)",
                                     "Summer (Jul–Sep)","Autumn (Oct–Dec)"])

    st.divider()
    support_link = "https://wa.me/918491828292?text=Hello, I need help with my hotel analytics dashboard."
    st.markdown(f"""
        <a href='{support_link}' target='_blank' style='text-decoration:none;'>
            <button class='support-btn'> 💬 Contact Support </button>
        </a>
    """, unsafe_allow_html=True)

    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.hotel = None
        st.session_state.pop("checklist_state", None)
        st.query_params.clear()
        st.cache_data.clear()
        st.rerun()

# ── Admin welcome screen ──────────────────────────────────
if hotel_id == "ADMIN":
    st.markdown("<p class='page-title'>⚙️ Administrator</p>", unsafe_allow_html=True)
    st.markdown("<p class='page-sub'>Welcome to Kashmir Hotel Analytics Admin.</p>", unsafe_allow_html=True)
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.info("👋 Use the sidebar to navigate to the **Admin Panel** to manage hotels.")
    st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)
    st.stop()

# ── Load data ─────────────────────────────────────────────
df = load_bookings(hotel_id)

# ── Header ────────────────────────────────────────────────
hc1, hc2 = st.columns([5, 1])
with hc1:
    st.markdown(f"<p class='page-title'>{hotel_name}</p>", unsafe_allow_html=True)
    st.markdown("<p class='page-sub'>Revenue & Occupancy Dashboard</p>", unsafe_allow_html=True)
with hc2:
    st.markdown(f"<br><span class='badge'>{season}</span>", unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

SM = {
    "Full Year": [1,2,3,4,5,6,7,8,9,10,11,12],
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

total_rev = int(fdf["Amount (₹)"].sum())
total_book = len(fdf)
total_nights = int(fdf["Nights"].sum())
avg_nights = round(fdf["Nights"].mean(), 1) if total_book else 0
avg_book = int(fdf["Amount (₹)"].mean()) if total_book else 0

# ── Premium KPIs ──────────────────────────────────────────
total_commission = fdf["commission_paid"].sum()
net_revenue = total_rev - total_commission
adr = net_revenue / total_nights if total_nights > 0 else 0
occupancy_rate = (total_nights / (30 * 30)) * 100

# ── Tabs ──────────────────────────────────────────────────
tab_overview, tab_bookings, tab_reviews, tab_risk = st.tabs([
    "📊 Financial Overview",
    "📋 Bookings & Operations",
    "⭐ Reputation & Reviews",
    "✈️ Travel Risk & Demand"
])

# ══════════════════════════════════════════════════════════
# TAB 1 — FINANCIAL OVERVIEW
# ══════════════════════════════════════════════════════════
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
        c1, c2 = st.columns([3, 2])
        with c1:
            st.markdown("<div class='section-title'>Monthly Revenue</div>", unsafe_allow_html=True)
            rev = (fdf.groupby(["Month_Num","Month"])["Amount (₹)"]
                   .sum().reset_index().sort_values("Month_Num"))
            fig1 = go.Figure(go.Bar(
                x=rev["Month"],
                y=rev["Amount (₹)"],
                marker=dict(color=rev["Amount (₹)"], colorscale="Sunset", line=dict(width=0)),
                text=rev["Amount (₹)"].apply(lambda x: f"₹{x/1000:.1f}k" if x >= 1000 else f"₹{x}"),
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>₹%{y:,}<extra></extra>"
            ))
            fig1.update_layout(**CHART)
            st.plotly_chart(fig1, use_container_width=True)

        with c2:
            st.markdown("<div class='section-title'>Guest Origins</div>", unsafe_allow_html=True)
            src = fdf["Source"].value_counts().reset_index()
            src.columns = ["Source","Guests"]
            fig2 = px.pie(src, names="Source", values="Guests", hole=0.6,
                          color_discrete_sequence=COLOR_SEQ)
            fig2.update_traces(
                textposition="outside",
                textinfo="label+percent",
                pull=[0.06 if i == 0 else 0 for i in range(len(src))],
                textfont=dict(size=11, color="#94a3b8"),
                marker=dict(line=dict(color="#060b18", width=3))
            )
            fig2.update_layout(**CHART, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        c3, c4 = st.columns([2, 3])
        with c3:
            st.markdown("<div class='section-title'>Room Type</div>", unsafe_allow_html=True)
            rooms = fdf["Room Type"].value_counts().reset_index()
            rooms.columns = ["Room Type","Count"]
            fig3 = go.Figure(go.Bar(
                x=rooms["Count"],
                y=rooms["Room Type"],
                orientation="h",
                marker=dict(color=COLOR_SEQ[:len(rooms)], line=dict(width=0), opacity=0.9),
                text=rooms["Count"],
                textposition="outside",
                textfont=dict(color="#94a3b8", size=12),
                hovertemplate="<b>%{y}</b>: %{x} bookings<extra></extra>"
            ))
            fig3.update_layout(**CHART)
            st.plotly_chart(fig3, use_container_width=True)

        with c4:
            st.markdown("<div class='section-title'>Bookings Over Time</div>", unsafe_allow_html=True)
            trend = (fdf.groupby(["Month_Num","Month"])
                     .size().reset_index(name="Bookings").sort_values("Month_Num"))
            fig4 = go.Figure(go.Scatter(
                x=trend["Month"],
                y=trend["Bookings"],
                mode="lines+markers",
                line=dict(color=VIBRANT_PURPLE, width=3, shape="spline"),
                marker=dict(size=10, color=VIBRANT_PURPLE, line=dict(color="white", width=2)),
                fill="tozeroy",
                fillcolor="rgba(139, 92, 246, 0.15)",
                hovertemplate="<b>%{x}</b>: %{y}<extra></extra>"
            ))
            fig4.update_layout(**CHART)
            st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════════════════
# TAB 2 — BOOKINGS & OPERATIONS
# ══════════════════════════════════════════════════════════
with tab_bookings:
    if total_book == 0:
        st.info("No bookings for this season.")
    else:
        ci1, ci2 = st.columns([1, 2])
        with ci1:
            st.markdown("<div class='section-title'>Quick Insights</div>", unsafe_allow_html=True)
            src = fdf["Source"].value_counts().reset_index()
            src.columns = ["Source","Guests"]
            rooms = fdf["Room Type"].value_counts().reset_index()
            rooms.columns = ["Room Type","Count"]

            top_src = src.iloc[0]["Source"] if len(src) else "—"
            top_room = rooms.iloc[0]["Room Type"] if len(rooms) else "—"
            foreign = src[src["Source"]=="Foreign"]["Guests"].sum() \
                      if "Foreign" in src["Source"].values else 0
            fp = round(foreign / src["Guests"].sum() * 100) \
                 if src["Guests"].sum() > 0 else 0
            conf = len(fdf[fdf["Status"]=="Confirmed"]) \
                   if "Confirmed" in fdf["Status"].values else 0

            rows = [
                ("Top guest market", top_src),
                ("Most booked room", top_room),
                ("Foreign guests", f"{fp}%"),
                ("Confirmed bookings", str(conf)),
                ("Total revenue", f"₹{total_rev:,}"),
            ]
            html = "<div class='card-wrap'>"
            for lbl, val in rows:
                html += (f"<div class='insight-row'><span>{lbl}</span>"
                         f"<span class='insight-val'>{val}</span></div>")
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)

        with ci2:
            st.markdown("<div class='section-title'>Recent Bookings</div>", unsafe_allow_html=True)
            recent = fdf.sort_values("Check-in", ascending=False).head(8).copy()

            def generate_wa_link(row):
                phone = str(row.get("Phone", "")).replace("+", "").strip()
                if not phone or phone == "nan":
                    return None
                guest = row.get("Guest Name", "Guest")
                msg = f"Hello {guest}, this is {hotel_name} regarding your booking."
                return f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"

            recent["WhatsApp"] = recent.apply(generate_wa_link, axis=1)
            st.dataframe(recent, use_container_width=True, hide_index=True,
                         column_config={
                             "WhatsApp": st.column_config.LinkColumn("Contact", display_text="💬 WhatsApp")
                         })

# ══════════════════════════════════════════════════════════
# TAB 3 — REPUTATION & REVIEWS
# ══════════════════════════════════════════════════════════
with tab_reviews:
    st.markdown("""
    <style>
    .review-container {
        background: var(--secondary-bg-color) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
        padding: 14px 16px !important;
        margin-bottom: 16px !important;
    }
    .review-status-row {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 6px 16px !important;
        font-size: 0.8rem !important;
        color: var(--text-color) !important;
    }
    .review-status-row span {
        white-space: nowrap !important;
    }
    .review-sentiment-box {
        background: var(--secondary-bg-color) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 12px 14px !important;
        margin-bottom: 12px !important;
    }
    .review-sentiment-box .flex-row {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        flex-wrap: wrap !important;
        gap: 6px 12px !important;
    }
    .review-aspect-badge {
        background: rgba(59,130,246,0.15) !important;
        color: var(--primary-color) !important;
        border-radius: 4px !important;
        padding: 2px 7px !important;
        font-size: 0.7rem !important;
        white-space: nowrap !important;
        display: inline-block !important;
        margin-right: 4px !important;
    }
    .review-item {
        background: var(--secondary-bg-color) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
        padding: 14px 16px !important;
        margin-bottom: 10px !important;
        overflow: hidden !important;
    }
    .review-item .review-header {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        margin-bottom: 6px !important;
        flex-wrap: wrap !important;
        gap: 4px 8px !important;
    }
    .review-item .review-text {
        font-size: 0.85rem !important;
        color: var(--text-muted) !important;
        margin: 0 0 8px 0 !important;
        word-break: break-word !important;
        overflow-wrap: break-word !important;
    }
    .review-item .review-footer {
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        flex-wrap: wrap !important;
    }
    @media (max-width: 600px) {
        .review-item .review-header {
            flex-direction: column !important;
            align-items: flex-start !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<p class='section-title'>⭐ OTA Reputation & Sentiment Analytics</p>", unsafe_allow_html=True)

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
        "Food & Dining": ['food','breakfast','dinner','lunch','buffet','taste','restaurant',
                          'chef','meal','delicious','rogan josh','kahwa','tea','mutton','eat'],
        "Heating & Plumbing": ['heating','heater','geyser','hot water','cold','freezing',
                                'water','plumbing','shower','bathroom','leak','warm'],
        "Service & Hospitality": ['service','staff','manager','hospitality','friendly',
                                   'rude','polite','help','reception','unhelpful','wait',
                                   'order','management'],
        "Room & Cleanliness": ['room','clean','dirty','sheet','blanket','bed','spacious',
                                'dusty','comfortable','view','garden','cabin','wooden','heritage'],
    }

    reviews_raw = load_reviews(hotel_id)

    with st.container():
        st.markdown("""
            <div style='background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.2);
                        border-radius:12px; padding:18px; margin-bottom:20px;'>
                <h4 style='margin:0 0 6px 0; color:var(--primary-color); font-size:1.15rem;'>
                    🔄 Live OTA Sync & Real-Time Sentiment Control Center</h4>
                <p style='font-size:0.8rem; color:var(--text-muted); margin:0;'>
                    Sync guest feedback automatically from Booking.com, Agoda, MakeMyTrip,
                    and Google, or write a custom review below to perform instant sentiment analysis.
                </p>
            </div>
        """, unsafe_allow_html=True)

    col_sync, col_manual = st.columns(2)

    with col_sync:
        st.markdown(
            "<p style='font-weight:600; color:var(--text-color); margin-bottom:8px; font-size:0.95rem;'>"
            "⚡ OTA Review Sync Status</p>",
            unsafe_allow_html=True
        )
        h_booking_url = hotel.get("booking_review_url", "")
        h_agoda_url = hotel.get("agoda_review_url", "")
        h_mmt_url = hotel.get("mmt_review_url", "") or hotel.get("mmt_url", "")
        h_google_place_id = hotel.get("google_place_id", "")

        status_items = []
        if h_booking_url:
            status_items.append("🟢 Booking.com")
        else:
            status_items.append("⚪ Booking.com")
        if h_agoda_url:
            status_items.append("🟢 Agoda")
        else:
            status_items.append("⚪ Agoda")
        if h_mmt_url:
            status_items.append("🟢 MakeMyTrip")
        else:
            status_items.append("⚪ MakeMyTrip")
        if h_google_place_id:
            status_items.append("🟢 Google Places")
        else:
            status_items.append("⚪ Google Places")

        st.markdown(f"""
            <div style='background:var(--secondary-bg-color); border:1px solid var(--border-color);
                        border-radius:8px; padding:10px 12px; margin-bottom:12px;'>
                <div style='font-size:0.75rem; color:var(--text-muted); text-transform:uppercase;
                            letter-spacing:0.5px; margin-bottom:6px;'>Connected Platforms</div>
                <div style='font-size:0.8rem; display:flex; gap:10px; flex-wrap:wrap; color:var(--text-color);'>
                    {" | ".join(status_items)}
                </div>
            </div>
        """, unsafe_allow_html=True)

        total_in_db = len(reviews_raw) if reviews_raw else 0
        any_configured = any([h_booking_url, h_agoda_url, h_mmt_url, h_google_place_id])

        if any_configured:
            st.markdown(f"""
                <div style='background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.2);
                            border-radius:8px; padding:12px; margin-bottom:12px;'>
                    <div style='font-size:0.85rem; color:#10b981; font-weight:600; margin-bottom:4px;'>
                        ✅ Auto-Sync Active
                    </div>
                    <div style='font-size:0.78rem; color:var(--text-muted);'>
                        Reviews sync automatically every 6 hours from all connected OTA platforms.
                        <b>{total_in_db}</b> reviews currently in your database.
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style='background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.2);
                            border-radius:8px; padding:12px; margin-bottom:12px;'>
                    <div style='font-size:0.85rem; color:#f59e0b; font-weight:600; margin-bottom:4px;'>
                        ⚠️ No OTA Platforms Configured
                    </div>
                    <div style='font-size:0.78rem; color:var(--text-muted);'>
                        Contact your administrator to connect your Booking.com, Agoda, and Google profiles.
                    </div>
                </div>
            """, unsafe_allow_html=True)

        if st.button("🔄 Refresh Reviews", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    with col_manual:
        st.markdown(
            "<p style='font-weight:600; color:var(--text-color); margin-bottom:8px; font-size:0.95rem;'>"
            "✍️ Real-Time Sentiment Analyzer Form</p>",
            unsafe_allow_html=True
        )
        m_review_text = st.text_area(
            "Review Text",
            height=82,
            placeholder="Type/paste a guest review to analyze sentiment in real time...",
            key="m_review_text_val"
        )
        m_rating = st.slider("Guest Rating Stars", 1, 5, 5, key="m_rating_val")

        if m_review_text:
            words = m_review_text.lower().split()
            pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
            neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)
            score = (m_rating - 3) * 2 + (pos_count - neg_count)

            if score > 0:
                live_sent, text_color = "🟢 Positive", "#10b981"
            elif score < 0:
                live_sent, text_color = "🔴 Negative", "#ef4444"
            else:
                live_sent, text_color = "🟡 Neutral", "#f59e0b"

            text_lower = m_review_text.lower()
            live_aspects = [a for a, kws in ASPECTS.items() if any(kw in text_lower for kw in kws)]
            if not live_aspects:
                live_aspects = ["General"]

            # ── FIXED F‑STRING ──
            st.markdown(f"""
                <div class='review-sentiment-box'>
                    <div class='flex-row'>
                        <span style='font-weight:600; color:var(--text-color);'>Live Sentiment:</span>
                        <span style='color:{text_color}; font-weight:700;'>{live_sent}</span>
                    </div>
                    <div style='font-size:0.8rem; color:var(--text-muted); margin-top:6px;'>
                        <span style='font-weight:600;'>Detected Topics:</span>
                        {" ".join([f"<span class='review-aspect-badge'>{a}</span>" for a in live_aspects])}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # Process reviews for display
    processed_reviews = []
    for r in reviews_raw:
        text = r.get("review_text", "")
        rating = r.get("rating", 3)
        words = str(text).lower().split()
        pos_c = sum(1 for w in words if w in POSITIVE_WORDS)
        neg_c = sum(1 for w in words if w in NEGATIVE_WORDS)
        sc = (rating - 3) * 2 + (pos_c - neg_c)
        sentiment = "Positive" if sc > 0 else ("Negative" if sc < 0 else "Neutral")
        text_lower = str(text).lower()
        aspects_found = [a for a, kws in ASPECTS.items() if any(kw in text_lower for kw in kws)]
        if not aspects_found:
            aspects_found = ["General"]
        processed_reviews.append({
            "guest_name": r.get("guest_name", "Guest"),
            "rating": rating,
            "review_text": text,
            "source": r.get("source", "Google"),
            "date": r.get("date", "2026-06-01"),
            "sentiment": sentiment,
            "aspects": aspects_found,
        })

    rdf = pd.DataFrame(processed_reviews)

    if not rdf.empty:
        total_count = len(rdf)
        avg_rating = rdf["rating"].mean()
        pos_count = len(rdf[rdf["sentiment"] == "Positive"])
        pos_pct = round((pos_count / total_count) * 100) if total_count > 0 else 0

        m1, m2, m3 = st.columns(3)
        m1.metric("⭐ Total OTA Reviews", total_count, help="Aggregate reviews from all sources")
        m2.metric("📈 Avg Rating Score", f"{avg_rating:.1f} / 5.0", help="Average guest rating")
        m3.metric("❤️ Positive Sentiment", f"{pos_pct}%", help="Percentage of overall positive feedback")

        neu_count = len(rdf[rdf["sentiment"] == "Neutral"])
        neg_count = len(rdf[rdf["sentiment"] == "Negative"])
        pos_bar = pos_count / total_count * 100 if total_count > 0 else 0
        neu_bar = neu_count / total_count * 100 if total_count > 0 else 0
        neg_bar = neg_count / total_count * 100 if total_count > 0 else 0

        st.markdown(f"""
            <div style='margin: 15px 0 25px 0;'>
                <div style='display:flex; justify-content:space-between; align-items:center;
                            font-size:0.8rem; color:var(--text-muted); margin-bottom:6px;
                            flex-wrap:wrap; gap:4px;'>
                    <span>Guest Sentiment Distribution</span>
                    <span>🟢 Positive ({pos_bar:.0f}%) | 🟡 Neutral ({neu_bar:.0f}%) |
                          🔴 Negative ({neg_bar:.0f}%)</span>
                </div>
                <div style='display:flex; height:12px; border-radius:6px; overflow:hidden;
                            background:var(--border-color);'>
                    <div style='width:{pos_bar}%; background:#10b981;' title='Positive'></div>
                    <div style='width:{neu_bar}%; background:#f59e0b;' title='Neutral'></div>
                    <div style='width:{neg_bar}%; background:#ef4444;' title='Negative'></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        aspect_sentiment = {}
        for aspect in ASPECTS.keys():
            aspect_reviews = rdf[rdf["aspects"].apply(lambda x: aspect in x)]
            total_asp = len(aspect_reviews)
            pct = round(len(aspect_reviews[aspect_reviews["sentiment"] == "Positive"]) / total_asp * 100) \
                  if total_asp > 0 else None
            aspect_sentiment[aspect] = (pct, total_asp)

        st.markdown("<div class='section-title'>Aspect-Based Guest Sentiment</div>", unsafe_allow_html=True)
        res_col1, res_col2 = st.columns(2)

        def render_aspect(col, emoji, label, key, low_advice, high_advice, low_color="#fbbf24"):
            score, count = aspect_sentiment[key]
            with col:
                if score is not None:
                    color = "#10b981" if score >= 70 else low_color
                    advice = low_advice if score < 70 else high_advice
                    st.markdown(f"""
                        <div style='background:rgba(255,255,255,0.02); border:1px solid rgba(148,163,184,0.15);
                                    border-radius:10px; padding:15px; margin-bottom:15px;'>
                            <div style='font-weight:600; display:flex; justify-content:space-between;
                                        align-items:flex-start; margin-bottom:8px; flex-wrap:wrap;
                                        gap:4px; min-width:0;'>
                                <span style='flex-shrink:0;'>{emoji} {label}</span>
                                <span style='color:{color}; font-weight:700; text-align:right;'>
                                    {score}% Positive ({count} reviews)</span>
                            </div>
                            <div style='height:6px; border-radius:3px; background:#334155;
                                        margin-bottom:8px; overflow:hidden;'>
                                <div style='width:{score}%; height:100%; background:{color};'></div>
                            </div>
                            <p style='font-size:0.8rem; opacity:0.8; margin:0;'>
                                <b>Operational Advice:</b> {advice}</p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style='background:rgba(255,255,255,0.02); border:1px solid rgba(148,163,184,0.15);
                                    border-radius:10px; padding:15px; margin-bottom:15px; opacity:0.6;'>
                            <div style='font-weight:600;'>{emoji} {label}</div>
                            <p style='font-size:0.8rem; margin:0;'>No guest reviews available yet.</p>
                        </div>
                    """, unsafe_allow_html=True)

        render_aspect(res_col1, "🍴", "Food & Dining", "Food & Dining",
                      "Insulate room-service food carriers to prevent cold food. Review morning buffet "
                      "temperature logs and conduct a chef taste-audit.",
                      "Guests love the buffet and local Kashmiri Kahwa. Maintain current recipes and food safety standards.")
        render_aspect(res_col1, "🔥", "Heating & Plumbing", "Heating & Plumbing",
                      "Audit fuel limits for backup generators during freezing night hours. Ensure geyser "
                      "timers are set 1 hour before peak guest wake-up times (6:00 AM).",
                      "Heating and hot water systems are operational and satisfying guests. Continue routine checks.",
                      low_color="#ef4444")
        render_aspect(res_col2, "🛎️", "Service & Hospitality", "Service & Hospitality",
                      "Proactively address room service delay complaints. Conduct front-desk logging checks and "
                      "coordination reviews.",
                      "Service hospitality levels are outstanding. Highlight polite and helpful staff members in "
                      "the team meeting.",
                      low_color="#ef4444")
        render_aspect(res_col2, "🛏️", "Room & Cleanliness", "Room & Cleanliness",
                      "Audit blanket cleanliness, sheet changing processes, and verify that dusty corners in "
                      "wood heritage cabins are cleaned.",
                      "Guests appreciate clean rooms, cozy linen, and garden/lake views. Maintain strict room "
                      "inspection schedules.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>All Guest Reviews</div>", unsafe_allow_html=True)

        for _, row in rdf.iterrows():
            stars = "⭐" * int(row["rating"])
            badge_color = {"Positive": "#10b981", "Neutral": "#f59e0b", "Negative": "#ef4444"}.get(
                row["sentiment"], "#64748b")
            aspects_html = " ".join([f"<span class='review-aspect-badge'>{a}</span>" for a in row["aspects"]])
            st.markdown(f"""
                <div class='review-item'>
                    <div class='review-header'>
                        <span style='font-weight:600; color:var(--text-color);'>{row["guest_name"]}</span>
                        <span style='color:#f59e0b; font-size:0.9rem; flex-shrink:0;'>{stars}</span>
                    </div>
                    <p class='review-text'>{row["review_text"]}</p>
                    <div class='review-footer'>
                        <span style='background:{badge_color}; color:white; border-radius:4px;
                                     padding:2px 8px; font-size:0.7rem; font-weight:600;
                                     flex-shrink:0;'>{row["sentiment"]}</span>
                        {aspects_html}
                        <span style='color:var(--text-muted); font-size:0.75rem; margin-left:auto;
                                     white-space:nowrap;'>{row["source"]} · {row["date"]}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No reviews found. Reviews will appear here once guests post on OTA platforms.")

# ══════════════════════════════════════════════════════════
# TAB 4 — TRAVEL RISK & DEMAND
# ══════════════════════════════════════════════════════════
with tab_risk:
    st.markdown("<div class='section-title'>✈️ Srinagar Air Connectivity & Demand Risk Matrix</div>",
                unsafe_allow_html=True)

    live_risk = get_srinagar_live_risk_data()
    risk_score = live_risk["risk_score"]
    weather = live_risk["weather"]

    # ── Live Airport Weather Card ──
    weather_icon = ("❄️" if weather["snow"] > 0 else "🌧️" if weather["rain"] > 0
                    else "🌫️" if weather["visibility_km"] < 2 else "☀️")

    st.markdown(f"""
        <div style='background:var(--secondary-bg-color); border:1px solid var(--border-card);
                    border-radius:12px; padding:16px; margin-bottom:20px; backdrop-filter:blur(10px);
                    display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;'>
            <div>
                <div style='font-size:0.75rem; color:var(--text-muted); text-transform:uppercase;
                            letter-spacing:1px; font-weight:600;'>
                    📍 Srinagar International Airport (SXR)</div>
                <div style='font-size:1.15rem; font-weight:700; color:var(--text-color);
                            display:flex; align-items:center; gap:8px; margin-top:2px;'>
                    <span>{weather_icon} {weather["desc"]}</span>
                    <span style='color:var(--text-muted);'>•</span>
                    <span style='color:var(--primary-color);'>{weather["temp"]}°C</span>
                </div>
            </div>
            <div style='display:flex; gap:20px; margin-top:10px;'>
                <div>
                    <div style='font-size:0.7rem; color:var(--text-muted);'>Visibility</div>
                    <div style='font-size:0.9rem; font-weight:600; color:var(--text-color);'>
                        {weather["visibility_km"]} km</div>
                </div>
                <div>
                    <div style='font-size:0.7rem; color:var(--text-muted);'>Wind Speed</div>
                    <div style='font-size:0.9rem; font-weight:600; color:var(--text-color);'>
                        {weather["wind_speed"]} km/h</div>
                </div>
                <div>
                    <div style='font-size:0.7rem; color:var(--text-muted);'>Active Snow/Rain</div>
                    <div style='font-size:0.9rem; font-weight:600; color:var(--text-color);'>
                        {max(weather["snow"], weather["rain"])} mm</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── Risk gauge ──
    risk_label = ("High Risk" if risk_score >= 70 else "Moderate Risk" if risk_score >= 40 else "Low Risk")
    gauge_color = ("#ef4444" if risk_label == "High Risk" else "#f59e0b" if risk_label == "Moderate Risk"
                   else "#10b981")

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
                {"range": [70,100], "color": "rgba(239,68,68,0.15)"},
            ],
            "threshold": {"line": {"color": "white", "width": 2}, "thickness": 0.75, "value": risk_score},
        },
        number={"font": {"size": 36, "color": gauge_color}, "suffix": "/100"}
    ))
    fig_gauge.update_layout(**CHART, height=280)

    g1, g2 = st.columns([2, 3])
    with g1:
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown(f"""
            <div style='background:var(--secondary-bg-color); border:1px solid var(--border-color);
                        border-radius:10px; padding:14px; margin-top:-10px;'>
                <div style='font-size:1rem; font-weight:700; color:{gauge_color}; margin-bottom:4px;'>
                    ⚠️ {risk_label}</div>
                <div style='font-size:0.8rem; color:var(--text-muted);'>
                    Composite score based on flight cancellations, weather events, political advisories,
                    and seasonal demand patterns.</div>
            </div>
        """, unsafe_allow_html=True)

    with g2:
        st.markdown("<div class='section-title'>Seasonal Disruption Risk Estimate</div>", unsafe_allow_html=True)
        st.caption("📊 Based on Srinagar's known winter fog & monsoon seasonality, blended with today's "
                   "live weather conditions for the current month.")

        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        seasonal_baseline = [70, 65, 40, 18, 12, 8, 10, 14, 20, 28, 50, 72]
        current_month_idx = datetime.now().month - 1
        cancel_prob = seasonal_baseline.copy()
        cancel_prob[current_month_idx] = round((seasonal_baseline[current_month_idx] + risk_score) / 2)
        colors_bar = ["#ef4444" if p >= 60 else "#f59e0b" if p >= 30 else "#10b981" for p in cancel_prob]

        fig_cancel = go.Figure(go.Bar(
            x=months, y=cancel_prob, marker_color=colors_bar,
            text=[f"{p}%" for p in cancel_prob], textposition="outside",
            hovertemplate="<b>%{x}</b>: %{y}% disruption risk<extra></extra>"
        ))
        fig_cancel.update_layout(**CHART)
        fig_cancel.update_yaxes(range=[0, 100], ticksuffix="%", gridcolor="rgba(255,255,255,0.05)",
                                showline=False, zeroline=False)
        st.plotly_chart(fig_cancel, use_container_width=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # ── Risk Factor Matrix ──
    st.markdown("<div class='section-title'>Risk Factor Matrix</div>", unsafe_allow_html=True)
    matrix_factors, matrix_likelihood, matrix_impact, matrix_level, matrix_mitigation = [], [], [], [], []

    for f in live_risk["active_factors"]:
        if f["factor"] == "☀️ Favorable Meteorological Conditions" and len(live_risk["active_factors"]) > 1:
            continue
        matrix_factors.append(f"⚡ Live: {f['factor']}")
        matrix_likelihood.append("Current")
        matrix_impact.append("High" if f["level"] in ["Critical", "High"] else "Medium")
        matrix_level.append("🔴 Critical" if f["level"] == "Critical"
                            else ("🟠 High" if f["level"] == "High" else "🟡 Moderate"))
        matrix_mitigation.append(f["mitigation"])

    matrix_factors.extend([
        "❄️ Winter Fog (Dec–Feb)",
        "🌧️ Monsoon Disruptions (Jul–Sep)",
        "🔌 Airport Power Outage",
        "🌐 Political Advisory / Alerts",
        "📉 Off-Season Demand Drop",
        "🛫 Single-Runway Bottleneck",
    ])
    matrix_likelihood.extend(["High","Medium","Low","Medium","High","Medium"])
    matrix_impact.extend(["High","Medium","High","High","Medium","High"])
    matrix_level.extend(["🔴 Critical","🟡 Moderate","🟠 High","🔴 Critical","🟡 Moderate","🟠 High"])
    matrix_mitigation.extend([
        "Flexible cancellation policy + proactive guest SMS alerts",
        "Monitor IMD forecasts 72 hrs ahead; maintain alternate road-trip packages",
        "Backup generator protocols; pre-check-in communication via WhatsApp",
        "Subscribe to MEA alerts; issue reassurance emails to confirmed bookings",
        "Launch winter packages & early-bird discounts by October",
        "Offer Jammu transfer packages as contingency for diverted flights",
    ])

    risk_df = pd.DataFrame({
        "Risk Factor": matrix_factors,
        "Likelihood/State": matrix_likelihood,
        "Impact": matrix_impact,
        "Risk Level": matrix_level,
        "Mitigation Strategy": matrix_mitigation,
    })
    st.dataframe(risk_df, use_container_width=True, hide_index=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # ── Operational Checklist (Firebase-backed) ──────────
    # ══════════════════════════════════════════════════════
    st.markdown("<div class='section-title'>📋 Pre-Season Operational Checklist</div>", unsafe_allow_html=True)

    CHECKLIST_ITEMS = [
        ("notam_alerts", "Subscribe to airport NOTAM alerts"),
        ("whatsapp_reminders", "Set up 48-hr guest arrival reminders (WhatsApp)"),
        ("ota_cancellation", "Update cancellation policy on all OTAs"),
        ("emergency_supplies", "Stock emergency supplies for weather disruptions"),
        ("alternate_transport", "Prepare alternate transport contacts (taxi/road)"),
        ("staff_delay_protocol", "Train staff on flight delay handling protocol"),
        ("tour_operators", "Set up local partnership with tour operators"),
        ("weather_faq", "Create weather-disruption guest FAQ sheet"),
        ("auto_refund", "Configure auto-refund rules for force majeure"),
        ("generator_fuel", "Verify generator fuel stock for winter months"),
    ]

    if "checklist_state" not in st.session_state:
        st.session_state.checklist_state = load_checklist(hotel_id)
    checklist_state = st.session_state.checklist_state

    total_items = len(CHECKLIST_ITEMS)
    done_count = sum(1 for key, _ in CHECKLIST_ITEMS if checklist_state.get(key, False))
    progress = done_count / total_items
    bar_color = "#10b981" if progress == 1.0 else "#3b82f6"

    st.markdown(f"""
        <div style='margin-bottom:14px;'>
            <div style='display:flex; justify-content:space-between; font-size:0.8rem;
                        color:var(--text-muted); margin-bottom:6px;'>
                <span>Checklist Progress</span>
                <span>{done_count} / {total_items} completed</span>
            </div>
            <div style='height:8px; border-radius:4px; background:var(--border-color); overflow:hidden;'>
                <div style='width:{progress*100:.0f}%; height:100%; background:{bar_color};'></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    chk1, chk2 = st.columns(2)
    half = total_items // 2

    def render_checklist_column(items, col):
        with col:
            for key, label in items:
                current = checklist_state.get(key, False)
                new_val = st.checkbox(label, value=current, key=f"chk_{key}")
                if new_val != current:
                    st.session_state.checklist_state[key] = new_val
                    save_checklist(hotel_id, st.session_state.checklist_state)
                    st.rerun()

    render_checklist_column(CHECKLIST_ITEMS[:half], chk1)
    render_checklist_column(CHECKLIST_ITEMS[half:], chk2)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # ── WhatsApp Guest Outreach Panel ──
    st.markdown("<div class='section-title'>💬 Guest Outreach — Send WhatsApp Messages</div>",
                unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.85rem;color:var(--text-muted);margin-bottom:16px;'>"
                "Select any guest to send them a proactive WhatsApp message. Upcoming bookings are shown first.</p>",
                unsafe_allow_html=True)

    today = date.today()
    arriving_bookings = pd.DataFrame()

    if not df.empty and "Check-in" in df.columns:
        try:
            df["Check-in-dt"] = pd.to_datetime(df["Check-in"], errors="coerce")
            upcoming = df[df["Check-in-dt"].dt.date >= today].copy().sort_values("Check-in-dt")
            arriving_bookings = upcoming if not upcoming.empty else \
                df.dropna(subset=["Check-in-dt"]).copy().sort_values("Check-in-dt", ascending=False)
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

# CSS Unlock
st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)
