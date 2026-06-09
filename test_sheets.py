import gspread

# Modernized connection for local testing
client = gspread.service_account(filename="credentials.json")

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