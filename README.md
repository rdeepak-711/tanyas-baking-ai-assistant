# Tanya's Baking AI Assistant

An AI-powered assistant designed specifically for **Tanya's Baking (Chennai)**.  
The goal is to help customers quickly find product information, inquire about prices, understand delivery details, explore Instagram posts, and get answers to FAQs — through **chat and voice** in **English & Tamil**.

This repo documents the **data**, **schemas**, and later the **code** that powers the assistant.

---

## 📌 Current Stage: STEP 1 — Canonical Data Model

We have defined the **minimal and practical** data schema that will be used to store and retrieve all information needed by the assistant.

You can find the schema here:

➡️ **`/docs/canonical_schema.md`**

It contains five core entity definitions:

1. **Product**
2. **Business Info**
3. **Reviews**
4. **Instagram Post**
5. **FAQ**

These are the base structures for all future scraping, ingestion, and search.

---

## 🚀 Project Vision (Short)

The end goal is to build:

- A **chat + voice AI assistant** for Tanya’s Baking  
- Supporting **Tamil + English**  
- Trained on **website, Instagram, Google, JustDial**, and manually curated data  
- Capable of answering product queries, class details, ordering info, and more  
- With a clean admin dashboard for updating data

---

## 🗂 Project Structure (as of now)

