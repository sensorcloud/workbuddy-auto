#!/usr/bin/env python3
"""Prepare file data for GitHub push in batches."""
import os
import json
import base64

BASE_DIR = r"C:\Users\Administrator\WorkBuddy\2026-05-11-task-2"

# All tracked files (from git ls-tree)
ALL_FILES = [
    ".gitignore",
    "README.md",
    "Architecture-算电协同平台-Phase1.md",
    "DeliveryReport-Phase1-Final.md",
    "DeliveryReport-算电协同平台-Phase1.md",
    "PRD-算电协同平台-Phase1.md",
    "TestReport-算电协同平台-Phase1.md",
    "VerificationReport-Phase1.md",
    "backend/app/api/__init__.py",
    "backend/app/api/assets.py",
    "backend/app/api/auth.py",
    "backend/app/api/earnings.py",
    "backend/app/api/marketplace.py",
    "backend/app/api/monitoring.py",
    "backend/app/api/orders.py",
    "backend/app/api/payments.py",
    "backend/app/api/scheduling.py",
    "backend/app/api/users.py",
    "backend/app/core/config.py",
    "backend/app/core/logging.py",
    "backend/app/core/security.py",
    "backend/app/database.py",
    "backend/app/main.py",
    "backend/app/models/asset.py",
    "backend/app/models/base.py",
    "backend/app/models/order.py",
    "backend/app/models/user.py",
    "backend/app/schemas/__init__.py",
    "backend/app/schemas/asset.py",
    "backend/app/schemas/order.py",
    "backend/app/schemas/user.py",
    "backend/app/services/__init__.py",
    "backend/app/services/asset_service.py",
    "backend/app/services/auth_service.py",
    "backend/app/services/earnings_service.py",
    "backend/app/services/marketplace_service.py",
    "backend/app/services/monitoring_service.py",
    "backend/app/services/order_service.py",
    "backend/app/services/payment_service.py",
    "backend/app/services/scheduling_service.py",
    "backend/app/services/user_service.py",
    "backend/requirements.txt",
    "backend/test_api.py",
    "backend/test_integration.py",
    "frontend/index.html",
    "frontend/package.json",
    "frontend/package-lock.json",
    "frontend/src/App.tsx",
    "frontend/src/assets/styles/global.css",
    "frontend/src/components/Common/ErrorBoundary.tsx",
    "frontend/src/components/Layout/index.tsx",
    "frontend/src/main.tsx",
    "frontend/src/pages/AssetManagement/index.tsx",
    "frontend/src/pages/Home/index.tsx",
    "frontend/src/pages/Marketplace/index.tsx",
    "frontend/src/pages/Monitoring/index.tsx",
    "frontend/src/pages/NotFound/index.tsx",
    "frontend/src/pages/Orders/index.tsx",
    "frontend/src/pages/Payment/index.tsx",
    "frontend/src/pages/Scheduling/index.tsx",
    "frontend/src/pages/UserCenter/Login.tsx",
    "frontend/src/pages/UserCenter/Register.tsx",
    "frontend/src/pages/UserCenter/index.tsx",
    "frontend/src/router/routes.tsx",
    "frontend/src/services/api.ts",
    "frontend/src/store/authStore.ts",
    "frontend/src/types/asset.types.ts",
    "frontend/src/types/order.types.ts",
    "frontend/tsconfig.json",
    "frontend/tsconfig.node.json",
    "frontend/vite.config.ts",
]

def read_file_content(filepath):
    """Read file content as string."""
    full_path = os.path.join(BASE_DIR, filepath)
    if not os.path.exists(full_path):
        print(f"WARNING: File not found: {full_path}")
        return None
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(full_path, 'r', encoding='gbk') as f:
                return f.read()
        except:
            print(f"ERROR: Cannot decode file: {filepath}")
            return None

def batch_files(files, max_size=800000):
    """Split files into batches by total content size."""
    batches = []
    current_batch = []
    current_size = 0
    
    for f in files:
        content = read_file_content(f)
        if content is None:
            continue
        fsize = len(content.encode('utf-8'))
        if current_size + fsize > max_size and current_batch:
            batches.append(current_batch)
            current_batch = []
            current_size = 0
        current_batch.append({"path": f, "content": content})
        current_size += fsize
    
    if current_batch:
        batches.append(current_batch)
    
    return batches

if __name__ == "__main__":
    batches = batch_files(ALL_FILES)
    print(f"Total files: {len(ALL_FILES)}")
    print(f"Total batches: {len(batches)}")
    for i, batch in enumerate(batches):
        total_size = sum(len(f["content"].encode('utf-8')) for f in batch)
        print(f"  Batch {i+1}: {len(batch)} files, {total_size/1024:.1f} KB")
    
    # Write batch data as JSON for later use
    output_dir = os.path.join(BASE_DIR, ".github_push_batches")
    os.makedirs(output_dir, exist_ok=True)
    for i, batch in enumerate(batches):
        outpath = os.path.join(output_dir, f"batch_{i+1}.json")
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(batch, f, ensure_ascii=False)
        print(f"  Written: {outpath}")
