"""Phase 2 Complete E2E Test Suite"""
import requests
import time
import sys

BASE = "http://127.0.0.1:8000/api/v1"
passed = 0
failed = 0
errors = []

def test(name, response, expected_status=None, check_fn=None):
    global passed, failed, errors
    status = response.status_code
    ok = True
    if expected_status:
        if isinstance(expected_status, list):
            if status not in expected_status:
                ok = False
        elif status != expected_status:
            ok = False
    if check_fn and not check_fn(response):
        ok = False
    if ok:
        passed += 1
        print(f"  PASS {name}: {status}")
    else:
        failed += 1
        detail = response.text[:200]
        print(f"  FAIL {name}: {status} (expected {expected_status}) - {detail}")
        errors.append(f"{name}: {status} - {detail}")


# Setup - register new user
r = requests.post(f"{BASE}/auth/register", json={
    "username": f"full_e2e_{int(time.time())}",
    "email": f"full_e2e_{int(time.time())}@test.com",
    "password": "Test1234",
    "role": "consumer"
})
token = r.json()["access_token"]
H = {"Authorization": f"Bearer {token}"}

print("=== Phase 2 Complete E2E Test Suite ===")
print()

# ====== 1. Wallet Module ======
print("[1] Wallet Module")
r = requests.get(f"{BASE}/wallet/balance", headers=H)
test("Get Balance", r, 200, lambda r: "balance" in r.json())

r = requests.post(f"{BASE}/wallet/recharge", json={"amount": 500.0, "payment_method": "alipay"}, headers=H)
test("Recharge (Alipay)", r, 200, lambda r: r.json().get("status") == "success")

r = requests.post(f"{BASE}/wallet/recharge", json={"amount": 200.0, "payment_method": "wechat"}, headers=H)
test("Recharge (WeChat)", r, 200, lambda r: r.json().get("status") == "success")

r = requests.get(f"{BASE}/wallet/transactions", headers=H)
test("Get Transactions", r, 200, lambda r: "items" in r.json())

r = requests.get(f"{BASE}/wallet/transactions", params={"type": "recharge"}, headers=H)
test("Filter Transactions by Type", r, 200)

r = requests.post(f"{BASE}/wallet/withdraw", json={
    "amount": 10.0, "bank_card": "6222000000001",
    "bank_name": "ICBC", "account_name": "Test User"
}, headers=H)
test("Withdraw (with bank info)", r, 200)

r = requests.put(f"{BASE}/wallet/low-balance-alert", json={"threshold": 100.0}, headers=H)
test("Set Low Balance Alert", r, 200)

# ====== 2. Marketplace Module ======
print()
print("[2] Marketplace Module")
r = requests.get(f"{BASE}/marketplace/assets", headers=H)
test("List Assets", r, 200, lambda r: "items" in r.json() and len(r.json()["items"]) > 0)

r = requests.get(f"{BASE}/marketplace/assets", params={"gpu_model": "A100", "region": "华北"}, headers=H)
test("Search Assets with Filters", r, 200, lambda r: "items" in r.json())

r = requests.get(f"{BASE}/marketplace/assets/asset-001", headers=H)
test("Get Asset Detail", r, 200, lambda r: "id" in r.json())

r = requests.get(f"{BASE}/marketplace/assets/asset-001/reviews", headers=H)
test("GET Asset Reviews", r, 200, lambda r: "items" in r.json())

r = requests.get(f"{BASE}/marketplace/assets/asset-999/reviews", headers=H)
test("GET Reviews (nonexistent asset)", r, 200, lambda r: r.json().get("total") == 0)

# ====== 3. Order Lifecycle ======
print()
print("[3] Order Lifecycle")
r = requests.post(f"{BASE}/orders/", json={"asset_id": "asset-001"}, headers=H)
test("Create Order", r, 201)
order_id = r.json().get("id", "")

if order_id:
    r = requests.get(f"{BASE}/orders/{order_id}", headers=H)
    test("Get Order Detail", r, 200, lambda r: r.json().get("status") == "pending")

    r = requests.put(f"{BASE}/orders/{order_id}/pay", headers=H)
    test("Pay Order", r, 200, lambda r: r.json().get("status") in ["paid", "running"])

    r = requests.get(f"{BASE}/orders/{order_id}/status-history", headers=H)
    test("Get Status History", r, 200, lambda r: len(r.json()) >= 2)

    r = requests.put(f"{BASE}/orders/{order_id}/complete", headers=H)
    test("Complete Order", r, 200, lambda r: r.json().get("status") == "completed")

    r = requests.post(f"{BASE}/orders/{order_id}/review", json={"score": 5, "text": "Excellent GPU!"}, headers=H)
    test("Review Order", r, 200, lambda r: r.json().get("success") == True)

    # Create second order for refund test
    r2 = requests.post(f"{BASE}/orders/", json={"asset_id": "asset-002"}, headers=H)
    order_id2 = r2.json().get("id", "")
    if order_id2:
        r2 = requests.put(f"{BASE}/orders/{order_id2}/pay", headers=H)
        test("Pay Order 2", r2, 200)
        r2 = requests.post(f"{BASE}/orders/{order_id2}/refund", json={"reason": "Test refund"}, headers=H)
        test("Refund Order", r2, 200, lambda r: r.json().get("success") == True)

    # Create third order for cancel test
    r3 = requests.post(f"{BASE}/orders/", json={"asset_id": "asset-003"}, headers=H)
    order_id3 = r3.json().get("id", "")
    if order_id3:
        r3 = requests.put(f"{BASE}/orders/{order_id3}/cancel", headers=H)
        test("Cancel Order", r3, 200, lambda r: r.json().get("status") == "cancelled")

# ====== 4. Payments Module ======
print()
print("[4] Payments Module")
r = requests.post(f"{BASE}/orders/", json={"asset_id": "asset-004"}, headers=H)
pid_order = r.json().get("id", "")
if pid_order:
    r = requests.post(f"{BASE}/payments/create", json={
        "order_id": pid_order, "amount": 10.0, "payment_method": "alipay"
    }, headers=H)
    test("Create Payment for Pending Order", r, 200)

r = requests.get(f"{BASE}/payments/order/{order_id}", headers=H)
test("Get Payment by Order ID", r, [200, 404])

# ====== 5. Monitoring Module ======
print()
print("[5] Monitoring Module")
r = requests.get(f"{BASE}/monitoring/resources/asset-001/latest", headers=H)
test("Get Latest Metrics", r, 200)

r = requests.get(f"{BASE}/monitoring/resources/asset-001/metrics", params={
    "metric": "cpu_usage",
    "from_time": "2026-05-13T00:00:00",
    "to_time": "2026-05-13T23:59:59",
}, headers=H)
test("Query Historical Metrics", r, 200, lambda r: "data_points" in r.json())

r = requests.post(f"{BASE}/monitoring/alert-rules", json={
    "name": "CPU High Alert",
    "resource_id": "asset-001",
    "metric": "cpu_usage",
    "condition": "gt",
    "threshold": 90.0,
    "duration_seconds": 60,
    "notify_channels": "web",
    "cooldown_seconds": 300
}, headers=H)
test("Create Alert Rule", r, 200)

r = requests.get(f"{BASE}/monitoring/alert-rules", headers=H)
test("List Alert Rules", r, 200)

r = requests.get(f"{BASE}/monitoring/alerts", headers=H)
test("List Alerts", r, 200)

# ====== 6. Billing Module ======
print()
print("[6] Billing Module")
r = requests.post(f"{BASE}/bills/generate", json={"year": 2026, "month": 5}, headers=H)
test("Generate Bill", r, 200, lambda r: r.json().get("status") == "generated")

r = requests.get(f"{BASE}/bills/monthly", params={"year": 2026, "month": 5}, headers=H)
test("Get Monthly Bill", r, 200)

r = requests.get(f"{BASE}/bills/list", headers=H)
test("List Bills", r, 200, lambda r: "items" in r.json())

r = requests.get(f"{BASE}/bills/invoices", headers=H)
test("List Invoices", r, 200)

r = requests.get(f"{BASE}/bills/reconciliation", params={
    "start_date": "2026-05-01", "end_date": "2026-05-31"
}, headers=H)
test("Reconciliation", r, 200)

# ====== 7. Phase 1 Compat ======
print()
print("[7] Phase 1 Compatibility")
r = requests.get("http://127.0.0.1:8000/health")
test("Health Check", r, 200)

r = requests.get(f"{BASE}/monitoring/tasks/order-0001", headers=H)
test("Task Status", r, 200)

r = requests.get(f"{BASE}/monitoring/tasks/order-0001/logs", headers=H)
test("Task Logs", r, 200)

r = requests.get(f"{BASE}/earnings/summary", headers=H)
test("Earnings Summary", r, 200)

r = requests.post(f"{BASE}/scheduling/quote", json={
    "task_type": "inference", "strategy": "cheapest", "estimated_duration_hours": 2
}, headers=H)
test("Scheduling Quote", r, 200)

r = requests.post(f"{BASE}/scheduling/validate", json={
    "container_image": "pytorch/pytorch:latest",
    "task_type": "inference", "estimated_duration_hours": 2
}, headers=H)
test("Scheduling Validate", r, 200)

# ====== Summary ======
print()
print("=" * 60)
print(f"  Total: {passed + failed} | PASS: {passed} | FAIL: {failed}")
if errors:
    print()
    print("  Failed Tests:")
    for e in errors:
        print(f"    - {e}")
print("=" * 60)

sys.exit(0 if failed == 0 else 1)
