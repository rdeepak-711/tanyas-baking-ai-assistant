# 🧁 Tanya’s Baking — AI Assistant (Hybrid RAG + Web Search + Google Reviews)

This project is an **AI-powered assistant** built specifically for **Tanya’s Baking (Chennai)**.
It combines:

* **Local structured data** (products, FAQs, business info)
* **Hybrid-RAG retrieval**
* **Intent-based routing**
* **Verified web search for baking knowledge**
* **Google Maps API for real Google ratings & reviews**
* **Tamil, English, & Tanglish support**
* **Model fallback (OpenAI → OpenRouter)**
* **Domain safety rules**

This ensures the AI stays **accurate, safe, and domain-specific**.

---

# 📁 Project Structure

```
tanyas-baking-ai-assistant
│
├── README.md
├── docs/
│   └── canonical_schema.md        # Your master data schema
│
├── data/
│   ├── business/
│   │   └── info.json              # Address, phone, hours, delivery info
│   ├── products/
│   │   └── products.json          # 10 product categories with images
│   ├── faq/
│   │   └── faq.json               # Manually curated FAQ
│   ├── instagram/
│   │   └── posts.json             # Scraped Instagram captions + images
│   ├── reviews/
│   │   └── google_reviews.json    # Fetched (Top 3) Google reviews
│   └── ingested_docs.json         # Final flattened RAG docs
│
├── src/
│   ├── ingest.py                  # Converts JSON → RAG chunk documents
│   ├── retrieve.py                # Custom keyword + scoring retrieval
│   ├── router.py                  # Intent classifier (tanya | baking | hybrid)
│   ├── web_search.py              # Serper search with Tanya whitelist filter
│   ├── google_reviews.py          # Fetches top 3 Google reviews for Tanya
│   ├── chat.py                    # The main hybrid agent
│   └── prompt_template.txt        # LLM prompt template
│
└── .env                           # API keys (OpenAI, Serper, Google, OpenRouter)
```

---

# 🚀 Features Completed

## ✅ 1. Canonical Data Model

A clean schema defining:

* Product structure
* Business info
* Instagram posts
* FAQ
* Reviews

Stored in `docs/canonical_schema.md`.

---

## ✅ 2. Local JSON Knowledge Base

You created:

* `info.json` (address, phone, hours, delivery options)
* `products.json` (10 categories + 10 images)
* `faq.json` (core Q&A about Tanya’s Baking)
* `posts.json` (Instagram scraped test set)

---

## ✅ 3. RAG Pipeline

`ingest.py` flattens JSON into small searchable text chunks.

`retrieve.py` performs:

* Token-based scoring
* Ranking
* Top-K retrieval

Used automatically by the bot.

---

## ✅ 4. Intent Router

`router.py` classifies every question as:

* **tanya** → Use Tanya-only knowledge
* **baking** → General baking + internet
* **hybrid** → Allow both

Examples:

| User Query                        | Intent |
| --------------------------------- | ------ |
| “What is Tanya’s address?”        | tanya  |
| “How to make buttercream?”        | baking |
| “Does Tanya make eggless cakes?”  | hybrid |
| “Teach me how to decorate a cake” | baking |
| “Reviews about Tanya”             | tanya  |

---

## ✅ 5. Real-Time Baking Knowledge (Web Search)

`web_search.py` uses **Serper API** to fetch:

* Recipes
* Techniques
* Ingredients
* Explanations

Results are filtered and cleaned before passing to the LLM.

---

## ✅ 6. Verified Google Reviews (Top 3)

`google_reviews.py` fetches:

* Business name
* Google rating
* Total reviews
* Top 3 customer reviews
* Verified source (Google Maps Place ID)

This ensures **no contamination** from other bakeries with similar names.

---

## ✅ 7. Domain Safety Rules

The assistant NEVER hallucinates other bakery data.

Safety layers:

* Verified PLACE_ID for Tanya
* Tanya web queries only return results from whitelisted URLs
* All other results are dropped
* If uncertain: respond safely (“not sure”)

---

## ✅ 8. Hybrid Prompt Building

`chat.py` merges:

```
LOCAL RAG CONTEXT
+
VERIFIED GOOGLE REVIEWS (if requested)
+
WEB SEARCH RESULTS (baking mode only)
```

Then sends the combined context to:

### Primary model

`OpenAI gpt-4o-mini (fast + best Tamil + English)`

### Fallback model

`meta-llama/3.1-8b-instruct (OpenRouter)`

---

## ✅ 9. Full Multi-Language Support

Tamil, English & Tanglish automatically detected.

---

# 🔥 Example Interaction (Working)

### Query:

```
Tanya's google review and rating
```

### Output:

```
Tanya's Baking has 5★ based on 166 reviews.
Top 3 reviews:
1. “Amazing taste…”
2. “Delivered on time…”
3. “My kids loved the custom cake…”

Sources:
- Google Maps (verified Place ID)
```

### Query:

```
How to make Swiss meringue buttercream?
```

→ Uses baking internet search + mix of top-rated recipe sites.

---

# ⚙️ Environment Variables

Create a `.env`:

```
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=or-...
SERPER_API_KEY=...
GOOGLE_API_KEY=...
```

---

# 🧪 Run the assistant

```
python3 src/chat.py
```

---
