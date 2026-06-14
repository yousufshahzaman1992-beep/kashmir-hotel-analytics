import smtplib
import secrets
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sheets_db import get_db

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
        try:
            sender   = st.secrets["email"]["sender"]
            password = st.secrets["email"]["password"]
        except:
            import toml, os
            s        = toml.load(os.path.expanduser("~/.streamlit/secrets.toml"))
            sender   = s["email"]["sender"]
            password = s["email"]["password"]

        setup_link = f"{app_url}?invite={token}"

        msg            = MIMEMultipart("alternative")
        msg["From"]    = f"Kashmir Analytics <{sender}>"
        msg["To"]      = email
        msg["Subject"] = f"You're invited to Kashmir Hotel Analytics — {hotel_name}"

        html = f"""
        <html>
        <body style='font-family:Inter,sans-serif;background:#f1f5f9;padding:40px'>
            <div style='max-width:500px;margin:0 auto;background:white;
                        border-radius:16px;padding:40px;box-shadow:0 4px 24px rgba(0,0,0,0.08)'>
                <div style='text-align:center;margin-bottom:32px'>
                    <div style='font-size:48px'>🏔️</div>
                    <h1 style='color:#0f172a;font-size:1.5rem;margin:8px 0'>
                        Kashmir Hotel Analytics
                    </h1>
                    <p style='color:#64748b;font-size:0.9rem'>Hotel Intelligence Platform</p>
                </div>
                <p style='color:#334155;font-size:0.95rem;line-height:1.6'>
                    Assalamu Alaikum,<br><br>
                    Your hotel <strong>{hotel_name}</strong> has been registered on
                    Kashmir Hotel Analytics. Click the button below to set up
                    your account password.
                </p>
                <div style='text-align:center;margin:32px 0'>
                    <a href='{setup_link}'
                       style='background:linear-gradient(135deg,#1d4ed8,#3b82f6);
                              color:white;padding:14px 32px;border-radius:10px;
                              text-decoration:none;font-weight:600;font-size:0.95rem;
                              display:inline-block'>
                        Set Up My Account →
                    </a>
                </div>
                <p style='color:#94a3b8;font-size:0.78rem;text-align:center;
                          border-top:1px solid #f1f5f9;padding-top:20px;margin-top:32px'>
                    This link is unique to your hotel and expires after use.<br>
                    Need help? WhatsApp us at +91 8491828292
                </p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)

        return True, "Email sent successfully"

    except Exception as e:
        return False, str(e)