#!/usr/bin/env python3
"""Test backend API endpoints"""
import requests
import json
import sys

BASE = "http://127.0.0.1:8000"

def test_health():
    r = requests.get(f"{BASE}/health")
    print(f"GET /health: {r.status_code} -> {r.json()}")
    return True

def test_login():
    r = requests.post(
        f"{BASE}/api/v1/auth/login",
        json={"username": "testuser", "password": "Test123456"},
    )
    print(f"POST /auth/login: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  token(prefix): {data['access_token'][:20]}...")
        print(f"  user: {data['user']}")
        return data["access_token"]
    else:
        print(f"  ERROR: {r.text}")
        return None

def test_assets(token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE}/api/v1/assets/", headers=headers, params={"page": 1, "page_size": 5})
    print(f"GET /assets/: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  items: {len(data.get('items', data if isinstance(data, list) else []))}")
        print(f"  total: {data.get('total', 'N/A')}")
    else:
        print(f"  ERROR: {r.text[:500]}")

def test_marketplace():
    r = requests.get(f"{BASE}/api/v1/marketplace/assets", params={"page": 1, "page_size": 5})
    print(f"GET /marketplace/assets: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  items: {len(data.get('items', []))}")
        print(f"  total: {data.get('total', 'N/A')}")
    else:
        print(f"  ERROR: {r.text[:500]}")

def test_quote():
    r = requests.post(
        f"{BASE}/api/v1/scheduling/quote",
        json={"task_type": "inference", "strategy": "cheapest", "estimated_duration_hours": 2.0},
    )
    print(f"POST /scheduling/quote: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  quotes: {len(data.get('quotes', []))}")
        print(f"  recommended: {'YES' if data.get('recommended_quote') else 'NO'}")
    else:
        print(f"  ERROR: {r.text[:500]}")

if __name__ == "__main__":
    try:
        test_health()
    except Exception as e:
        print(f"ERROR: Backend not running? {e}")
        sys.exit(1)

    token = test_login()
    if token:
        test_assets(token)
    test_marketplace()
    test_quote()
    print("\nAll tests completed!")
