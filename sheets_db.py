import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from google.cloud.firestore_v1.base_query import FieldFilter

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
    docs = list(db.collection("hotels").where(filter=FieldFilter("username", "==", username)).limit(1).get())
    if docs:
        data = docs[0].to_dict()
        if data.get("password") == password:
            return data
    return None

# ── Load bookings for a hotel — no index needed ───────────
@st.cache_data(ttl=300, show_spinner=False)
def load_bookings(hotel_id):
    db   = get_db()
    # We remove order_by from the Firestore query to bypass the requirement for a Composite Index.
    # Sorting is handled in Python/Pandas below.
    docs = db.collection("bookings").where(filter=FieldFilter("hotel_id", "==", hotel_id)).get()
    data = [doc.to_dict() for doc in docs]

    df = _process_bookings_dataframe(data)
    if not df.empty and "Check-in" in df.columns:
        df = df.sort_values("Check-in", ascending=False)
    return df

def _process_bookings_dataframe(data):
    """Helper to standardize booking data processing."""
    cols = [
        "Guest Name", "Phone", "Check-in", "Check-out", "Nights",
        "Room Type", "Guests", "Source", "Amount (₹)",
        "Status", "Notes", "hotel_id"
    ]
    # Create DataFrame and ensure all expected columns exist (handles missing fields in legacy data)
    df = pd.DataFrame(data).reindex(columns=cols)
    
    # Ensure Phone is at least an empty string to prevent 'nan' strings in WhatsApp links
    df["Phone"] = df["Phone"].fillna("")

    if not df.empty:
        # Explicit format parsing is significantly faster than generic parsing
        df["Check-in"]  = pd.to_datetime(df["Check-in"], format='%Y-%m-%d', errors='coerce')
        df["Check-out"] = pd.to_datetime(df["Check-out"], format='%Y-%m-%d', errors='coerce')
        
        # Pre-calculate month info once during the cached load
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
    docs = db.collection("bookings").order_by("`Check-in`", direction="DESCENDING").limit(1000).get()
    data = [doc.to_dict() for doc in docs]
    return _process_bookings_dataframe(data)