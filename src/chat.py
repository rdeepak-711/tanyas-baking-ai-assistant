# src/chat.py
import os, json
from pathlib import Path
from dotenv import load_dotenv
import requests

from retrieve import retrieve
from router import decide_intent
from web_search import web_search

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# load prompt template
TEMPLATE_PATH = Path(__file__).resolve().parent / "prompt_template.txt"
PROMPT_TEMPLATE = TEMPLATE_PATH.read_text(encoding="utf-8")


def build_combined_prompt(local_docs, web_results, question):
    # local_context string
    local_context = "\n\n".join([f"{d['type']} | {d['id']} | {d['source']}\n{d['text']}" for d in local_docs])
    web_context = "\n\n".join([f"{w['title']}\n{w['snippet']}\nSource: {w['link']}" for w in (web_results or [])])

    prompt = PROMPT_TEMPLATE.replace("{{local_context}}", local_context or "No local context available.")
    prompt = prompt.replace("{{web_context}}", web_context or "No relevant web results.")
    prompt = prompt.replace("{{question}}", question)
    return prompt

# reuse call_openai / call_openrouter patterns (from earlier final chat.py)
def call_openai(prompt):
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = { "model": "gpt-4o-mini", "messages": [{"role":"user","content":prompt}], "temperature":0.2 }
    r = requests.post(OPENAI_URL, headers=headers, json=payload, timeout=20)
    if r.status_code != 200:
        return None, r.text
    data = r.json()
    try:
        return data["choices"][0]["message"]["content"], None
    except Exception as e:
        return None, str(data)

def call_openrouter(prompt):
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    payload = {"model":"meta-llama/3.1-8b-instruct", "messages":[{"role":"user","content":prompt}]}
    r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
    try:
        data = r.json()
        return data["choices"][0]["message"]["content"], None
    except Exception as e:
        return None, r.text

def format_sources(local_docs, web_results):
    local_set = sorted({d['source'] for d in local_docs})
    # For web results split verified vs unverified
    verified_web = [w for w in (web_results or []) if w.get("verified")]
    unverified_web = [w for w in (web_results or []) if not w.get("verified")]
    s_local = "\n".join(local_set) if local_set else "None"
    s_verified = "\n".join([w["link"] for w in verified_web]) if verified_web else "None"
    s_unverified = "\n".join([f"{w['link']} ({w.get('reason')})" for w in unverified_web]) if unverified_web else "None"
    return s_local, s_verified, s_unverified

def fetch_google_reviews_for_tanya():
    """
    Resolve place_id with FindPlaceFromText, then get top 3 reviews & rating.
    Requires GOOGLE_API_KEY set in .env and Places API enabled+billing.
    """
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        print("[WARN] GOOGLE_API_KEY missing — cannot fetch Google reviews.")
        return []

    # Try to resolve the place by text (use place name + city)
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
            print("[ERROR] FindPlaceFromText failed:", data.get("status"), data.get("error_message"))
            return []

        place_id = data["candidates"][0]["place_id"]
    except Exception as e:
        print("[ERROR] FindPlaceFromText error:", e)
        return []

    # Now fetch details including reviews + rating
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
            print("[ERROR] Google API returned:", data2.get("status"), data2.get("error_message"))
            return []

        result = data2.get("result", {})
        rating = result.get("rating")
        total = result.get("user_ratings_total")
        reviews = result.get("reviews", [])[:3]  # top 3

        formatted = []
        # add rating summary as a first "web result" (optional)
        if rating is not None:
            formatted.append({
                "title": f"Google Rating: {rating}★ ({total} reviews)" if total else f"Google Rating: {rating}★",
                "snippet": f"Google rating: {rating} from {total} reviews" if total else f"Google rating: {rating}",
                "link": f"https://www.google.com/maps/search/?api=1&query=place_id:{place_id}",
                "verified": True,
                "reason": "Google Maps place details"
            })

        for rv in reviews:
            formatted.append({
                "title": f"Google Review by {rv.get('author_name','User')}",
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

def chat(question):
    intent = decide_intent(question)
    print(f"Router intent: {intent}")

    # 1. Local docs (RAG)
    local_docs = retrieve(question)

    # 2. Choose web scope
    if intent == "tanya":
        web_scope = "tanya"
    elif intent == "hybrid":
        web_scope = "tanya"
    else:
        web_scope = "baking"

    # 3. First fetch general/filtered web results
    web_results = web_search(question, scope=web_scope)

    # 4. If Tanya intent → add Google Maps top 3 reviews
    if intent == "tanya":
        google_reviews = fetch_google_reviews_for_tanya()
        if google_reviews:
            web_results.extend(google_reviews)

    # 5. Hybrid fallback: if no verified Tanya results → use baking results
    if intent == "hybrid":
        verified = [w for w in web_results if w.get("verified")]
        if not verified:
            web_results = web_search(question, scope="baking")

    # 6. Tanya safety filtering
    if intent == "tanya":
        verified_only = [w for w in web_results if w.get("verified")]
        if not verified_only:
            print("No verified Tanya web results found — will rely on local data only.")
            web_results = []
        else:
            web_results = verified_only

    print(f"Local docs: {len(local_docs)}  |  Web results: {len(web_results)}")

    # 7. Build prompt
    prompt = build_combined_prompt(local_docs, web_results, question)

    # 8. Call model (OpenAI primary → OpenRouter fallback)
    answer, err = call_openai(prompt)
    if not answer:
        answer, err = call_openrouter(prompt)
        if not answer:
            print("All models failed. Error:", err)
            return

    # 9. Format sources
    s_local, s_verified, s_unverified = format_sources(local_docs, web_results)

    # 10. Output
    print("\n--- ANSWER ---\n")
    print(answer)
    print("\n--- SOURCES (LOCAL) ---\n")
    print(s_local)
    print("\n--- SOURCES (WEB - VERIFIED) ---\n")
    print(s_verified)
    print("\n--- SOURCES (WEB - UNVERIFIED / DROPPED) ---\n")
    print(s_unverified)

if __name__ == "__main__":
    q = input("Ask Tanya’s Baking assistant: ")
    chat(q)
