import firebase_admin
from firebase_admin import credentials, firestore

# 1. Setup Connection (Make sure firebase_credentials.json is in your folder)
try:
    cred = credentials.Certificate("firebase_credentials.json")
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Error: {e}")
    exit()

def add_real_hotel():
    # --- CONFIGURE YOUR HOTEL DATA HERE ---
    hotel_id = "LALIT001" 
    hotel_data = {
        "hotel_id": hotel_id,
        "name": "The Lalit Grand Palace Srinagar",
        "username": "lalit_user",
        "password": "password123", # In production, use a hashed password
        "email": "manager@thelalit.com",
        "plan": "premium",
        
        # Direct links to the review sections for the scraper
        "booking_review_url": "https://www.booking.com/hotel/in/the-lailit-grand-palace-srinagar.html#tab-reviews",
        "agoda_review_url": "https://www.agoda.com/the-lalit-grand-palace-srinagar-hotel/hotel/srinagar-in.html",
        "mmt_url": "https://www.makemytrip.com/hotels/the_lalit_grand_palace_srinagar-details-srinagar.html"
    }

    # Save to the 'hotels' collection in Firestore
    db.collection("hotels").document(hotel_id).set(hotel_data)
    print(f"✅ Real hotel '{hotel_data['name']}' added successfully!")
    print(f"👉 You can now log in using:")
    print(f"   Username: {hotel_data['username']}")
    print(f"   Password: {hotel_data['password']}")

if __name__ == "__main__":
    add_real_hotel()