"""Read all project files and create TAPD Wiki pages via API data preparation."""
import os
import json

BASE_DIR = r"C:\Users\Administrator\WorkBuddy\2026-05-11-task-2"
PARENT_WIKI_ID = "1146744119001000010"
WORKSPACE_ID = 46744119
CREATOR = "蓝海"

# Define wiki pages to create
WIKI_PAGES = [
    {
        "name": "PRD 产品需求文档",
        "file": "PRD-算电协同平台-Phase1.md",
    },
    {
        "name": "架构设计文档",
        "file": "Architecture-算电协同平台-Phase1.md",
    },
    {
        "name": "测试报告",
        "file": "TestReport-算电协同平台-Phase1.md",
    },
    {
        "name": "验收报告",
        "file": "VerificationReport-Phase1.md",
    },
    {
        "name": "交付报告",
        "file": "DeliveryReport-Phase1-Final.md",
    },
]

# Read file content
for page in WIKI_PAGES:
    filepath = os.path.join(BASE_DIR, page["file"])
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        page["content"] = content
        page["size"] = len(content)
        print(f"✅ {page['name']}: {page['size']:,} chars ({page['file']})")
    else:
        page["content"] = f"# {page['name']}\n\n文件未找到: {page['file']}"
        page["size"] = 0
        print(f"❌ {page['name']}: file not found")

# Save for use
output = {
    "workspace_id": WORKSPACE_ID,
    "parent_wiki_id": PARENT_WIKI_ID,
    "creator": CREATOR,
    "pages": WIKI_PAGES
}
outpath = os.path.join(BASE_DIR, ".github_push_batches", "tapd_wiki_pages.json")
with open(outpath, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False)
print(f"\nSaved to: {outpath}")
