import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

from sheets_db import load_bookings, get_hotel_by_id
from login import show_login
from style import apply_style, sidebar_logo

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

    # ── Restore session from query params AFTER layout is hidden ──
    hid = st.query_params.get("hid")
    if hid:
        if hid == "ADMIN":
            st.session_state["logged_in"] = True
            st.session_state["hotel"]     = {"hotel_id": "ADMIN", "name": "Administrator"}
            st.rerun()
        else:
            hotel = get_hotel_by_id(hid) # UI stays hidden while this runs
            if hotel:
                st.session_state["logged_in"] = True
                st.session_state["hotel"]     = hotel
                st.rerun() # Force instant update to show sidebar properly

apply_style()

CHART = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#64748b", size=11),
    xaxis=dict(gridcolor="rgba(148,163,184,0.15)", linecolor="rgba(148,163,184,0.2)"),
    yaxis=dict(gridcolor="rgba(148,163,184,0.15)", linecolor="rgba(148,163,184,0.2)"),
    margin=dict(t=20, b=20, l=10, r=10)
)
BLUES = [[0,"#bfdbfe"],[1,"#2563eb"]]
BLUE  = "#3b82f6"

# ══════════════════════════════════════════════════════════
# LOGIN PAGE
# ══════════════════════════════════════════════════════════
if not st.session_state.get("logged_in"):
    show_login()
    st.stop()

# ══════════════════════════════════════════════════════════
# DASHBOARD (only reaches here if logged in)
# ══════════════════════════════════════════════════════════
hotel      = st.session_state.hotel
hotel_id   = hotel["hotel_id"]
hotel_name = hotel["name"]

# Persist session in URL
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
                    color:var(--text-color)'>{hotel_name}</div>
        <div style='font-size:0.75rem;color:#3b82f6'>
            {hotel.get("plan", "Full Access").title()}{" Plan" if "plan" in hotel else ""}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("↻ Refresh Data", use_container_width=True):
        st.cache_data.clear() # Already present, good.
        st.rerun()

    season = st.selectbox("Season",
        ["Full Year","Winter (Jan–Mar)","Spring (Apr–Jun)",
         "Summer (Jul–Sep)","Autumn (Oct–Dec)"])

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
        st.session_state.logged_in = False # Already present, good.
        st.session_state.hotel     = None # Already present, good.
        st.query_params.clear() # Already present, good.
        st.cache_data.clear() # Already present, good.
        st.rerun()

# ── Load data for THIS hotel only ────────────────────────
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
    st.stop()

fdf = df[df["Month_Num"].isin(SM[season])]

total_rev    = int(fdf["Amount (₹)"].sum())
total_book   = len(fdf)
total_nights = int(fdf["Nights"].sum())
avg_nights   = round(fdf["Nights"].mean(), 1) if total_book else 0
avg_book     = int(fdf["Amount (₹)"].mean())  if total_book else 0

st.markdown("<div class='section-title'>Performance Overview</div>", unsafe_allow_html=True)

# Using a container for metrics helps with layout stability
with st.container():
    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric("📋 Bookings",    str(total_book))
    k2.metric("💰 Revenue",     f"₹{total_rev:,}")
    k3.metric("🌙 Nights Sold", str(total_nights))
    k4.metric("📅 Avg Stay",    f"{avg_nights} nights")
    k5.metric("💵 Avg Booking", f"₹{avg_book:,}")

st.markdown("<br>", unsafe_allow_html=True)

if total_book == 0:
    st.info("No bookings for this season.")
    st.stop()

c1, c2 = st.columns([3,2])
with c1:
    st.markdown("<div class='section-title'>Monthly Revenue</div>", unsafe_allow_html=True)
    rev = (fdf.groupby(["Month_Num","Month"])["Amount (₹)"]
              .sum().reset_index().sort_values("Month_Num"))
    fig1 = go.Figure(go.Bar(
        x=rev["Month"], y=rev["Amount (₹)"],
        marker=dict(color=rev["Amount (₹)"], colorscale=BLUES, line=dict(width=0)),
        hovertemplate="<b>%{x}</b><br>₹%{y:,}<extra></extra>"
    ))
    fig1.update_layout(**CHART)
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.markdown("<div class='section-title'>Guest Origins</div>", unsafe_allow_html=True)
    src = fdf["Source"].value_counts().reset_index()
    src.columns = ["Source","Guests"]
    fig2 = px.pie(src, names="Source", values="Guests", hole=0.55,
                  color_discrete_sequence=["#2563eb","#3b82f6","#60a5fa",
                                            "#93c5fd","#bfdbfe","#1e40af","#dbeafe"])
    fig2.update_traces(textposition="outside", textinfo="percent+label",
                       textfont=dict(size=10))
    fig2.update_layout(**CHART, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

c3, c4 = st.columns([2,3])
with c3:
    st.markdown("<div class='section-title'>Room Type</div>", unsafe_allow_html=True)
    rooms = fdf["Room Type"].value_counts().reset_index()
    rooms.columns = ["Room Type","Count"]
    fig3 = go.Figure(go.Bar(
        x=rooms["Count"], y=rooms["Room Type"], orientation="h",
        marker=dict(color=rooms["Count"], colorscale=BLUES, line=dict(width=0)),
        hovertemplate="<b>%{y}</b>: %{x}<extra></extra>"
    ))
    fig3.update_layout(**CHART)
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.markdown("<div class='section-title'>Bookings Over Time</div>", unsafe_allow_html=True)
    trend = (fdf.groupby(["Month_Num","Month"])
                .size().reset_index(name="Bookings").sort_values("Month_Num"))
    fig4 = go.Figure(go.Scatter(
        x=trend["Month"], y=trend["Bookings"],
        mode="lines+markers",
        line=dict(color=BLUE, width=2.5),
        marker=dict(size=8, color=BLUE, line=dict(color="white", width=2)),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.07)",
        hovertemplate="<b>%{x}</b>: %{y}<extra></extra>"
    ))
    fig4.update_layout(**CHART)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

ci1, ci2 = st.columns([1,2])
with ci1:
    st.markdown("<div class='section-title'>Quick Insights</div>", unsafe_allow_html=True)
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
    recent = fdf.sort_values("Check-in", ascending=False).head(8)
    st.dataframe(recent, use_container_width=True, hide_index=True)