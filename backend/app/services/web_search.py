# src/web_search.py
import os
import requests
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

SERPER_KEY = os.getenv("SERPER_API_KEY")
SERPER_URL = "https://google.serper.dev/search"

# Tanya whitelist: domains and (optionally) specific paths you trust
# Add more exact domains/paths as you trust them.
TANYA_WHITELIST = [
    "tanyasbaking.com",
    "www.tanyasbaking.com",
    "instagram.com/tanyas_baking",
    "www.instagram.com/tanyas_baking",
    "justdial.com",
    "google.com/maps",
    "maps.google.com",
    "google.com/maps/place/Tanya's+Baking+(Homemade+Cakes+and+Class)",
    "www.google.com/maps/place/Tanya's+Baking+(Homemade+Cakes+and+Class)",
]


def domain_from_url(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def is_whitelisted(url: str) -> bool:
    dom = domain_from_url(url)
    # Check domain contains any whitelisted domain fragment
    for allowed in TANYA_WHITELIST:
        if allowed in dom or allowed in url:
            return True
    return False


def verify_tanya_page(url: str, keywords: list = None) -> bool:
    """
    Fetch the page and check for explicit mentions of Tanya's Baking or address tokens.
    This is a light verification (not full-proof), but dramatically reduces false matches.
    """
    keywords = keywords or ["tanya", "tanya's baking", "tanyas baking", "madambakkam", "padmavathy", "9677276248"]
    try:
        r = requests.get(url, timeout=6, headers={"User-Agent": "tanyas-bot/1.0"})
        if r.status_code != 200:
            return False
        text = r.text.lower()
        # require at least one keyword match
        return any(k.lower() in text for k in keywords)
    except Exception:
        return False


def _serper_search(query: str, num: int = 5):
    if not SERPER_KEY:
        return []
    payload = {"q": query, "num": num}
    headers = {"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"}
    try:
        r = requests.post(SERPER_URL, headers=headers, json=payload, timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("[web_search] Serper error:", e)
        return {}


def web_search(query: str, scope: str = "baking", top_n: int = 3):
    """
    scope: "baking" (general) or "tanya" (Tanya-specific)
    returns list of {title, snippet, link, verified(bool)}
    """
    raw = _serper_search(query, num=top_n + 2)
    organic = raw.get("organic", []) or []

    results = []
    for item in organic[:top_n]:
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        link = item.get("link", "")

        if scope == "tanya":
            # Only accept if domain is whitelisted AND page verification passes
            if not is_whitelisted(link):
                # mark not whitelisted (do not append as verified)
                results.append({"title": title, "snippet": snippet, "link": link, "verified": False, "reason": "not_whitelisted"})
                continue
            # if whitelisted, do a lightweight verification
            verified = verify_tanya_page(link)
            results.append({"title": title, "snippet": snippet, "link": link, "verified": verified, "reason": None if verified else "failed_verification"})
        else:
            # Baking scope — do not verify against Tanya whitelist.
            results.append({"title": title, "snippet": snippet, "link": link, "verified": True, "reason": None})

    return results

def fetch_google_reviews_for_tanya():
    """
    Fetches the top 3 reviews from Tanya's Google Maps listing using Serper.
    Only pulls reviews from the exact whitelisted Google Maps place.
    """

    payload = {
        "q": "Tanya's Baking Chennai Google Reviews",
        "type": "local",
        "num": 1
    }

    headers = {
        "X-API-KEY": SERPER_KEY,
        "Content-Type": "application/json"
    }

    try:
        r = requests.post(SERPER_URL, json=payload, headers=headers)
        data = r.json()

        # Local results contain google reviews in "local" index
        local_results = data.get("local", [])
        if not local_results:
            return []

        place = local_results[0]

        url = place.get("link", "")
        if TANYA_GOOGLE_MAPS not in url:
            return []  # Do not trust other Google listings

        # Reviews available?
        reviews = place.get("reviews", [])
        top3 = reviews[:3]

        formatted = []
        for r in top3:
            formatted.append({
                "author": r.get("author", "Anonymous"),
                "rating": r.get("rating", ""),
                "text": r.get("snippet", ""),
                "link": url,
                "verified": True,
                "type": "google_review"
            })

        return formatted

    except Exception as e:
        print("[DEBUG] Tanya Google review fetch failed:", e)
        return []
