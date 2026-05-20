---
name: whop
description: Use this skill whenever the user wants to do anything with Whop — selling digital products, deploying files (PDFs, eBooks, templates, courses, software tools), managing products/plans/memberships, creating checkout links, or setting up a Whop storefront. If the user mentions Whop, selling digital files, or wants to publish/deploy digital products to Whop, use this skill.
license: Apache-2.0
---

# Whop Digital Products Guide

## Overview

Whop is a platform for selling digital products: eBooks, PDFs, templates (DOCX/XLSX/PPTX), courses, software tools, memberships, and more. Files hosted on Google Drive or Dropbox can be linked directly as product downloads.

## Authentication

All API requests require a Bearer token. The API key starts with `whop_`:

```python
import requests

API_KEY = "whop_your_api_key_here"  # set via env var WHOP_API_KEY
BASE_URL = "https://api.whop.com"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}
```

Always read the API key from the environment:
```python
import os
API_KEY = os.environ["WHOP_API_KEY"]
```

## Core Concepts

- **Company**: Your seller account. One per Whop account.
- **Product**: A digital item for sale (eBook, template pack, course, tool, etc.).
- **Plan**: A pricing option attached to a product (one-time, recurring, free trial).
- **Membership**: Created when a customer purchases a plan. Grants access.
- **Checkout Link**: A shareable URL that takes buyers to purchase a plan.
- **File delivery**: Files are attached to products. Buyers get access after purchase.

## Company Info

```python
def get_company():
    resp = requests.get(f"{BASE_URL}/v5/companies/me", headers=headers)
    resp.raise_for_status()
    return resp.json()

company = get_company()
print(company["id"], company["title"])
```

## Products

### List Products

```python
def list_products():
    resp = requests.get(f"{BASE_URL}/v5/products", headers=headers)
    resp.raise_for_status()
    return resp.json()["data"]

for product in list_products():
    print(product["id"], product["name"])
```

### Create a Product

```python
def create_product(name: str, visibility: str = "visible"):
    payload = {
        "name": name,
        "visibility": visibility,  # "visible", "hidden", or "archived"
    }
    resp = requests.post(f"{BASE_URL}/v5/products", headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()

product = create_product("Ultimate Template Bundle")
product_id = product["id"]
```

### Get a Product

```python
def get_product(product_id: str):
    resp = requests.get(f"{BASE_URL}/v5/products/{product_id}", headers=headers)
    resp.raise_for_status()
    return resp.json()
```

### Update a Product

```python
def update_product(product_id: str, **fields):
    resp = requests.put(
        f"{BASE_URL}/v5/products/{product_id}",
        headers=headers,
        json=fields,
    )
    resp.raise_for_status()
    return resp.json()

update_product(product_id, name="Ultimate Template Bundle v2", visibility="visible")
```

## Plans (Pricing)

### Create a One-Time Payment Plan

```python
def create_one_time_plan(product_id: str, price_cents: int, currency: str = "usd"):
    payload = {
        "product_id": product_id,
        "plan_type": "one_time",
        "initial_price": price_cents,   # in cents, e.g. 2900 = $29.00
        "currency": currency,
        "billing_period": 0,
    }
    resp = requests.post(f"{BASE_URL}/v5/plans", headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()

plan = create_one_time_plan(product_id, price_cents=2900)  # $29.00
plan_id = plan["id"]
```

### Create a Recurring Subscription Plan

```python
def create_subscription_plan(
    product_id: str,
    price_cents: int,
    billing_period: int = 30,  # days
    currency: str = "usd",
):
    payload = {
        "product_id": product_id,
        "plan_type": "recurring",
        "renewal_price": price_cents,
        "billing_period": billing_period,
        "currency": currency,
    }
    resp = requests.post(f"{BASE_URL}/v5/plans", headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()

plan = create_subscription_plan(product_id, price_cents=999, billing_period=30)
```

### Create a Free Plan

```python
def create_free_plan(product_id: str):
    payload = {
        "product_id": product_id,
        "plan_type": "free",
        "initial_price": 0,
        "billing_period": 0,
    }
    resp = requests.post(f"{BASE_URL}/v5/plans", headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()
```

### List Plans for a Product

```python
def list_plans(product_id: str):
    resp = requests.get(
        f"{BASE_URL}/v5/plans",
        headers=headers,
        params={"product_id": product_id},
    )
    resp.raise_for_status()
    return resp.json()["data"]
```

## Checkout Links

A checkout link sends buyers directly to the payment page for a plan.

```python
def create_checkout_link(plan_id: str, redirect_url: str = None):
    payload = {"plan_id": plan_id}
    if redirect_url:
        payload["redirect_url"] = redirect_url
    resp = requests.post(
        f"{BASE_URL}/v5/checkout-links", headers=headers, json=payload
    )
    resp.raise_for_status()
    return resp.json()

link = create_checkout_link(plan_id, redirect_url="https://yoursite.com/thank-you")
print(link["url"])  # share this with buyers
```

## File Delivery — Linking Google Drive / Dropbox Files

Whop delivers files to buyers after purchase. For files hosted on Google Drive or Dropbox, use a direct-download URL as the file source.

### Getting a Direct Download URL

**Google Drive:**
1. Open the file in Google Drive
2. Click Share → "Anyone with the link" → Copy link
3. Transform the share URL:
   - Share URL: `https://drive.google.com/file/d/FILE_ID/view?usp=sharing`
   - Direct download: `https://drive.google.com/uc?export=download&id=FILE_ID`

**Dropbox:**
1. Get the share link (ends in `?dl=0`)
2. Change `?dl=0` to `?dl=1` for a direct download link

### Attaching a File to a Product via API

```python
def attach_file_to_product(product_id: str, file_url: str, file_name: str):
    payload = {
        "product_id": product_id,
        "url": file_url,       # direct download URL
        "name": file_name,
    }
    resp = requests.post(
        f"{BASE_URL}/v5/files", headers=headers, json=payload
    )
    resp.raise_for_status()
    return resp.json()

attach_file_to_product(
    product_id,
    file_url="https://drive.google.com/uc?export=download&id=YOUR_FILE_ID",
    file_name="Ultimate_Template_Bundle.zip",
)
```

### List Files Attached to a Product

```python
def list_product_files(product_id: str):
    resp = requests.get(
        f"{BASE_URL}/v5/files",
        headers=headers,
        params={"product_id": product_id},
    )
    resp.raise_for_status()
    return resp.json()["data"]
```

## Memberships (Customers)

### List Memberships for a Product

```python
def list_memberships(product_id: str, valid_only: bool = True):
    params = {"product_id": product_id}
    if valid_only:
        params["status"] = "active"
    resp = requests.get(f"{BASE_URL}/v5/memberships", headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()["data"]

members = list_memberships(product_id)
for m in members:
    print(m["id"], m["user"]["email"])
```

### Get a Single Membership

```python
def get_membership(membership_id: str):
    resp = requests.get(
        f"{BASE_URL}/v5/memberships/{membership_id}", headers=headers
    )
    resp.raise_for_status()
    return resp.json()
```

### Revoke a Membership

```python
def revoke_membership(membership_id: str):
    resp = requests.post(
        f"{BASE_URL}/v5/memberships/{membership_id}/revoke", headers=headers
    )
    resp.raise_for_status()
    return resp.json()
```

## Webhooks

Set up webhooks in the Whop dashboard under **Settings → Webhooks**. Whop sends events for:

- `membership.went_valid` — purchase completed, grant access / send file
- `membership.went_invalid` — subscription cancelled or expired
- `payment.succeeded` — payment confirmed
- `payment.failed` — payment failed

### Verify and Handle Webhook Events

```python
import hmac
import hashlib
from flask import Flask, request, jsonify

app = Flask(__name__)
WEBHOOK_SECRET = os.environ["WHOP_WEBHOOK_SECRET"]

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)

@app.route("/webhooks/whop", methods=["POST"])
def whop_webhook():
    sig = request.headers.get("X-Whop-Signature", "")
    if not verify_signature(request.data, sig, WEBHOOK_SECRET):
        return jsonify({"error": "invalid signature"}), 401

    event = request.json
    event_type = event.get("action")

    if event_type == "membership.went_valid":
        membership = event["data"]
        user_email = membership["user"]["email"]
        product_id = membership["product_id"]
        # Send welcome email, grant Discord access, etc.
        print(f"New member: {user_email} for product {product_id}")

    elif event_type == "membership.went_invalid":
        membership = event["data"]
        # Revoke access, remove from Discord, etc.
        print(f"Membership expired: {membership['id']}")

    return jsonify({"ok": True})
```

## Full Deployment Workflow

Use this sequence to publish a new digital product end-to-end:

```python
import os, requests

API_KEY = os.environ["WHOP_API_KEY"]
BASE_URL = "https://api.whop.com"
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def post(path, payload):
    r = requests.post(f"{BASE_URL}{path}", headers=headers, json=payload)
    r.raise_for_status()
    return r.json()

def get(path, params=None):
    r = requests.get(f"{BASE_URL}{path}", headers=headers, params=params)
    r.raise_for_status()
    return r.json()

# 1. Create product
product = post("/v5/products", {"name": "My eBook Bundle", "visibility": "visible"})
product_id = product["id"]
print(f"Product: {product_id}")

# 2. Create a one-time $19 plan
plan = post("/v5/plans", {
    "product_id": product_id,
    "plan_type": "one_time",
    "initial_price": 1900,
    "billing_period": 0,
    "currency": "usd",
})
plan_id = plan["id"]
print(f"Plan: {plan_id}")

# 3. Attach files (Google Drive direct-download URLs)
files = [
    ("https://drive.google.com/uc?export=download&id=GDRIVE_ID_1", "ebook.pdf"),
    ("https://drive.google.com/uc?export=download&id=GDRIVE_ID_2", "templates.zip"),
]
for url, name in files:
    post("/v5/files", {"product_id": product_id, "url": url, "name": name})
    print(f"Attached: {name}")

# 4. Create checkout link
checkout = post("/v5/checkout-links", {"plan_id": plan_id})
print(f"Checkout URL: {checkout['url']}")
```

## Quick Reference

| Task | Endpoint | Method |
|------|----------|--------|
| Get company info | `/v5/companies/me` | GET |
| List products | `/v5/products` | GET |
| Create product | `/v5/products` | POST |
| Update product | `/v5/products/{id}` | PUT |
| List plans | `/v5/plans?product_id=...` | GET |
| Create plan | `/v5/plans` | POST |
| Create checkout link | `/v5/checkout-links` | POST |
| Attach file | `/v5/files` | POST |
| List files | `/v5/files?product_id=...` | GET |
| List memberships | `/v5/memberships` | GET |
| Revoke membership | `/v5/memberships/{id}/revoke` | POST |

## Common Errors

| Status | Meaning | Fix |
|--------|---------|-----|
| 401 | Invalid API key | Check `WHOP_API_KEY` env var |
| 403 | Insufficient permissions | Use a key with seller scope |
| 404 | Resource not found | Verify the product/plan ID |
| 422 | Validation error | Check required fields in payload |
| 429 | Rate limited | Back off and retry after delay |
