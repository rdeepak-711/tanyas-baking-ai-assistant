# Canonical Data Model (Master Schema)

This document defines the minimal and practical data model for Tanya's Baking AI Assistant.  
It contains only the essential fields required at this stage.  
More fields may be added later as the assistant grows.

---

## ⭐ PRODUCT (Cake / Cupcake / Brownie / Class)

| Field         | Description |
|---------------|-------------|
| `product_id`  | Unique ID for each product |
| `name`        | Name of the product |
| `category`    | Category (e.g., Cake, Cupcake, Brownie, Class) |
| `description` | Short description of the product |
| `price`       | Price or base price |
| `size_options`| Sizes available (e.g., 0.5kg, 1kg) |
| `image_urls`  | List of associated images |
| `source_urls` | Where the product information was extracted from |

---

## ⭐ BUSINESS INFO

| Field             | Description |
|-------------------|-------------|
| `business_name`   | Official business name |
| `address`         | Full address |
| `contact_numbers` | Phone numbers for contact |
| `whatsapp`        | WhatsApp number for orders |
| `working_hours`   | Business operating hours |
| `delivery_info`   | Delivery or pickup details |

---

## ⭐ REVIEWS

| Field        | Description |
|--------------|-------------|
| `review_id`  | Unique review identifier |
| `platform`   | Source platform (Google, JustDial, Instagram, etc.) |
| `rating`     | Rating if available (1–5) |
| `text`       | Review content |
| `date`       | Date of the review |
| `source_url` | Link to the original review |

---

## ⭐ INSTAGRAM POST

| Field        | Description |
|--------------|-------------|
| `post_id`    | Instagram post ID |
| `caption`    | Caption text extracted from the post |
| `image_urls` | Images or thumbnails |
| `date`       | Posting date |
| `source_url` | URL of the Instagram post |

---

## ⭐ FAQ

| Field      | Description |
|------------|-------------|
| `question` | Frequently asked question |
| `answer`   | Answer to the question |
| `source`   | Where the question/answer came from |

---

### ✔ This file forms the base structure for all further scraping, storage, and RAG pipeline development.
