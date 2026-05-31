import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define permissions
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Connect using credentials
creds  = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open your sheet
sheet = client.open("Kashmir Hotel Bookings").sheet1

# Read all rows
data = sheet.get_all_records()
print("Connected! Rows found:", len(data))

# Write a test row
sheet.append_row([
    "Test Guest", "2024-01-01", "2024-01-03",
    2, "Deluxe", 2, "Delhi", 5000,
    "Confirmed", "Test booking", "HOTEL001"
])
print("Test row written successfully!")