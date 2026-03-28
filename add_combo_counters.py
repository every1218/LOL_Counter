import json

# 조합 카운터 데이터 (원본 표기 그대로 저장)
combo_counter_data = {
    "카르마":    ["(카이사|트타)&노틸"],
    "노틸러스":  ["시비르&딩거", "이즈&(브라움|레오나|딩거)"],
    "쓰레쉬":   ["시비르&딩거", "케틀&몰가"],
    "룰루":     ["(진|케틀|애쉬|바루스)&(자이라|제라스)", "(징크스|드븐|자야|케틀)&블츠", "(애쉬|닐라|미포|루시안)&소나"],
    "블리츠크랭크": ["(시비르|이즈)&딩거", "(이즈|트타)&(레오나|브라움)", "(사미라|칼리|트타)&알리"],
    "레오나":   ["(이즈|루시안)&브라움", "칼리&타릭"],
    "바드":     ["(자야|트타|케틀)&블츠", "(카이사|트타)&노틸"],
    "브라움":   ["(제리|유나라)&유미", "(아펠|징크스|제리)&룰루", "(이즈|시비르|케틀)&(바드|카르마)", "케틀&럭스"],
    "세라핀":   ["(징크스|드븐|자야|케틀)&블츠", "(진|바루스)&제라스"],
    "파이크":   ["(시비르|이즈)&딩거", "사미라&(노틸|알리|레오나)", "(바루스|애쉬)&소라카"],
    "제라스":   ["(징크스|드븐|자야|케틀)&블츠", "(카이사|트타)&노틸", "아무무&미포"],
}

# JSONL 읽기
file_path = "champ.jsonl"
lines = []
with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        data = json.loads(line)
        champ_name = data.get("champion", "")
        if champ_name in combo_counter_data:
            data["combo_counters"] = combo_counter_data[champ_name]
            print(f"✅ {champ_name} - combo_counters 추가됨")
        lines.append(data)

# JSONL 다시 쓰기
with open(file_path, "w", encoding="utf-8") as f:
    for data in lines:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

print("\n완료! champ.jsonl 업데이트됨")
