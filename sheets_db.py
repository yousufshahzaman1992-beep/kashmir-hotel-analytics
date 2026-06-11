import streamlit as st
import gspread
import pandas as pd
import os

@st.cache_resource(show_spinner=False)
def get_client():
    """Modernized gspread authentication using service account methods."""
    if os.path.exists("credentials.json"):
        # Local development: Use service_account directly
        return gspread.service_account(filename="credentials.json")
    else:
        # Streamlit Cloud: Use service_account_from_dict with Secrets
        # Casting to dict ensures compatibility with internal Google auth libraries
        return gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))

def get_bookings_sheet():
    return get_client().open("Kashmir Hotel Bookings").sheet1

def get_hotels_sheet():
    return get_client().open("Kashmir Hotel Bookings").worksheet("Hotels")

# --- Load hotels for login ---
@st.cache_data(ttl=600, show_spinner=False)
def load_hotels():
    sheet = get_hotels_sheet()
    data  = sheet.get_all_records()
    if data:
        df = pd.DataFrame(data)
        # Normalize column names to lowercase and replace spaces with underscores
        df.columns = [c.lower().replace(" ", "_") for c in df.columns]
        return df
    return pd.DataFrame(
        columns=["hotel_id","name","username","password","email","plan"]
    )

# --- Verify login ---
def verify_login(username, password):
    df    = load_hotels()
    if df.empty:
        return None
    
    # Clean inputs: username is case-insensitive, password is case-sensitive
    u_input = str(username).strip().lower()
    p_input = str(password).strip()
    
    # Compare against cleaned data
    match = df[
        (df["username"].astype(str).str.strip().str.lower() == u_input) & 
        (df["password"].astype(str).str.strip() == p_input)
    ]
    
    if len(match) > 0:
        return match.iloc[0].to_dict()
    return None

# --- Get hotel by ID ---
def get_hotel_by_id(hotel_id):
    df    = load_hotels()
    if df.empty:
        return None
    
    # Ensure robust string comparison (stripping whitespace, case-insensitive ID)
    search_id = str(hotel_id).strip().upper()
    match = df[df["hotel_id"].astype(str).str.strip().str.upper() == search_id]
    
    if len(match) > 0:
        return match.iloc[0].to_dict()
    return None

def prepare_bookings_df(df):
    """Standardizes types and adds time-based features to bookings dataframe."""
    if df.empty:
        return df
    # Handle malformed dates and ensure numeric types
    date_cols = ["Check-in", "Check-out"]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    df["Amount (₹)"] = pd.to_numeric(df["Amount (₹)"], errors='coerce').fillna(0)
    df = df.dropna(subset=["Check-in", "Check-out"])
    
    df["Month"]     = df["Check-in"].dt.strftime("%b")
    df["Month_Num"] = df["Check-in"].dt.month
    return df

# --- Load bookings filtered by hotel_id ---
@st.cache_data(ttl=300, show_spinner=False)
def load_bookings(hotel_id):
    sheet = get_bookings_sheet()
    data  = sheet.get_all_records()
    if not data:
        return pd.DataFrame(columns=[
            "Guest Name","Check-in","Check-out","Nights",
            "Room Type","Guests","Source","Amount (₹)",
            "Status","Notes","Hotel ID"
        ])
    df = pd.DataFrame(data)
    # Robust filtering: ignore case and whitespace in Hotel IDs
    search_id = str(hotel_id).strip().upper()
    df = df[df["Hotel ID"].astype(str).str.strip().str.upper() == search_id]
    
    if len(df) == 0:
        return df

    return prepare_bookings_df(df)

# --- Save booking ---
def save_booking(booking: dict):
    sheet = get_bookings_sheet()
    sheet.append_row([
        booking["Guest Name"],
        booking["Check-in"],
        booking["Check-out"],
        booking["Nights"],
        booking["Room Type"],
        booking["Guests"],
        booking["Source"],
        booking["Amount (₹)"],
        booking["Status"],
        booking["Notes"],
        booking["Hotel ID"]
    ])
    # Clear the specific cache for this hotel so the dashboard updates immediately
    load_bookings.clear(booking["Hotel ID"])

# --- Register a new hotel ---
def register_hotel(name, username, password, email, plan="basic"):
    sheet = get_hotels_sheet()
    data  = sheet.get_all_records()
    for row in data:
        if row["username"] == username:
            return "exists"
    hotel_id = f"HOTEL{str(len(data) + 1).zfill(3)}"
    sheet.append_row([hotel_id, name, username, password, email, plan])
    return "success"

def init_session():
    """Centralized session management for multi-page apps."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "hotel" not in st.session_state:
        st.session_state.hotel = None

    if not st.session_state.logged_in:
        hid = st.query_params.get("hid")
        if hid:
            hotel = get_hotel_by_id(hid)
            if hotel:
                st.session_state.logged_in = True
                st.session_state.hotel = hotel