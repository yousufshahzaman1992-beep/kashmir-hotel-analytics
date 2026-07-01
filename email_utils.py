import smtplib
import secrets
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sheets_db import get_db
from email.utils import formatdate, make_msgid

# ── Generate unique invite token ──────────────────────────
def generate_invite_token():
    return secrets.token_urlsafe(32)

# ── Save invite token to Firebase ─────────────────────────
def save_invite_token(token, hotel_id, email):
    db = get_db()
    db.collection("invites").document(token).set({
        "token":    token,
        "hotel_id": hotel_id,
        "email":    email,
        "used":     False
    })

# ── Get invite by token ───────────────────────────────────
def get_invite(token):
    db  = get_db()
    doc = db.collection("invites").document(token).get()
    return doc.to_dict() if doc.exists else None

# ── Mark invite as used ───────────────────────────────────
def mark_invite_used(token):
    db = get_db()
    db.collection("invites").document(token).update({"used": True})

# ── Get reset by token ────────────────────────────────────
def get_reset(token):
    db  = get_db()
    doc = db.collection("resets").document(token).get()
    return doc.to_dict() if doc.exists else None

# ── Mark reset as used ────────────────────────────────────
def mark_reset_used(token):
    db = get_db()
    db.collection("resets").document(token).update({"used": True})

# ── Save reset token to Firebase ─────────────────────────
def save_reset_token(token, hotel_id, email):
    db = get_db()
    db.collection("resets").document(token).set({
        "token":    token,
        "hotel_id": hotel_id,
        "email":    email,
        "used":     False
    })

# ── Send password reset email ────────────────────────────
def send_reset_email(hotel_name, email, token, app_url):
    try:
        if "email" not in st.secrets:
            return False, "Email secrets not configured in st.secrets"

        sender   = st.secrets["email"]["sender"]
        password = st.secrets["email"]["password"]

        reset_link = f"{app_url}?reset={token}"

        # ── Plain‑text only message ───────────────────────
        text = f"""Assalamu Alaikum,

We received a request to reset your password for Kashmir Hotel Analytics (Hotel: “{hotel_name}”).

To reset your password, please copy this link and open it in your browser:
{reset_link}

This link works only once and is unique to your request.

If you did not request this, you can safely ignore this email.

If you need any help, reply to this email or WhatsApp +91 8491828292.

Thank you,
Kashmir Hotel Analytics Team"""

        msg = MIMEText(text, "plain", "utf-8")
        msg["From"]         = f"Kashmir Hotel Analytics <{sender}>"
        msg["To"]           = email
        msg["Subject"]      = f"Password Reset Request for {hotel_name}"
        msg["Date"]         = formatdate(localtime=True)
        msg["Message-ID"]   = make_msgid(domain=sender.split("@")[-1])
        msg["Reply-To"]     = sender
        msg["X-Mailer"]     = "Mozilla Thunderbird 102.15.1"
        msg["X-Priority"]   = "3"
        msg["List-Unsubscribe"] = f"<mailto:{sender}?subject=unsubscribe>"

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)

        return True, "Reset email sent successfully"

    except Exception as e:
        return False, f"SMTP Error: {str(e)}"


# ── Send invitation email (ultra‑safe plain‑text only) ────
def send_invite_email(hotel_name, email, token, app_url):
    try:
        if "email" not in st.secrets:
            return False, "Email secrets not configured in st.secrets"

        sender   = st.secrets["email"]["sender"]
        password = st.secrets["email"]["password"]

        setup_link = f"{app_url}?invite={token}"

        # ── Plain‑text only message (most trustworthy) ─────
        text = f"""Assalamu Alaikum,

Your hotel “{hotel_name}” has been registered on Kashmir Hotel Analytics.

To set up your account, please copy this link and open it in your browser:
{setup_link}

This link works only once and is unique to your hotel.

If you need any help, reply to this email or WhatsApp +91 8491828292.

Thank you,
Kashmir Hotel Analytics Team"""

        # Build message with many real‑client headers
        msg = MIMEText(text, "plain", "utf-8")
        msg["From"]         = f"Kashmir Hotel Analytics <{sender}>"
        msg["To"]           = email
        msg["Subject"]      = f"Account setup for {hotel_name}"
        msg["Date"]         = formatdate(localtime=True)
        msg["Message-ID"]   = make_msgid(domain=sender.split("@")[-1])
        msg["Reply-To"]     = sender
        msg["X-Mailer"]     = "Mozilla Thunderbird 102.15.1"   # looks like a normal client
        msg["X-Priority"]   = "3"                              # normal priority
        msg["List-Unsubscribe"] = f"<mailto:{sender}?subject=unsubscribe>"  # good practice

        # ── Send via Gmail with STARTTLS ───────────────────
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)

        return True, "Email sent successfully"

    except Exception as e:
        return False, f"SMTP Error: {str(e)}"