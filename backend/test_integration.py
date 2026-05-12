"""
前后端API集成测试脚本
验证所有前后端API端点的连通性和数据格式
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"
TEST_USER = {"username": f"testuser_api", "password": "Test123456", "email": "testapi@test.com", "role": "consumer"}

results = []
token = None

def test(name, func):
    """运行测试并记录结果"""
    try:
        result = func()
        results.append({"name": name, "status": "PASS", "detail": result})
        print(f"  ✅ {name}: {result}")
    except Exception as e:
        results.append({"name": name, "status": "FAIL", "detail": str(e)})
        print(f"  ❌ {name}: {e}")

# 1. 健康检查
print("\n=== 1. 健康检查 ===")
test("GET /health", lambda: requests.get("http://localhost:8000/health").json())

# 2. 用户注册
print("\n=== 2. 用户注册 ===")
def register():
    r = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)
    data = r.json()
    global token
    token = data.get("access_token")
    if not token:
        # 如果已注册，尝试登录
        r = requests.post(f"{BASE_URL}/auth/login", json={"username": TEST_USER["username"], "password": TEST_USER["password"]})
        data = r.json()
        token = data.get("access_token")
    return f"token={'yes' if token else 'no'}, user={data.get('user', {}).get('username', 'N/A')}"
test("POST /auth/register", register)

# 3. 用户登录
print("\n=== 3. 用户登录 ===")
def login():
    r = requests.post(f"{BASE_URL}/auth/login", json={"username": TEST_USER["username"], "password": TEST_USER["password"]})
    data = r.json()
    global token
    token = data.get("access_token")
    return f"token={'yes' if token else 'no'}, type={data.get('token_type', 'N/A')}"
test("POST /auth/login", login)

headers = {"Authorization": f"Bearer {token}"} if token else {}

# 4. 资产管理
print("\n=== 4. 资产管理 ===")
def create_asset():
    r = requests.post(f"{BASE_URL}/assets/", json={
        "owner_id": "test-user-001",
        "type": "compute",
        "spec": {"gpu": "A100-80G", "vram": "80GB", "cpu_cores": 128, "memory_gb": 512},
        "pricing": {"compute_price_per_hour": 15.5, "is_spot": False, "spot_discount": 0},
        "energy_profile": {"power_source": "solar", "PUE": 1.2, "carbon_intensity": 0.3, "price_per_kwh": 0.45},
        "location": {"region": "east-china", "zone": "zone-a"},
    }, headers=headers)
    data = r.json()
    return f"status={r.status_code}, id={data.get('id', 'N/A')}"
test("POST /assets/", create_asset)

def list_assets():
    r = requests.get(f"{BASE_URL}/assets/?page=1&page_size=10", headers=headers)
    data = r.json()
    items = data.get("items", [])
    total = data.get("total", 0)
    return f"total={total}, items_count={len(items)}, has_pagination={'page' in data}"
test("GET /assets/", list_assets)

# 5. 资源市场
print("\n=== 5. 资源市场 ===")
def search_marketplace():
    r = requests.get(f"{BASE_URL}/marketplace/assets?page=1&page_size=10", headers=headers)
    data = r.json()
    items = data.get("items", [])
    total = data.get("total", 0)
    return f"total={total}, items_count={len(items)}"
test("GET /marketplace/assets", search_marketplace)

def search_with_filters():
    r = requests.get(f"{BASE_URL}/marketplace/assets?power_source=solar&region=east-china", headers=headers)
    data = r.json()
    return f"total={data.get('total', 0)}, items_count={len(data.get('items', []))}"
test("GET /marketplace/assets?filters", search_with_filters)

# 6. 智能调度
print("\n=== 6. 智能调度 ===")
def validate_task():
    r = requests.post(f"{BASE_URL}/scheduling/validate", json={
        "container_image": "pytorch/pytorch:latest",
        "task_type": "inference",
        "estimated_duration_hours": 2.0,
    }, headers=headers)
    data = r.json()
    return f"valid={data.get('valid', 'N/A')}"
test("POST /scheduling/validate", validate_task)

def get_quote():
    r = requests.post(f"{BASE_URL}/scheduling/quote", json={
        "task_type": "inference",
        "strategy": "cheapest",
        "estimated_duration_hours": 2.0,
    }, headers=headers)
    data = r.json()
    quotes = data.get("quotes", [])
    recommended = data.get("recommended_quote")
    return f"quotes_count={len(quotes)}, has_recommended={recommended is not None}"
test("POST /scheduling/quote", get_quote)

# 7. 订单管理
print("\n=== 7. 订单管理 ===")
def submit_task():
    r = requests.post(f"{BASE_URL}/scheduling/tasks", json={
        "selected_quote": {
            "asset_id": "asset-sim-001",
            "compute_cost": 25.0,
            "energy_cost": 5.0,
            "total_cost": 30.0,
            "carbon_saved_kg": 10.0,
        },
        "container_image": "pytorch/pytorch:latest",
        "task_type": "inference",
        "estimated_duration_hours": 2.0,
    }, headers=headers)
    data = r.json()
    return f"order_id={data.get('order_id', 'N/A')}, status={data.get('status', 'N/A')}"
test("POST /scheduling/tasks", submit_task)

def list_orders():
    r = requests.get(f"{BASE_URL}/orders/?page=1&page_size=10", headers=headers)
    data = r.json()
    items = data.get("items", [])
    total = data.get("total", 0)
    return f"total={total}, items_count={len(items)}"
test("GET /orders/", list_orders)

# 8. 任务监控
print("\n=== 8. 任务监控 ===")
def get_task_status():
    r = requests.get(f"{BASE_URL}/monitoring/tasks/test-task-001", headers=headers)
    data = r.json()
    return f"status={data.get('status', 'N/A')}, has_metrics={'real_time_metrics' in data}"
test("GET /monitoring/tasks/{id}", get_task_status)

# 9. 收益概览
print("\n=== 9. 收益概览 ===")
def get_earnings():
    r = requests.get(f"{BASE_URL}/earnings/summary", headers=headers)
    data = r.json()
    return f"today={data.get('today', 0)}, this_month={data.get('this_month', 0)}"
test("GET /earnings/summary", get_earnings)

# 汇总
print("\n" + "="*50)
passed = sum(1 for r in results if r["status"] == "PASS")
failed = sum(1 for r in results if r["status"] == "FAIL")
print(f"测试结果: ✅ {passed} 通过, ❌ {failed} 失败, 共 {len(results)} 项")
if failed > 0:
    print("\n失败项目:")
    for r in results:
        if r["status"] == "FAIL":
            print(f"  ❌ {r['name']}: {r['detail']}")
