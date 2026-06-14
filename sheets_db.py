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
        except (KeyError, FileNotFoundError, Exception):
            cred = credentials.Certificate("firebase_credentials.json")
        firebase_admin.initialize_app(cred)
    return firestore.client()

# ── Load all hotels ───────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def load_hotels():
    db   = get_db()
    # Using get() is generally faster for smaller management collections
    docs = db.collection("hotels").get()
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
    # Optimization: Query specifically for the username
    docs = list(db.collection("hotels").where("username", "==", username).limit(1).get())
    if docs:
        data = docs[0].to_dict()
        if data.get("password") == password:
            return data
    return None

# ── Load bookings for a hotel — no index needed ───────────
@st.cache_data(ttl=300, show_spinner=False)
def load_bookings(hotel_id):
    db   = get_db()
    # Optimization: Server-side filtering reduces latency and costs
    docs = db.collection("bookings").where("hotel_id", "==", hotel_id).get()
    data = [doc.to_dict() for doc in docs]

    return _process_bookings_dataframe(data)

def _process_bookings_dataframe(data):
    """Helper to standardize booking data processing."""
    cols = [
        "Guest Name", "Check-in", "Check-out", "Nights",
        "Room Type", "Guests", "Source", "Amount (₹)",
        "Status", "Notes", "hotel_id"
    ]
    if not data:
        return pd.DataFrame(columns=cols)

    df = pd.DataFrame(data)
    if "Check-in" in df.columns:
        df["Check-in"]  = pd.to_datetime(df["Check-in"], errors='coerce')
        df["Check-out"] = pd.to_datetime(df["Check-out"], errors='coerce')
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
    # Targeted cache clearing is more efficient than st.cache_data.clear()
    load_bookings.clear(booking.get("hotel_id"))

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
    # Suggestion: Add .limit(500) or filter by date to prevent 
    # performance degradation as data grows.
    docs = db.collection("bookings").order_by("Check-in", direction="DESCENDING").limit(1000).get()
    data = [doc.to_dict() for doc in docs]
    return _process_bookings_dataframe(data)