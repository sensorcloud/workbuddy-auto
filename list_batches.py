import json
for bn in [1, 2, 3]:
    with open(f'.github_push_batches/sub_batch_{bn}.json', 'r', encoding='utf-8') as f:
        batch = json.load(f)
    print(f"\n=== Sub-batch {bn}: {len(batch)} files ===")
    for item in batch:
        print(f"  {item['path']} ({len(item['content']):,} chars)")
