import streamlit as st
import sys, os
from sheets_db import get_db, hash_password, load_hotels
from email_utils import get_invite, mark_invite_used, get_reset, mark_reset_used
from style import apply_style

st.set_page_config(page_title="Setup / Reset Account", page_icon="🔐", layout="centered")
apply_style()

# Hide sidebar
st.markdown("""
<style>
section[data-testid="stSidebar"] { display: none !important; }
.block-container { max-width: 440px !important; margin: 0 auto; padding-top: 4vh; }
</style>
""", unsafe_allow_html=True)

# ── Check invite/reset tokens ─────────────────────────────
invite_token = st.query_params.get("invite") or st.session_state.get("invite_token")
reset_token = st.query_params.get("reset") or st.session_state.get("reset_token")

is_reset_mode = bool(reset_token)
token = reset_token if is_reset_mode else invite_token

if not token:
    st.error("❌ Invalid or missing invite/reset link.")
    st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)
    st.stop()

record = get_reset(token) if is_reset_mode else get_invite(token)

if not record:
    st.error("❌ Reset link not found." if is_reset_mode else "❌ Invite link not found.")
    st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)
    st.stop()

if record.get("used"):
    st.warning("⚠️ This link has already been used. Please login normally.")
    st.page_link("app.py", label="Go to Login →")
    st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)
    st.stop()

hotel_id = record["hotel_id"]

# ── Load hotel info ───────────────────────────────────────
db  = get_db()
doc = db.collection("hotels").document(hotel_id).get()

if not doc.exists:
    st.error("❌ Hotel not found.")
    st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)
    st.stop()

hotel = doc.to_dict()

# ── Title Form ────────────────────────────────────────────
form_title = "Reset Your Password" if is_reset_mode else "Set Up Your Account"
st.markdown(f"""
<div style='text-align:center;margin-bottom:32px'>
    <div style='font-size:48px'>🏔️</div>
    <h1 style='font-size:1.5rem;margin:8px 0'>{form_title}</h1>
</div>
""", unsafe_allow_html=True)

if is_reset_mode:
    st.markdown(f"Resetting password for **{hotel['name']}** (Username: `{hotel.get('username')}`).")
else:
    st.markdown(f"Welcome **{hotel['name']}**! Choose your username and password below.")
st.markdown("<br>", unsafe_allow_html=True)

with st.form("setup_form"):
    if not is_reset_mode:
        username  = st.text_input("Choose Username", placeholder="e.g. dallake")
    
    password  = st.text_input("New Password" if is_reset_mode else "Choose Password", type="password",
                               placeholder="Min 6 characters")
    password2 = st.text_input("Confirm New Password" if is_reset_mode else "Confirm Password", type="password",
                               placeholder="Repeat password")
    
    submit_label = "🔒 Reset My Password" if is_reset_mode else "✅ Create My Account"
    submit    = st.form_submit_button(submit_label, use_container_width=True)

if submit:
    if (not is_reset_mode and not username) or not password:
        st.error("❌ Please fill in all fields.")
    elif len(password) < 6:
        st.error("❌ Password must be at least 6 characters.")
    elif password != password2:
        st.error("❌ Passwords do not match.")
    else:
        try:
            # Update hotel credentials
            update_fields = {"password": hash_password(password)}
            if not is_reset_mode:
                update_fields["username"] = username
                
            db.collection("hotels").document(hotel_id).update(update_fields)
            
            # Mark invite/reset as used
            if is_reset_mode:
                mark_reset_used(token)
            else:
                mark_invite_used(token)
            
            # Clear the hotel cache so the Admin Panel sees the updates
            load_hotels.clear()
            
            # Clean up session state
            if "invite_token" in st.session_state:
                del st.session_state["invite_token"]
            if "reset_token" in st.session_state:
                del st.session_state["reset_token"]
                
            st.success("✅ Password updated successfully!" if is_reset_mode else "✅ Account created successfully!")
            st.info("You can now login with your credentials.")
            st.page_link("app.py", label="Go to Login →")
        except Exception as e:
            st.error(f"❌ Failed to update account: {str(e)}")

# CSS Unlock — triggers the dynamic has-selector to reveal the page
st.markdown("<div class='app-unlocked'></div>", unsafe_allow_html=True)