# 🧁 Tanya’s Baking — AI Assistant  
### Hybrid RAG + Web Search + Google Reviews + FastAPI Backend + Widget-Ready Architecture

This project is an **AI-powered assistant** built specifically for **Tanya’s Baking (Chennai)**.

It combines:

- **Local structured data** (products, FAQs, business info)
- **Hybrid-RAG retrieval**
- **Intent-based routing**
- **Verified baking web search**
- **Google Maps API for top 3 real reviews**
- **Domain safety filters to avoid other bakeries**
- **Tamil, English & Tanglish support**
- **FastAPI backend**
- **Widget-ready API to embed on any website**
- **Modular architecture (microservice-friendly)**

This ensures the AI is **accurate, safe, and fully tuned to Tanya’s Baking**.

---

# 📁 Project Structure

```
tanyas-baking-ai-assistant/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── chat.py                 # /ask endpoint
│   │   │   ├── admin.py                # admin routes (future)
│   │   │   ├── analytics.py            # usage logs (future)
│   │   │   └── models/
│   │   │       └── chat_models.py      # Request/Response models
│   │   │
│   │   ├── core/
│   │   │   └── config.py               # env loader + settings
│   │   │
│   │   ├── services/
│   │   │   ├── llm_engine.py           # main Hybrid AI engine
│   │   │   ├── retrieve.py             # local RAG retriever
│   │   │   ├── router.py               # intent: tanya/baking/hybrid
│   │   │   ├── web_search.py           # Serper search
│   │   │   ├── ingest.py               # build ingested_docs.json
│   │   │   ├── google_reviews.py       # verified Google reviews
│   │   │   └── prompt_template.txt     # LLM prompt template
│   │   │
│   │   ├── data/
│   │   │   ├── business/info.json
│   │   │   ├── products/products.json
│   │   │   ├── faq/faq.json
│   │   │   ├── instagram/posts.json
│   │   │   ├── reviews/google_reviews.json (optional)
│   │   │   └── ingested_docs.json
│   │   │
│   │   └── main.py                     # FastAPI bootstrap
│   │
│   └── requirements.txt
│
├── docs/
│   ├── canonical_schema.md             # data model
│   └── WHITELIST.md                    # allowed domain rules
│
└── README.md
```

---

# 🚀 Features Completed

## ✅ 1. Canonical Data Schema
Defines how all baking business data should be structured:
- Products
- Instagram posts
- Business details
- FAQ
- Ratings & reviews

Stored in: `docs/canonical_schema.md`.

---

## ✅ 2. JSON Knowledge Base
Manually curated + scraped data:

- `info.json` → address, hours, phone, delivery  
- `faq.json` → curated FAQ  
- `products.json` → 10 categories + prices + images  
- `posts.json` → Instagram captions/images  
- `google_reviews.json` (optional offline copy)  

---

## ✅ 3. RAG Pipeline (Local Retrieval)
`ingest.py` converts JSON → small search-friendly chunks.  
`retrieve.py` retrieves top-K matching chunks from:

```
data/ingested_docs.json
```

---

## ✅ 4. Intent Router
`router.py` decides:

| Intent | Meaning |
|--------|---------|
| **tanya** | data must be verified Tanya-specific + local data |
| **baking** | general baking recipes, tips, techniques |
| **hybrid** | mix both (ex: “eggless cake Tanya makes?”) |

---

## ✅ 5. Verified Web Search (Baking Only)
`web_search.py` uses Serper API to fetch:

- Recipes  
- Techniques  
- Baking tutorials  
- Ingredients  
- Methods  

Filtered & ranked before sending to the LLM.

---

## ✅ 6. Verified Google Reviews (Top 3)
`google_reviews.py` fetches:

- Google rating  
- Total number of reviews  
- Top 3 verified reviews  
- Verified via **place_id**  
- Prevents contamination from other bakeries with the same name

---

## ✅ 7. Domain-Safety Rules ✔
The assistant **never mixes** other bakeries with similar names:

- Uses Tanya-specific **place_id**
- Only accepts verified URLs
- Filters out irrelevant search results
- If unsure → safely replies “Not sure”

---

## ✅ 8. Hybrid LLM Engine
`llm_engine.py` merges:

```
LOCAL RAG CONTEXT
+ VERIFIED GOOGLE REVIEWS
+ WEB SEARCH RESULTS
+ INTENT ROUTING
```

Then calls:

### Primary  
✔ `OpenAI gpt-4o-mini` (Tamil + English best)

### Fallback  
✔ `meta-llama/3.1-8b-instruct` (OpenRouter)

---

## ✅ 9. REST API (FastAPI)
### Chat endpoint
```
POST /api/chat/ask
```

Payload:
```json
{
  "question": "How to make buttercream?",
  "session_id": "user-123"
}
```

Response:
```json
{
  "answer": "...",
  "local_sources": [...],
  "web_sources_verified": [...],
  "web_sources_unverified": [...],
  "intent": "baking"
}
```

---

# 🎈 Future Roadmap

## 🟢 **1. Frontend Chat Widget (Floating Bubble)**
Embed anywhere — React, plain HTML, WordPress, Shopify.

Features:
- Floating icon
- Chat popup
- Typing indicator
- Theme customization
- Powered by `/chat/ask`

## 🟢 **2. Admin Dashboard (Next.js + FastAPI)**
See:
- Conversations
- Top queries
- User sessions
- Errors
- Web search usage
- Analytics graphs
- Custom FAQ editor
- Product editor
- Upload training data

## 🟢 **3. Conversation Storage (PostgreSQL/MongoDB)**

## 🟢 **4. Webhook for WhatsApp**

## 🟢 **5. Multi-business Generic Version**
Turn this into **“AI Assistant for Local Businesses Blueprint”** where any store can:

- Upload products  
- Upload images  
- Upload FAQ  
- Configure brand  
- Embed widget  
- Launch bot in 5 minutes  

---

# ⚙️ Environment Variables

Create `.env` in `backend/`:

```
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=or-...
SERPER_API_KEY=...
GOOGLE_API_KEY=...
```

---

# ▶️ Running the Backend

```
cd backend
uvicorn app.main:app --reload
```

---

# 🧪 Test Chatbot (Command Line Version)

```
python3 backend/app/services/llm_engine.py
```

---

