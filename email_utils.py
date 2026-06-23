import smtplib
import secrets
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sheets_db import get_db
import email.utils

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

# ── Send invitation email ─────────────────────────────────
def send_invite_email(hotel_name, email, token, app_url):
    try:
        # Streamlit automatically handles secrets.toml locally and in the cloud
        if "email" not in st.secrets:
            return False, "Email secrets not configured in st.secrets"

        sender   = st.secrets["email"]["sender"]
        password = st.secrets["email"]["password"]

        setup_link = f"{app_url}?invite={token}"

        # ── Build message with proper headers for Gmail trust ──
        msg = MIMEMultipart("alternative")
        msg["From"]     = f"Kashmir Hotel Analytics <{sender}>"
        msg["To"]       = email
        msg["Subject"]  = f"Account setup for {hotel_name}"
        msg["Reply-To"] = sender
        msg["Date"]     = email.utils.formatdate(localtime=True)
        # A unique Message‑ID helps Gmail avoid treating this as bulk spam
        msg["Message-ID"] = email.utils.make_msgid(domain=sender.split("@")[-1])

        # ── Plain text (always included for trust) ─────────
        plain_text = f"""Assalamu Alaikum,

Your hotel “{hotel_name}” has been registered on Kashmir Hotel Analytics.
To finish setting up your account, please open this link:

{setup_link}

This link is unique and can only be used once.
If you need any help, just reply to this email or WhatsApp us at +91 8491828292.

Thank you,
Kashmir Hotel Analytics Team"""

        # ── Clean, lightweight HTML (no heavy divs/gradients) ──
        html_text = f"""\
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; color: #222; padding: 20px;">
    <p>Assalamu Alaikum,</p>
    <p>Your hotel <strong>{hotel_name}</strong> has been registered on
       Kashmir Hotel Analytics.</p>
    <p>Please finish setting up your account by visiting:</p>
    <p>
        <a href="{setup_link}" style="color: #1a73e8; text-decoration: none;">
            {setup_link}
        </a>
    </p>
    <p style="font-size: 0.9em; color: #555;">
        This link is unique to your hotel and can only be used once.<br>
        Need help? Reply to this email or WhatsApp us at +91 8491828292.
    </p>
    <p style="margin-top: 30px; font-size: 0.85em; color: #777;">
        – Kashmir Hotel Analytics Team
    </p>
</body>
</html>"""

        msg.attach(MIMEText(plain_text, "plain"))
        msg.attach(MIMEText(html_text, "html"))

        # Use port 587 with STARTTLS for better compatibility
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)

        return True, "Email sent successfully"

    except Exception as e:
        return False, f"SMTP Error: {str(e)}"
