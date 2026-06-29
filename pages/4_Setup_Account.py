import streamlit as st
import sys, os
from sheets_db import get_db, hash_password, load_hotels
from email_utils import get_invite, mark_invite_used
from style import apply_style

st.set_page_config(page_title="Setup Account", page_icon="🔐", layout="centered")
apply_style()

# Hide sidebar
st.markdown("""
<style>
section[data-testid="stSidebar"] { display: none !important; }
.block-container { max-width: 440px !important; margin: 0 auto; padding-top: 4vh; }
</style>
""", unsafe_allow_html=True)

# ── Check invite token ────────────────────────────────────
token = st.query_params.get("invite") or st.session_state.get("invite_token")

if not token:
    st.error("❌ Invalid or missing invite link.")
    st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)
    st.stop()

invite = get_invite(token)

if not invite:
    st.error("❌ Invite link not found.")
    st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)
    st.stop()

if invite.get("used"):
    st.warning("⚠️ This invite link has already been used. Please login normally.")
    st.page_link("app.py", label="Go to Login →")
    st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)
    st.stop()

hotel_id = invite["hotel_id"]

# ── Load hotel info ───────────────────────────────────────
db  = get_db()
doc = db.collection("hotels").document(hotel_id).get()

if not doc.exists:
    st.error("❌ Hotel not found.")
    st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)
    st.stop()

hotel = doc.to_dict()

# ── Setup Form ────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;margin-bottom:32px'>
    <div style='font-size:48px'>🏔️</div>
    <h1 style='font-size:1.5rem;margin:8px 0'>Set Up Your Account</h1>
</div>
""", unsafe_allow_html=True)

st.markdown(f"Welcome **{hotel['name']}**! Choose your username and password below.")
st.markdown("<br>", unsafe_allow_html=True)

with st.form("setup_form"):
    username  = st.text_input("Choose Username", placeholder="e.g. dallake")
    password  = st.text_input("Choose Password", type="password",
                               placeholder="Min 6 characters")
    password2 = st.text_input("Confirm Password", type="password",
                               placeholder="Repeat password")
    submit    = st.form_submit_button("✅ Create My Account", width='stretch')

if submit:
    if not username or not password:
        st.error("❌ Please fill in all fields.")
    elif len(password) < 6:
        st.error("❌ Password must be at least 6 characters.")
    elif password != password2:
        st.error("❌ Passwords do not match.")
    else:
        try:
            # Update hotel with chosen credentials
            db.collection("hotels").document(hotel_id).update({
                "username": username,
                "password": hash_password(password)
            })
            # Mark invite as used
            mark_invite_used(token)
            
            # Clear the hotel cache so the Admin Panel sees the new username
            load_hotels.clear()
            
            # Clean up session state
            if "invite_token" in st.session_state:
                del st.session_state["invite_token"]
                
            st.success("✅ Account created successfully!")
            st.info("You can now login with your new credentials.")
            st.page_link("app.py", label="Go to Login →")
        except Exception as e:
            st.error(f"❌ Failed to update account: {str(e)}")

# CSS Unlock — triggers the dynamic has-selector to reveal the page
st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)