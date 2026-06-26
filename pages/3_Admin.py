import os
import sys
import streamlit as st
import pandas as pd

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sheets_db import (
    get_hotel_by_id,
    load_hotels,
    load_all_bookings,
    add_hotel,
    get_db,
    update_hotel_ota_links,
)
from style import apply_style, sidebar_logo, ensure_auth, render_custom_navigation

st.set_page_config(
    page_title="Admin Panel · Kashmir Analytics",
    page_icon="⚙️",
    layout="wide",
)

apply_style()
hotel = ensure_auth(allowed_roles=["ADMIN"])

with st.sidebar:
    sidebar_logo()
    render_custom_navigation()
    st.divider()
    st.markdown(
        """
        <div class='logged-in-box'>
            <div class='logged-in-box-label'>Session</div>
            <div class='logged-in-box-name'>Administrator</div>
            <div class='logged-in-box-plan'
                 style='background:rgba(239,68,68,0.15);color:#f87171;
                        border:1px solid rgba(239,68,68,0.3);'>
                ⚡ Full Access
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.hotel = None
        st.query_params.clear()
        st.cache_data.clear()
        st.rerun()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("<p class='page-title'>⚙️ Admin Panel</p>", unsafe_allow_html=True)
st.markdown("<p class='page-sub'>Manage hotels, OTA links, and platform settings.</p>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

tab_hotels, tab_ota, tab_bookings, tab_sync = st.tabs([
    "🏨 Hotels",
    "🔗 OTA Links",
    "📋 All Bookings",
    "🔄 Sync Status",
])

# ══════════════════════════════════════════════════════════
# TAB 1 — HOTELS
# ══════════════════════════════════════════════════════════
with tab_hotels:
    st.markdown("### Registered Hotels")

    hotels_df = load_hotels()
    if hotels_df.empty:
        st.info("No hotels registered yet.")
    else:
        display_cols = [c for c in ["hotel_id", "name", "username", "email", "plan"] if c in hotels_df.columns]
        st.dataframe(hotels_df[display_cols], use_container_width=True, hide_index=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("### ➕ Add New Hotel")

    with st.form("add_hotel_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            new_id       = st.text_input("Hotel ID (e.g. HOTEL002)", placeholder="HOTEL002")
            new_name     = st.text_input("Hotel Name", placeholder="Pine Valley Resort")
            new_username = st.text_input("Login Username", placeholder="pinevalley")
        with c2:
            new_password = st.text_input("Password", type="password")
            new_email    = st.text_input("Email", placeholder="owner@hotel.com")
            new_plan     = st.selectbox("Plan", ["Basic", "Pro", "Enterprise"])

        submitted = st.form_submit_button("✅ Create Hotel", use_container_width=True)
        if submitted:
            if not new_id or not new_name or not new_username or not new_password:
                st.error("Hotel ID, Name, Username, and Password are required.")
            else:
                hotel_id_clean = new_id.strip().upper()
                existing = get_hotel_by_id(hotel_id_clean)
                if existing:
                    st.error(f"Hotel ID '{hotel_id_clean}' already exists.")
                else:
                    add_hotel(
                        hotel_id=hotel_id_clean,
                        name=new_name.strip(),
                        username=new_username.strip(),
                        password=new_password,
                        email=new_email.strip(),
                        plan=new_plan,
                    )
                    st.success(f"✅ Hotel '{hotel_id_clean}' created successfully!")
                    st.rerun()

# ══════════════════════════════════════════════════════════
# TAB 2 — OTA LINKS
# ══════════════════════════════════════════════════════════
with tab_ota:
    st.markdown("### 🔗 Configure OTA Review Links")
    st.caption(
        "Set Booking.com, Agoda, MakeMyTrip review page URLs and Google Place ID for each hotel. "
        "The sync worker uses these to scrape and import guest reviews automatically."
    )

    hotels_df = load_hotels()
    if hotels_df.empty:
        st.info("No hotels available. Add hotels first.")
    else:
        hotel_options = {
            row["hotel_id"]: row.get("name", row["hotel_id"])
            for _, row in hotels_df.iterrows()
            if row.get("hotel_id") not in ("ADMIN", None)
        }
        selected_id = st.selectbox(
            "Select Hotel",
            options=list(hotel_options.keys()),
            format_func=lambda hid: f"{hotel_options[hid]} ({hid})",
        )

        if selected_id:
            hdata = get_hotel_by_id(selected_id) or {}

            with st.form(f"ota_form_{selected_id}"):
                st.markdown(f"**Editing OTA links for: {hotel_options[selected_id]}**")

                booking_url = st.text_input(
                    "Booking.com Review URL",
                    value=hdata.get("booking_review_url", ""),
                    placeholder="https://www.booking.com/hotel/in/my-hotel.en-gb.html",
                )
                agoda_url = st.text_input(
                    "Agoda Review URL",
                    value=hdata.get("agoda_review_url", ""),
                    placeholder="https://www.agoda.com/my-hotel/hotel/kashmir.html",
                )
                mmt_url = st.text_input(
                    "MakeMyTrip Review URL",
                    value=hdata.get("mmt_review_url", "") or hdata.get("mmt_url", ""),
                    placeholder="https://www.makemytrip.com/hotels/hotel-details/?hotelId=202601011",
                )
                google_place_id = st.text_input(
                    "Google Place ID",
                    value=hdata.get("google_place_id", ""),
                    placeholder="ChIJxxxxxxxxxxxxxxx",
                    help="Find it at: https://developers.google.com/maps/documentation/javascript/examples/places-placeid-finder",
                )

                if st.form_submit_button("💾 Save OTA Links", use_container_width=True):
                    ok = update_hotel_ota_links(
                        hotel_id=selected_id,
                        booking_url=booking_url,
                        agoda_url=agoda_url,
                        mmt_url=mmt_url,
                        google_place_id=google_place_id,
                    )
                    if ok:
                        st.success("✅ OTA links saved successfully!")
                    else:
                        st.error("Failed to save. Check Firestore connection.")

            # Show current status
            st.markdown("#### Current Platform Status")
            platforms = {
                "🟢 Booking.com" if hdata.get("booking_review_url") else "⚪ Booking.com": hdata.get("booking_review_url", "Not configured"),
                "🟢 Agoda"       if hdata.get("agoda_review_url")   else "⚪ Agoda":       hdata.get("agoda_review_url", "Not configured"),
                "🟢 MakeMyTrip"  if (hdata.get("mmt_review_url") or hdata.get("mmt_url")) else "⚪ MakeMyTrip": hdata.get("mmt_review_url") or hdata.get("mmt_url") or "Not configured",
                "🟢 Google Places" if hdata.get("google_place_id") else "⚪ Google Places": hdata.get("google_place_id", "Not configured"),
            }
            for label, val in platforms.items():
                st.markdown(
                    f"<div style='font-size:0.85rem; padding:4px 0;'>"
                    f"<b>{label}</b> — <span style='color:var(--text-muted);'>{val}</span></div>",
                    unsafe_allow_html=True,
                )

# ══════════════════════════════════════════════════════════
# TAB 3 — ALL BOOKINGS
# ══════════════════════════════════════════════════════════
with tab_bookings:
    st.markdown("### 📋 All Bookings (Platform-Wide)")

    all_bookings = load_all_bookings()
    if all_bookings.empty:
        st.info("No bookings in the system yet.")
    else:
        st.caption(f"Showing {len(all_bookings)} bookings across all hotels.")

        # Filters
        f1, f2 = st.columns(2)
        with f1:
            hotel_filter = st.multiselect(
                "Filter by Hotel",
                options=sorted(all_bookings["hotel_id"].dropna().unique().tolist()),
            )
        with f2:
            status_filter = st.multiselect(
                "Filter by Status",
                options=sorted(all_bookings["Status"].dropna().unique().tolist()),
            )

        filtered = all_bookings.copy()
        if hotel_filter:
            filtered = filtered[filtered["hotel_id"].isin(hotel_filter)]
        if status_filter:
            filtered = filtered[filtered["Status"].isin(status_filter)]

        display_cols = [
            c for c in [
                "hotel_id", "Guest Name", "Check-in", "Check-out",
                "Nights", "Room Type", "Amount (₹)", "Source", "Status",
            ]
            if c in filtered.columns
        ]
        st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)

        total_rev = int(filtered["Amount (₹)"].sum()) if "Amount (₹)" in filtered else 0
        st.markdown(
            f"<div style='text-align:right; font-size:0.9rem; color:var(--text-muted); margin-top:8px;'>"
            f"Total Revenue (filtered): <b style='color:var(--text-color);'>₹{total_rev:,}</b></div>",
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════════════════
# TAB 4 — SYNC STATUS
# ══════════════════════════════════════════════════════════
with tab_sync:
    st.markdown("### 🔄 OTA Sync Status & Manual Trigger")

    st.info(
        "**Automatic sync** runs every 6 hours via cron (`setup_cron.sh`). "
        "Use the button below to trigger a manual sync for a specific hotel."
    )

    hotels_df = load_hotels()
    hotel_options = {
        row["hotel_id"]: row.get("name", row["hotel_id"])
        for _, row in hotels_df.iterrows()
        if row.get("hotel_id") not in ("ADMIN", None)
    }

    sync_hotel_id = st.selectbox(
        "Hotel to sync",
        options=["ALL"] + list(hotel_options.keys()),
        format_func=lambda hid: "All Hotels" if hid == "ALL" else f"{hotel_options.get(hid, hid)} ({hid})",
    )

    if st.button("🔄 Run Sync Now", use_container_width=True):
        import subprocess
        cmd = [sys.executable, os.path.join(project_root, "sync_worker.py")]
        if sync_hotel_id != "ALL":
            cmd += ["--hotel", sync_hotel_id]
        with st.spinner("Running sync... this may take 1–3 minutes."):
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=project_root,
                )
                output = result.stdout + result.stderr
                if result.returncode == 0:
                    st.success("✅ Sync completed successfully!")
                else:
                    st.error(f"Sync exited with code {result.returncode}")
                with st.expander("📄 Sync Log", expanded=True):
                    st.code(output or "(no output)", language="text")
            except subprocess.TimeoutExpired:
                st.error("⏱ Sync timed out after 5 minutes.")
            except Exception as e:
                st.error(f"Failed to run sync: {e}")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("### 📄 Recent Log Files")

    log_dir = os.path.join(project_root, "logs")
    if os.path.isdir(log_dir):
        log_files = sorted(
            [f for f in os.listdir(log_dir) if f.endswith(".log")],
            reverse=True,
        )[:5]
        if log_files:
            selected_log = st.selectbox("Select log file", log_files)
            log_path = os.path.join(log_dir, selected_log)
            try:
                with open(log_path) as f:
                    content = f.read()
                st.code(content[-5000:] if len(content) > 5000 else content, language="text")
            except Exception as e:
                st.error(f"Could not read log: {e}")
        else:
            st.caption("No log files yet. Logs appear here after the first sync run.")
    else:
        st.caption("Logs directory not found. It will be created on the first sync run.")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Cron Setup")
    st.code(
        "# Make cron script executable and install:\n"
        "chmod +x setup_cron.sh\n"
        "./setup_cron.sh\n\n"
        "# Verify cron is installed:\n"
        "crontab -l",
        language="bash",
    )

st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)