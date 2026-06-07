import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os

@st.cache_resource(show_spinner=False)
def get_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Check if we are running locally with a file or on the cloud with secrets
    # Check for local file, otherwise use Streamlit Secrets (for GitHub/Cloud)
    if os.path.exists("credentials.json"):
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    else:
        # This uses the Secrets management in Streamlit Cloud
        creds_info = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        
    return gspread.authorize(creds)

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
    
    # Clean inputs and ensure string comparison with stripped whitespace
    u_input = str(username).strip()
    p_input = str(password).strip()
    
    # Compare against cleaned data
    match = df[
        (df["username"].astype(str).str.strip() == u_input) & 
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
    
    # Ensure robust string comparison (stripping whitespace)
    search_id = str(hotel_id).strip()
    match = df[df["hotel_id"].astype(str).str.strip() == search_id]
    
    if len(match) > 0:
        return match.iloc[0].to_dict()
    return None

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
    df = df[df["Hotel ID"] == hotel_id]
    if len(df) == 0:
        return df
    df["Check-in"]  = pd.to_datetime(df["Check-in"])
    df["Check-out"] = pd.to_datetime(df["Check-out"])
    df["Month"]     = df["Check-in"].dt.strftime("%b")
    df["Month_Num"] = df["Check-in"].dt.month
    return df

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