import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
import urllib.parse
import sys

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

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

apply_style()

CHART = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#94a3b8", size=11),
    xaxis=dict(showgrid=False, showline=False, zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", showline=False, zeroline=False),
    margin=dict(t=30, b=20, l=10, r=10),
    hoverlabel=dict(bgcolor="#1e293b", font_size=13, font_family="Inter", bordercolor="rgba(255,255,255,0.1)")
)
BLUES = [[0,"#bfdbfe"],[1,"#2563eb"]]
VIBRANT_PURPLE = "#8b5cf6"

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

    # Restore session from URL
    hid = st.query_params.get("hid")
    if hid:
        if hid == "ADMIN":
            st.session_state["logged_in"] = True
            st.session_state["hotel"]     = {"hotel_id": "ADMIN", "name": "Administrator", "plan": "admin"}
            st.rerun()
        else:
            hotel = get_hotel_by_id(hid)
            if hotel:
                st.session_state["logged_in"] = True
                st.session_state["hotel"]     = hotel
                st.rerun()

    show_login()
    st.stop()

# ══════════════════════════════════════════════════════════
# LOGGED IN — dashboard
# ══════════════════════════════════════════════════════════
hotel      = st.session_state.hotel
hotel_id   = hotel["hotel_id"]
hotel_name = hotel["name"]

# Persist session in URL
st.query_params["hid"] = hotel_id

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
            {hotel.get("plan","basic").title()} Plan
        </div>
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
            <button style='width:100%;border-radius:10px;padding:10px;
                           background:#25d366;color:white;border:none;
                           cursor:pointer;font-weight:600;margin-bottom:8px'>
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
    st.stop()

fdf = df[df["Month_Num"].isin(SM[season])]

total_rev    = int(fdf["Amount (₹)"].sum())
total_book   = len(fdf)
total_nights = int(fdf["Nights"].sum())
avg_nights   = round(fdf["Nights"].mean(), 1) if total_book else 0
avg_book     = int(fdf["Amount (₹)"].mean())  if total_book else 0

st.markdown("<div class='section-title'>Performance Overview</div>", unsafe_allow_html=True)

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

# ── Row 1: Revenue + Origins ──────────────────────────────
c1, c2 = st.columns([3,2])
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
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.markdown("<div class='section-title'>Guest Origins</div>", unsafe_allow_html=True)
    src = fdf["Source"].value_counts().reset_index()
    src.columns = ["Source","Guests"]
    fig2 = px.pie(src, names="Source", values="Guests", hole=0.55,
                  color_discrete_sequence=px.colors.qualitative.Vivid)
    fig2.update_traces(textposition="outside", textinfo="label+percent",
                       pull=[0.05 if i == 0 else 0 for i in range(len(src))],
                       textfont=dict(size=11, color="#94a3b8"))
    fig2.update_layout(**CHART, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── Row 2: Room Type + Trend ──────────────────────────────
c3, c4 = st.columns([2,3])
with c3:
    st.markdown("<div class='section-title'>Room Type</div>", unsafe_allow_html=True)
    rooms = fdf["Room Type"].value_counts().reset_index()
    rooms.columns = ["Room Type","Count"]
    fig3 = go.Figure(go.Bar(
        x=rooms["Count"], y=rooms["Room Type"], orientation="h",
        marker=dict(color=rooms["Count"], colorscale="Viridis", line=dict(width=0)),
        text=rooms["Count"],
        textposition="auto",
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
        line=dict(color=VIBRANT_PURPLE, width=3, shape="spline"),
        marker=dict(size=10, color=VIBRANT_PURPLE, line=dict(color="white", width=2)),
        fill="tozeroy", fillcolor="rgba(139, 92, 246, 0.15)",
        hovertemplate="<b>%{x}</b>: %{y}<extra></extra>"
    ))
    fig4.update_layout(**CHART)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── Insights + Recent Bookings ────────────────────────────
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