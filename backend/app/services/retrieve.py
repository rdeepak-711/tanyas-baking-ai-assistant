import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
INGESTED_FILE = DATA_DIR / "ingested_docs.json"

def load_docs():
    with open(INGESTED_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def simple_keyword_search(query, docs, top_k=3):
    query_tokens = re.findall(r"\w+", query.lower())
    scored = []

    # Define keywords that indicate "business info"
    business_keywords = {"address", "location", "where", "reach", "map"}

    for doc in docs:
        text = doc["text"].lower()
        score = sum(token in text for token in query_tokens)

        # If any business keywords appear in the query → boost business doc
        if any(keyword in query_tokens for keyword in business_keywords):
            if doc["type"] == "business":
                score += 5   # strong boost

        # Avoid adding docs with no score at all
        if score > 0:
            scored.append((score, doc))

    # Sort by score
    scored.sort(reverse=True, key=lambda x: x[0])

    # Return only the docs
    return [doc for _, doc in scored[:top_k]]


def retrieve(query):
    docs = load_docs()
    results = simple_keyword_search(query, docs)
    print(f"Retrieved {len(results)} documents for query: “{query}”")
    return results

if __name__ == "__main__":
    query = input("Enter your question: ")
    results = retrieve(query)
    for r in results:
        print(f"- {r['type']} | {r['id']} | source={r['source']}")
        print(f"  → {r['text'][:200]} …")
