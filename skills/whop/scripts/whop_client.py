"""Whop API client — helper for managing digital products on Whop."""

import os
import sys
import requests

BASE_URL = "https://api.whop.com"


def get_headers():
    api_key = os.environ.get("WHOP_API_KEY")
    if not api_key:
        print("Error: WHOP_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


def api_get(path, params=None):
    r = requests.get(f"{BASE_URL}{path}", headers=get_headers(), params=params)
    r.raise_for_status()
    return r.json()


def api_post(path, payload):
    r = requests.post(f"{BASE_URL}{path}", headers=get_headers(), json=payload)
    r.raise_for_status()
    return r.json()


def api_put(path, payload):
    r = requests.put(f"{BASE_URL}{path}", headers=get_headers(), json=payload)
    r.raise_for_status()
    return r.json()


# ── Company ──────────────────────────────────────────────────────────────────

def get_company():
    return api_get("/v5/companies/me")


# ── Products ──────────────────────────────────────────────────────────────────

def list_products():
    return api_get("/v5/products").get("data", [])


def get_product(product_id):
    return api_get(f"/v5/products/{product_id}")


def create_product(name, visibility="visible"):
    return api_post("/v5/products", {"name": name, "visibility": visibility})


def update_product(product_id, **fields):
    return api_put(f"/v5/products/{product_id}", fields)


# ── Plans ─────────────────────────────────────────────────────────────────────

def list_plans(product_id):
    return api_get("/v5/plans", params={"product_id": product_id}).get("data", [])


def create_one_time_plan(product_id, price_cents, currency="usd"):
    return api_post("/v5/plans", {
        "product_id": product_id,
        "plan_type": "one_time",
        "initial_price": price_cents,
        "billing_period": 0,
        "currency": currency,
    })


def create_subscription_plan(product_id, price_cents, billing_period=30, currency="usd"):
    return api_post("/v5/plans", {
        "product_id": product_id,
        "plan_type": "recurring",
        "renewal_price": price_cents,
        "billing_period": billing_period,
        "currency": currency,
    })


def create_free_plan(product_id):
    return api_post("/v5/plans", {
        "product_id": product_id,
        "plan_type": "free",
        "initial_price": 0,
        "billing_period": 0,
    })


# ── Checkout Links ────────────────────────────────────────────────────────────

def create_checkout_link(plan_id, redirect_url=None):
    payload = {"plan_id": plan_id}
    if redirect_url:
        payload["redirect_url"] = redirect_url
    return api_post("/v5/checkout-links", payload)


# ── Files ─────────────────────────────────────────────────────────────────────

def list_product_files(product_id):
    return api_get("/v5/files", params={"product_id": product_id}).get("data", [])


def attach_file(product_id, file_url, file_name):
    return api_post("/v5/files", {
        "product_id": product_id,
        "url": file_url,
        "name": file_name,
    })


def gdrive_direct_url(file_id):
    """Convert a Google Drive file ID to a direct download URL."""
    return f"https://drive.google.com/uc?export=download&id={file_id}"


def dropbox_direct_url(share_url):
    """Convert a Dropbox share URL to a direct download URL."""
    return share_url.replace("?dl=0", "?dl=1").replace("&dl=0", "&dl=1")


# ── Memberships ───────────────────────────────────────────────────────────────

def list_memberships(product_id, status="active"):
    return api_get("/v5/memberships", params={
        "product_id": product_id,
        "status": status,
    }).get("data", [])


def get_membership(membership_id):
    return api_get(f"/v5/memberships/{membership_id}")


def revoke_membership(membership_id):
    return api_post(f"/v5/memberships/{membership_id}/revoke", {})


# ── Full deployment helper ────────────────────────────────────────────────────

def deploy_product(name, price_cents, files, currency="usd", redirect_url=None):
    """
    Create a product, one-time plan, attach files, and return a checkout URL.

    files: list of (url, filename) tuples — use gdrive_direct_url() or
           dropbox_direct_url() to convert share links first.
    """
    product = create_product(name)
    product_id = product["id"]
    print(f"Created product: {product_id} — {name}")

    plan = create_one_time_plan(product_id, price_cents, currency)
    plan_id = plan["id"]
    print(f"Created plan: {plan_id} (${price_cents / 100:.2f} {currency.upper()})")

    for url, fname in files:
        attach_file(product_id, url, fname)
        print(f"Attached file: {fname}")

    checkout = create_checkout_link(plan_id, redirect_url)
    checkout_url = checkout["url"]
    print(f"Checkout URL: {checkout_url}")

    return {
        "product_id": product_id,
        "plan_id": plan_id,
        "checkout_url": checkout_url,
    }


if __name__ == "__main__":
    import json

    company = get_company()
    print(f"Connected to Whop company: {company['title']} ({company['id']})")

    products = list_products()
    print(f"\nYour products ({len(products)}):")
    for p in products:
        print(f"  {p['id']}  {p['name']}  [{p['visibility']}]")
