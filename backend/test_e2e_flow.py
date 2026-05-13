#!/usr/bin/env python3
"""端到端业务流程测试脚本"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_e2e():
    # Step 1: 注册
    print("=== Step 1: 注册用户 ===")
    r = requests.post(f"{BASE_URL}/auth/register", json={
        "username": "e2e_flow_user",
        "email": "e2eflow@test.com",
        "password": "Test123456",
        "confirm_password": "Test123456"
    })
    data = r.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    token = data.get("access_token", "")
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: 浏览市场
    print("\n=== Step 2: 浏览算力市场 ===")
    r = requests.get(f"{BASE_URL}/marketplace/assets?page=1&page_size=2", headers=headers)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False)[:500])

    # Step 3: 获取报价
    print("\n=== Step 3: 智能报价 ===")
    r = requests.post(f"{BASE_URL}/scheduling/quote", headers=headers, json={
        "asset_id": "asset-001",
        "instance_type": "compute",
        "duration_hours": 2,
        "gpu_count": 2
    })
    quote = r.json()
    print(json.dumps(quote, indent=2, ensure_ascii=False))

    # Step 4: 创建订单
    print("\n=== Step 4: 提交订单 ===")
    r = requests.post(f"{BASE_URL}/orders/", headers=headers, json={
        "asset_id": "asset-001",
        "compute_cost": 30,
        "energy_cost": 10,
        "total_cost": 40,
        "instance_type": "compute"
    })
    order = r.json()
    print(json.dumps(order, indent=2, ensure_ascii=False))
    order_id = order.get("id")

    # Step 5: 支付订单
    print(f"\n=== Step 5: 支付订单 ({order_id}) ===")
    r = requests.put(f"{BASE_URL}/orders/{order_id}/pay", headers=headers, json={
        "payment_method": "wallet"
    })
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))

    # Step 6: 查看钱包
    print("\n=== Step 6: 查看钱包余额 ===")
    r = requests.get(f"{BASE_URL}/wallet/balance", headers=headers)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))

    # Step 7: 查看账单
    print("\n=== Step 7: 查看账单 ===")
    r = requests.get(f"{BASE_URL}/bills/monthly?year=2026&month=5", headers=headers)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))

    # Step 8: 查看监控
    print("\n=== Step 8: 查看监控指标 ===")
    r = requests.get(f"{BASE_URL}/monitoring/resources/asset-001/latest", headers=headers)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))

    print("\n=== 全链路业务流程测试完成 ===")

if __name__ == "__main__":
    test_e2e()
