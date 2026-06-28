#!/usr/bin/env python3
import os, sys, hashlib, argparse
from datetime import datetime

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.makedirs(os.path.join(project_root, "logs"), exist_ok=True)

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    log_path = os.path.join(project_root, "logs", f"sync_{datetime.now().strftime('%Y-%m-%d')}.log")
    try:
        with open(log_path, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass

def get_db():
    import firebase_admin
    from firebase_admin import credentials, firestore
    if not firebase_admin._apps:
        cred_path = os.path.join(project_root, "firebase_credentials.json")
        firebase_admin.initialize_app(credentials.Certificate(cred_path))
    return firestore.client()

def save_review(db, review):
    hotel_id   = str(review.get("hotel_id", "")).strip().upper()
    source     = str(review.get("source", "unknown")).strip()
    guest_name = str(review.get("guest_name", "Guest")).strip()
    text       = str(review.get("review_text", "")).strip()
    date_val   = str(review.get("date", "")).strip()
    rating     = int(review.get("rating", 3))
    if not text:
        return False
    unique_str = f"{hotel_id}_{source}_{guest_name}_{text[:100]}_{date_val}"
    doc_id = hashlib.md5(unique_str.encode("utf-8")).hexdigest()
    db.collection("reviews").document(doc_id).set({
        "hotel_id": hotel_id, "guest_name": guest_name, "rating": rating,
        "review_text": text, "source": source, "date": date_val,
        "synced_at": datetime.now().isoformat(),
    })
    return True

def get_google_api_key():
    key = os.environ.get("GOOGLE_PLACES_API_KEY", "")
    if key:
        return key
    try:
        import toml
        secrets_path = os.path.join(project_root, ".streamlit", "secrets.toml")
        if os.path.exists(secrets_path):
            s = toml.load(secrets_path)
            return s.get("google_places_api_key") or s.get("google_places", {}).get("api_key", "")
    except Exception:
        pass
    return ""

def fetch_google_reviews(place_id, hotel_name, api_key):
    import requests
    if not api_key:
        return []
    if not place_id:
        try:
            resp = requests.get(
                "https://maps.googleapis.com/maps/api/place/findplacefromtext/json",
                params={"input": hotel_name, "inputtype": "textquery", "fields": "place_id", "key": api_key},
                timeout=10).json()
            candidates = resp.get("candidates", [])
            if not candidates:
                return []
            place_id = candidates[0]["place_id"]
        except Exception as e:
            log(f"  Google lookup error: {e}"); return []
    try:
        resp = requests.get(
            "https://maps.googleapis.com/maps/api/place/details/json",
            params={"place_id": place_id, "fields": "name,rating,reviews", "key": api_key, "language": "en"},
            timeout=10).json()
        out = []
        for r in resp.get("result", {}).get("reviews", [])[:5]:
            ts = r.get("time")
            out.append({
                "guest_name": r.get("author_name", "Guest"),
                "rating": int(r.get("rating", 5)),
                "review_text": r.get("text", ""),
                "source": "Google",
                "date": datetime.fromtimestamp(ts).strftime("%Y-%m-%d") if ts else datetime.now().strftime("%Y-%m-%d"),
            })
        return out
    except Exception as e:
        log(f"  Google details error: {e}"); return []

def sync_hotel(db, hotel_data, scrapers_available, google_api_key):
    hotel_id    = str(hotel_data.get("hotel_id", "")).strip().upper()
    hotel_name  = hotel_data.get("name", hotel_id)
    booking_url = hotel_data.get("booking_review_url", "")
    agoda_url   = hotel_data.get("agoda_review_url", "")
    mmt_url     = hotel_data.get("mmt_review_url", "") or hotel_data.get("mmt_url", "")
    google_place = hotel_data.get("google_place_id", "")
    log(f"Syncing: {hotel_name} ({hotel_id})")
    saved = 0
    g_reviews = fetch_google_reviews(google_place, hotel_name, google_api_key)
    for r in g_reviews:
        r["hotel_id"] = hotel_id
        if save_review(db, r): saved += 1
    log(f"  Google: {len(g_reviews)} fetched")
    if not scrapers_available:
        log("  OTA scrapers unavailable — skipping")
        log(f"  Total saved: {saved}"); return saved
    from scraper import scrape_booking_reviews_with_proxy, scrape_agoda_reviews, scrape_mmt_reviews
    if booking_url:
        try:
            reviews = scrape_booking_reviews_with_proxy(booking_url, headless=True, max_reviews=30)
            for r in reviews:
                r["hotel_id"] = hotel_id
                if save_review(db, r): saved += 1
            log(f"  Booking.com: {len(reviews)} fetched")
        except Exception as e: log(f"  Booking.com error: {e}")
    else: log("  Booking.com: not configured")
    if agoda_url:
        try:
            reviews = scrape_agoda_reviews(agoda_url, headless=True, max_reviews=30)
            for r in reviews:
                r["hotel_id"] = hotel_id
                if save_review(db, r): saved += 1
            log(f"  Agoda: {len(reviews)} fetched")
        except Exception as e: log(f"  Agoda error: {e}")
    else: log("  Agoda: not configured")
    if mmt_url:
        try:
            reviews = scrape_mmt_reviews(mmt_url, headless=True, max_reviews=30)
            for r in reviews:
                r["hotel_id"] = hotel_id
                if save_review(db, r): saved += 1
            log(f"  MakeMyTrip: {len(reviews)} fetched")
        except Exception as e: log(f"  MakeMyTrip error: {e}")
    else: log("  MakeMyTrip: not configured")
    log(f"  Total saved: {saved}"); return saved

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hotel", default=None)
    args = parser.parse_args()
    log("="*60); log("OTA Sync Worker started")
    log("Note: OTA scraping has moved to separate GitHub repo. This worker handles Google Places sync only.")
    try:
        import scraper; scrapers_available = True; log("Scraper: OK")
    except ImportError as e:
        scrapers_available = False; log(f"Scraper: unavailable ({e}) - OTA scraping handled by separate GitHub Actions repo")
    google_api_key = get_google_api_key()
    log(f"Google API key: {'SET' if google_api_key else 'NOT SET'}")
    db = get_db(); log("Firebase: connected")
    if args.hotel:
        doc = db.collection("hotels").document(args.hotel.strip().upper()).get()
        if not doc.exists: log(f"Hotel {args.hotel} not found"); sys.exit(1)
        hotels = [doc.to_dict()]
    else:
        docs = db.collection("hotels").get()
        hotels = [d.to_dict() for d in docs if d.to_dict().get("hotel_id") not in ("ADMIN", None, "")]
    log(f"Hotels to sync: {len(hotels)}")
    total = 0
    for h in hotels:
        try: total += sync_hotel(db, h, scrapers_available, google_api_key)
        except Exception as e: log(f"  ERROR {h.get('hotel_id')}: {e}")
    log("="*60); log(f"Done. Total saved: {total}"); log("="*60)

if __name__ == "__main__":
    main()
