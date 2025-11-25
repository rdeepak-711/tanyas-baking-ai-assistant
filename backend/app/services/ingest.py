import json
from pathlib import Path

# Paths to your data folders
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PRODUCTS_FILE = DATA_DIR / "products" / "products.json"
FAQ_FILE      = DATA_DIR / "faq"      / "faq.json"
BUSINESS_FILE = DATA_DIR / "business" / "info.json"
INSTAGRAM_FILE= DATA_DIR / "instagram"/ "posts.json"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def ingest():
    docs = []
    # Load business info
    biz = load_json(BUSINESS_FILE)
    docs.append({"type": "business", "id": "business_info", "text": json.dumps(biz), "source": BUSINESS_FILE.as_uri()})

    # Load FAQ
    faq_data = load_json(FAQ_FILE).get("faqs", [])
    for idx, f in enumerate(faq_data):
        docs.append({
            "type": "faq",
            "id": f"faq_{idx}",
        "text": f["question"] + " " + f["answer"],
        "source": FAQ_FILE.as_uri()
    })


    # Load Products
    prod_data = load_json(PRODUCTS_FILE).get("products", [])
    for p in prod_data:
        docs.append({"type": "product", "id": p["product_id"], "text": p["name"] + " " + p["description"], "source": PRODUCTS_FILE.as_uri()})

    # Load Instagram posts
    ig_data = load_json(INSTAGRAM_FILE).get("instagram_posts", [])
    for p in ig_data:
        docs.append({"type": "instagram", "id": p["post_id"], "text": p["caption"], "source": INSTAGRAM_FILE.as_uri()})

    # Save the “chunks” to file for now
    out_path = DATA_DIR / "ingested_docs.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    print(f"Ingested {len(docs)} documents → {out_path}")

if __name__ == "__main__":
    ingest()
