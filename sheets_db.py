import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd

# ── Initialize Firebase once ──────────────────────────────
@st.cache_resource
def get_db():
    if not firebase_admin._apps:
        try:
            # Streamlit Cloud — use secrets
            import json
            cred_dict = dict(st.secrets["firebase"])
            cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(cred_dict)
        except:
            # Local — use file
            cred = credentials.Certificate("firebase_credentials.json")

        firebase_admin.initialize_app(cred)

    return firestore.client()


# ── Load all hotels ───────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def load_hotels():
    db = get_db()
    docs = db.collection("hotels").stream()
    data = [doc.to_dict() for doc in docs]

    return (
        pd.DataFrame(data)
        if data
        else pd.DataFrame(
            columns=[
                "hotel_id",
                "name",
                "username",
                "password",
                "email",
                "plan",
            ]
        )
    )


# ── Get hotel by ID ───────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def get_hotel_by_id(hotel_id):
    db = get_db()
    doc = db.collection("hotels").document(hotel_id).get()
    return doc.to_dict() if doc.exists else None


# ── Verify login ──────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def verify_login(username, password):
    db = get_db()

    docs = (
        db.collection("hotels")
        .where("username", "==", username)
        .where("password", "==", password)
        .limit(1)
        .stream()
    )

    for doc in docs:
        return doc.to_dict()

    return None


# ── Load bookings for a hotel ─────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_bookings(hotel_id):
    db = get_db()

    docs = (
        db.collection("bookings")
        .where(filter=firestore.FieldFilter("hotel_id", "==", hotel_id))
        .stream()
    )

    data = [doc.to_dict() for doc in docs]

    if not data:
        return pd.DataFrame(
            columns=[
                "Guest Name",
                "Check-in",
                "Check-out",
                "Nights",
                "Room Type",
                "Guests",
                "Source",
                "Amount (₹)",
                "Status",
                "Notes",
                "Hotel ID",
            ]
        )

    df = pd.DataFrame(data)
    df["Check-in"] = pd.to_datetime(df["Check-in"])
    df["Check-out"] = pd.to_datetime(df["Check-out"])
    df["Month"] = df["Check-in"].dt.strftime("%b")
    df["Month_Num"] = df["Check-in"].dt.month

    return df


# ── Save a new booking ────────────────────────────────────
def save_booking(booking: dict):
    db = get_db()
    db.collection("bookings").add(booking)
    load_bookings.clear()


# ── Add a new hotel ───────────────────────────────────────
def add_hotel(hotel_id, name, username, password, email, plan):
    db = get_db()

    db.collection("hotels").document(hotel_id).set(
        {
            "hotel_id": hotel_id,
            "name": name,
            "username": username,
            "password": password,
            "email": email,
            "plan": plan,
        }
    )

    load_hotels.clear()

# ── Load all bookings (admin only) ───────────────────────
# ── Load all bookings (admin only) ───────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_all_bookings():
    db = get_db()
    docs = db.collection("bookings").stream()
    data = [doc.to_dict() for doc in docs]

    return (
        pd.DataFrame(data)
        if data
        else pd.DataFrame(
            columns=[
                "Guest Name",
                "Check-in",
                "Check-out",
                "Nights",
                "Room Type",
                "Guests",
                "Source",
                "Amount (₹)",
                "Status",
                "Notes",
                "Hotel ID",
            ]
        )
    )


# ── Compatibility Wrapper ────────────────────────────────
def init_session():
    """Ensures Firebase is initialized."""
    return get_db()