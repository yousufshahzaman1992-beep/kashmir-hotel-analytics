import firebase_admin
from firebase_admin import credentials, firestore
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ── Connect Firebase ──────────────────────────────────────
cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ── Connect Google Sheets ─────────────────────────────────
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
gcreds  = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client  = gspread.authorize(gcreds)
sheet   = client.open("Kashmir Hotel Bookings")

# ── Migrate Hotels ────────────────────────────────────────
print("Migrating hotels...")
hotels = sheet.worksheet("Hotels").get_all_records()
for hotel in hotels:
    db.collection("hotels").document(hotel["hotel_id"]).set(hotel)
    print(f"  ✅ {hotel['name']}")

# ── Migrate Bookings ──────────────────────────────────────
print("Migrating bookings...")
bookings = sheet.sheet1.get_all_records()
for i, booking in enumerate(bookings):
    doc_id = f"booking_{i+1:04d}"
    db.collection("bookings").document(doc_id).set(booking)
    print(f"  ✅ Booking {i+1} — {booking.get('Guest Name','')}")

print("\n🎉 Migration complete!")
print(f"Hotels migrated:   {len(hotels)}")
print(f"Bookings migrated: {len(bookings)}")
