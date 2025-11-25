import os
import requests
from pathlib import Path
from dotenv import load_dotenv

from app.services.retrieve import retrieve
from app.services.router import decide_intent
from app.services.web_search import web_search
from app.services.google_reviews import fetch_google_reviews_for_tanya

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

TEMPLATE_PATH = Path(__file__).resolve().parent / "prompt_template.txt"
PROMPT_TEMPLATE = TEMPLATE_PATH.read_text(encoding="utf-8")


# ----------------------------------------------------------------
# Build Prompt
# ----------------------------------------------------------------
def build_combined_prompt(local_docs, web_results, question):
    local_context = "\n\n".join(
        [f"{d['type']} | {d['id']} | {d['source']}\n{d['text']}" for d in local_docs]
    )

    web_context = "\n\n".join(
        [f"{w['title']}\n{w['snippet']}\nSource: {w['link']}" for w in (web_results or [])]
    )

    prompt = PROMPT_TEMPLATE.replace(
        "{{local_context}}", local_context or "No local context found."
    ).replace(
        "{{web_context}}", web_context or "No web results."
    ).replace(
        "{{question}}", question
    )

    return prompt


# ----------------------------------------------------------------
# Model calls
# ----------------------------------------------------------------
def call_openai(prompt: str):
    if not OPENAI_API_KEY:
        return None, "Missing OPENAI_API_KEY"

    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }

    r = requests.post(OPENAI_URL, headers=headers, json=payload, timeout=20)
    try:
        data = r.json()
        return data["choices"][0]["message"]["content"], None
    except Exception:
        return None, r.text


def call_openrouter(prompt: str):
    if not OPENROUTER_API_KEY:
        return None, "Missing OPENROUTER_API_KEY"

    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "meta-llama/3.1-8b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
    }

    r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=20)
    try:
        data = r.json()
        return data["choices"][0]["message"]["content"], None
    except Exception:
        return None, r.text


# ----------------------------------------------------------------
# Source Formatter
# ----------------------------------------------------------------
def format_sources(local_docs, web_results):
    local_sources = sorted({d["source"] for d in local_docs})
    verified = [w["link"] for w in (web_results or []) if w.get("verified")]
    unverified = [
        f"{w['link']} ({w.get('reason')})"
        for w in (web_results or [])
        if not w.get("verified")
    ]

    return local_sources, verified, unverified


# ----------------------------------------------------------------
# Main Engine
# ----------------------------------------------------------------
def answer_question(question: str) -> dict:
    """
    Main callable for FastAPI.
    Does all RAG → web search → Google reviews → LLM → response formatting.
    """
    intent = decide_intent(question)

    # 1. Retrieve local docs
    local_docs = retrieve(question)

    # 2. Choose web scope
    if intent == "tanya":
        scope = "tanya"
    elif intent == "hybrid":
        scope = "tanya"
    else:
        scope = "baking"

    # 3. Search web
    web_results = web_search(question, scope=scope)

    # 4. Add Google reviews for Tanya
    if intent == "tanya":
        google_reviews = fetch_google_reviews_for_tanya()
        if google_reviews:
            web_results.extend(google_reviews)

    # 5. Safety: Tanya → only verified sources
    if intent == "tanya":
        verified = [w for w in web_results if w.get("verified")]
        if verified:
            web_results = verified
        else:
            web_results = []

    # 6. Build prompt
    prompt = build_combined_prompt(local_docs, web_results, question)

    # 7. Call models
    answer, err = call_openai(prompt)
    if not answer:
        answer, err = call_openrouter(prompt)
        if not answer:
            return {"error": err or "LLM failed"}

    # 8. Format sources
    src_local, src_verified, src_unverified = format_sources(local_docs, web_results)

    # 9. Return JSON for API
    return {
        "answer": answer,
        "sources": {
            "local": src_local,
            "web_verified": src_verified,
            "web_unverified": src_unverified,
        },
        "intent": intent,
    }
