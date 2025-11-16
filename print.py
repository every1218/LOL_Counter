
import json
import sys

def load_champion_data(file_path):
    """JSONL 파일에서 챔피언 데이터를 로드합니다."""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def print_champion_info(champion_data):
    """챔피언 정보를 형식에 맞게 출력합니다."""
    print(f"## 챔피언: {champion_data['champion']}\n")
    
    print("### 하드 카운터")
    if champion_data['hard_counters']:
        for counter in champion_data['hard_counters']:
            print(f"- **{counter['name']}**: {counter['reason']}")
    else:
        print("- 정보 없음")
    
    print("\n---\n")
    
    print("### 일반 카운터")
    if champion_data['general_counters']:
        print(", ".join(champion_data['general_counters']))
    else:
        print("- 정보 없음")

def main():
    """메인 실행 함수입니다."""
    try:
        champion_data_store = load_champion_data('champ.jsonl')
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"오류: 'champ.jsonl' 파일을 읽을 수 없습니다. ({e})")
        return

    if not champion_data_store:
        print("오류: 'champ.jsonl' 파일에 데이터가 없습니다.")
        return

    # 인자가 없는 경우 마지막 챔피언 정보 출력
    if len(sys.argv) < 2:
        last_champion_data = champion_data_store[-1]
        print_champion_info(last_champion_data)
        return

    # 인자가 있는 경우 해당 챔피언 정보 검색 및 출력
    if len(sys.argv) == 2:
        champion_name_query = sys.argv[1] 
    if len(sys.argv) == 3:
        champion_name_query = sys.argv[1] + " " + sys.argv[2]

    found_data = None
    for champion_data in champion_data_store:
        if champion_data['champion'] == champion_name_query:
            found_data = champion_data
            break

    if not found_data:
        print(f"'{champion_name_query}'에 대한 데이터를 찾을 수 없습니다.")
        return

    print_champion_info(found_data)

if __name__ == "__main__":
    main()
