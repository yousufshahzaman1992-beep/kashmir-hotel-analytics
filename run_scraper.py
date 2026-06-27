#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sheets_db import load_hotels, sync_hotel_reviews


def main():
    hotels_df = load_hotels()

    if hotels_df.empty:
        print("No hotels found in Firestore. Nothing to sync.")
        return

    total_saved = 0

    for _, hotel in hotels_df.iterrows():
        hotel_id = hotel.get("hotel_id")
        name = hotel.get("name", hotel_id)

        if not hotel_id or str(hotel_id).strip().upper() == "ADMIN":
            continue

        any_configured = any([
            hotel.get("booking_review_url"),
            hotel.get("agoda_review_url"),
            hotel.get("mmt_review_url") or hotel.get("mmt_url"),
            hotel.get("google_place_id"),
        ])

        if not any_configured:
            print(f"Skipping {name} ({hotel_id}) — no OTA links configured.")
            continue

        print(f"\n=== Syncing {name} ({hotel_id}) ===")
        try:
            saved, msg, logs = sync_hotel_reviews(hotel_id, name)
            print(msg)
            for line in logs:
                print(" ", line)
            total_saved += saved
        except Exception as e:
            print(f"  ERROR syncing {hotel_id}: {e}")

    print(f"\nDone. Total new reviews saved across all hotels: {total_saved}")


if __name__ == "__main__":
    main()
