import re

TANYA_KEYWORDS = [
    "tanya", "tanyas", "tanya's", "tanyas baking", "tanyas_baking",
    "our cakes", "pound cake", "sickle cake", "madambakkam", "padmavathy"
]
BAKING_KEYWORDS = [
    "recipe", "how to", "bake", "baking", "ingredients", "oven", "ganache", "buttercream",
    "eggless", "temperature", "preheat", "whisk", "fold"
]

def decide_intent(query: str) -> str:
    q = query.lower()

    # if query explicitly mentions Tanya -> tanya
    if any(k in q for k in TANYA_KEYWORDS):
        # if also baking words present -> hybrid
        if any(b in q for b in BAKING_KEYWORDS):
            return "hybrid"
        return "tanya"

    # if explicitly baking -> baking
    if any(b in q for b in BAKING_KEYWORDS):
        return "baking"

    # default: treat as tanya if short and likely user asking about store (where, address)
    if re.search(r"\b(address|where|open|hours|timings|price|order|menu|class|classess|delivery)\b", q):
        return "tanya"

    # fallback conservative: hybrid
    return "hybrid"
