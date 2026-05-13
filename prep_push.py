import json

with open('.github_push_batches/sub_batch_1.json', 'r', encoding='utf-8') as f:
    batch = json.load(f)

# Write each file's content to a temp file for easy reading
for i, item in enumerate(batch):
    outpath = f'.github_push_batches/s1_f{i:02d}.txt'
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(item['content'])
    print(f"[s1_f{i:02d}] {item['path']}: {outpath}")

# Also write the full batch as a single JSON with proper format for push_files
push_data = {
    "owner": "sensorcloud",
    "repo": "workbuddy-auto",
    "branch": "main",
    "message": "feat: 算电协同产业互联网平台 Phase 1 - 后端代码与文档",
    "files": [{"path": item["path"], "content": item["content"]} for item in batch]
}
with open('.github_push_batches/push_1.json', 'w', encoding='utf-8') as f:
    json.dump(push_data, f, ensure_ascii=False)
print(f"\nPush data saved. Files count: {len(push_data['files'])}")
