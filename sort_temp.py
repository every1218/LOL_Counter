import json

# Read the data from champ.jsonl
with open('champ.jsonl', 'r', encoding='utf-8') as f:
    data = [json.loads(line) for line in f]

# Sort the data by the 'champion' key
sorted_data = sorted(data, key=lambda x: x['champion'])

# Write the sorted data back to champ.jsonl
with open('champ.jsonl', 'w', encoding='utf-8') as f:
    for item in sorted_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print("champ.jsonl 정렬 완료")
