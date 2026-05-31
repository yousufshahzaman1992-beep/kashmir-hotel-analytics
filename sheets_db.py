import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def get_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds  = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    return gspread.authorize(creds)

def get_bookings_sheet():
    return get_client().open("Kashmir Hotel Bookings").sheet1

def get_hotels_sheet():
    return get_client().open("Kashmir Hotel Bookings").worksheet("Hotels")

# --- Load hotels for login ---
def load_hotels():
    sheet = get_hotels_sheet()
    data  = sheet.get_all_records()
    return pd.DataFrame(data) if data else pd.DataFrame(
        columns=["hotel_id","name","username","password","email","plan"]
    )

# --- Verify login ---
def verify_login(username, password):
    df = load_hotels()
    match = df[(df["username"] == username) & (df["password"] == password)]
    if len(match) > 0:
        return match.iloc[0].to_dict()  # returns hotel info dict
    return None

# --- Load bookings filtered by hotel_id ---
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