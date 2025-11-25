import os
import requests

def fetch_google_reviews_for_tanya():
    """
    Fetch Google reviews & rating for Tanya's Baking using:
    1) FindPlaceFromText (resolve place_id)
    2) Place Details API (get reviews + rating)
    Requires GOOGLE_API_KEY in .env and Google Places API enabled.
    """
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        print("[WARN] GOOGLE_API_KEY missing — cannot fetch Google reviews.")
        return []

    # Step 1 — Find place_id
    find_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params_find = {
        "input": "Tanya's Baking Madambakkam Chennai",
        "inputtype": "textquery",
        "fields": "place_id,formatted_address,name",
        "key": GOOGLE_API_KEY
    }

    try:
        r = requests.get(find_url, params=params_find, timeout=8)
        data = r.json()

        if data.get("status") != "OK" or not data.get("candidates"):
            print("[ERROR] FindPlaceFromText failed:", data)
            return []

        place_id = data["candidates"][0]["place_id"]

    except Exception as e:
        print("[ERROR] FindPlaceFromText error:", e)
        return []

    # Step 2 — Fetch rating + reviews
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params_details = {
        "place_id": place_id,
        "fields": "rating,user_ratings_total,reviews",
        "key": GOOGLE_API_KEY
    }

    try:
        r2 = requests.get(details_url, params=params_details, timeout=8)
        data2 = r2.json()

        if data2.get("status") != "OK":
            print("[ERROR] Google API returned:", data2)
            return []

        result = data2.get("result", {})
        rating = result.get("rating")
        total = result.get("user_ratings_total")
        reviews = result.get("reviews", [])[:3]

        formatted = []

        # Add rating summary
        formatted.append({
            "title": f"Google Rating: {rating}★ ({total} reviews)",
            "snippet": f"Rating {rating} from {total} reviews",
            "link": f"https://www.google.com/maps/search/?api=1&query=place_id:{place_id}",
            "verified": True,
            "reason": "Google Maps official data"
        })

        # Add top 3 reviews
        for rv in reviews:
            formatted.append({
                "title": f"Review by {rv.get('author_name', 'User')}",
                "snippet": rv.get("text", ""),
                "rating": rv.get("rating"),
                "link": f"https://www.google.com/maps/search/?api=1&query=place_id:{place_id}",
                "verified": True,
                "reason": "Google Maps verified review"
            })

        return formatted

    except Exception as e:
        print("[ERROR] Failed to fetch Google reviews:", e)
        return []
