import firebase_admin
from firebase_admin import credentials, firestore

# Connect using your key file
cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)

# Get database
db = firestore.client()

# Write a test document
db.collection("hotels").document("TEST001").set({
    "hotel_id": "TEST001",
    "name": "Test Hotel",
    "username": "testhotel",
    "password": "test123",
    "email": "test@hotel.com",
    "plan": "basic"
})

print("✅ Connected to Firebase successfully!")
print("✅ Test hotel written to Firestore!")