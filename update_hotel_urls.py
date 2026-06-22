import firebase_admin
from firebase_admin import credentials, firestore

# ── Initialize Firebase ───────────────────────────────────
# This script uses your local credentials file to access Firestore.
try:
    cred = credentials.Certificate("firebase_credentials.json")
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Error connecting to Firebase: {e}")
    exit()

def update_hotel_ota_urls(hotel_id, booking_url, agoda_url, mmt_url):
    """
    Updates a specific hotel document with direct review URLs.
    """
    # Ensure the ID is normalized (uppercase, stripped)
    doc_id = str(hotel_id).strip().upper()
    hotel_ref = db.collection("hotels").document(doc_id)
    
    # Verify the hotel exists before updating
    if not hotel_ref.get().exists:
        print(f"⚠️  Hotel '{doc_id}' not found in Firestore. Skipping...")
        return

    hotel_ref.update({
        "booking_review_url": booking_url,
        "agoda_review_url": agoda_url,
        "mmt_review_url": mmt_url
    })
    print(f"✅ Successfully updated OTA URLs for: {doc_id}")

if __name__ == "__main__":
    # ── CONFIGURE YOUR DATA HERE ──────────────────────────
    # Replace the example URLs with the actual direct review page links
    # for each of your hotels.
    
    hotel_updates = [
        {
            "hotel_id": "HOTEL001",
            "booking_url": "https://www.booking.com/hotel/in/the-lailit-grand-palace-srinagar.html",
            "agoda_url": "https://www.agoda.com/the-lalit-grand-palace-srinagar-hotel/hotel/srinagar-in.html",
            "mmt_url": "https://www.makemytrip.com/hotels/the_lalit_grand_palace_srinagar-details-srinagar.html"
        },
        # Add more dictionaries for other hotels as needed...
    ]

    print("🚀 Starting bulk update of OTA review URLs...")
    for item in hotel_updates:
        update_hotel_ota_urls(item["hotel_id"], item["booking_url"], item["agoda_url"], item["mmt_url"])
    print("\n✨ Update process complete!")