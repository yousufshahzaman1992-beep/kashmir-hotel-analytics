import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd

# ── Initialize Firebase once ──────────────────────────────
@st.cache_resource
def get_db():
    if not firebase_admin._apps:
        try:
            cred_dict = dict(st.secrets["firebase"])
            cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(cred_dict)
        except:
            cred = credentials.Certificate("firebase_credentials.json")
        firebase_admin.initialize_app(cred)
    return firestore.client()

# ── Load all hotels ───────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def load_hotels():
    db   = get_db()
    docs = db.collection("hotels").stream()
    data = [doc.to_dict() for doc in docs]
    return pd.DataFrame(data) if data else pd.DataFrame(
        columns=["hotel_id","name","username","password","email","plan"]
    )

# ── Get hotel by ID ───────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def get_hotel_by_id(hotel_id):
    db  = get_db()
    doc = db.collection("hotels").document(hotel_id).get()
    return doc.to_dict() if doc.exists else None

# ── Verify login ──────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def verify_login(username, password):
    db   = get_db()
    docs = db.collection("hotels").stream()
    for doc in docs:
        data = doc.to_dict()
        if data.get("username") == username and data.get("password") == password:
            return data
    return None

# ── Load bookings for a hotel — no index needed ───────────
@st.cache_data(ttl=300, show_spinner=False)
def load_bookings(hotel_id):
    db   = get_db()
    docs = db.collection("bookings").stream()
    data = [doc.to_dict() for doc in docs]

    # Filter in Python — no Firestore index needed
    data = [d for d in data if d.get("hotel_id") == hotel_id]

    if not data:
        return pd.DataFrame(columns=[
            "Guest Name","Check-in","Check-out","Nights",
            "Room Type","Guests","Source","Amount (₹)",
            "Status","Notes","hotel_id"
        ])

    df = pd.DataFrame(data)
    df["Check-in"]  = pd.to_datetime(df["Check-in"])
    df["Check-out"] = pd.to_datetime(df["Check-out"])
    df["Month"]     = df["Check-in"].dt.strftime("%b")
    df["Month_Num"] = df["Check-in"].dt.month
    return df

# ── Save a new booking ────────────────────────────────────
def save_booking(booking: dict):
    db = get_db()
    # Ensure field name is hotel_id not Hotel ID
    if "Hotel ID" in booking:
        booking["hotel_id"] = booking.pop("Hotel ID")
    db.collection("bookings").add(booking)
    st.cache_data.clear()

# ── Add a new hotel ───────────────────────────────────────
def add_hotel(hotel_id, name, username, password, email, plan):
    db = get_db()
    db.collection("hotels").document(hotel_id).set({
        "hotel_id": hotel_id,
        "name":     name,
        "username": username,
        "password": password,
        "email":    email,
        "plan":     plan
    })
    load_hotels.clear()

# ── Load all bookings (admin only) ────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_all_bookings():
    db   = get_db()
    docs = db.collection("bookings").stream()
    data = [doc.to_dict() for doc in docs]
    return pd.DataFrame(data) if data else pd.DataFrame(columns=[
        "Guest Name","Check-in","Check-out","Nights",
        "Room Type","Guests","Source","Amount (₹)",
        "Status","Notes","hotel_id"
    ])

# ── Compatibility stubs ───────────────────────────────────
def get_hotels_sheet():
    return None

def get_bookings_sheet():
    return None