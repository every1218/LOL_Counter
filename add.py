import re
import json
import sys

def parse_champion_descriptions(raw_text):
    """
    "이름 : 설명" 형식의 여러 문단 텍스트를
    [{"name": "...", "reason": "..."}, ...] JSON 리스트로 변환합니다.
    """
    
    # 1. 텍스트의 앞뒤 공백/줄바꿈 제거
    text_to_split = raw_text.strip()
    
    # 2. re.findall을 사용하여 (이름)과 (설명)을 직접 캡처
    #    - (이름 패턴) : (설명 패턴)
    #    - 설명은 다음 이름 패턴이 나오거나, 문자열 끝(\Z)이 나오기 전까지 모두 캡처 (re.DOTALL)
    pattern = re.compile(
        # 괄호 부분에 （） (전각 문자) 추가
        r'([가-힣A-Za-z\s()（）]+?)\s*:\s*(.*?)(?=\n[가-힣A-Za-z\s()（）]+?\s*:|\Z)', 
        re.DOTALL
    )
    
    matches = pattern.findall(text_to_split)
    
    champion_list = []
    
    # 3. 캡처된 (이름, 설명) 튜플을 순회
    for name_raw, reason_raw in matches:
        
        # 4. 이름과 설명에서 공백 제거
        name = name_raw.strip()
        reason = reason_raw.strip()
        
        if not name or not reason: # 둘 중 하나라도 비어있으면 건너뛰기
            continue
            
        # 5. 설명(reason)에서 각주 번호([47] 등) 제거
        reason = re.sub(r'\[\d+\]', '', reason).strip()
        
        # 6. 리스트에 딕셔너리 형태로 추가
        champion_list.append({"name": name, "reason": reason})
            
    return champion_list

# --- 4. 메인 실행 함수 ---
def main():
    
    # ⭐️⭐️⭐️⭐️⭐️
    # 1. 여기에 위키에서 복사한 "기타" 섹션 등의 텍스트를 붙여넣기
    RAW_TEXT_INPUT = """
아지르 : 하이머딩거와 마찬가지로 소환수를 소환하여 딜을 하는 챔피언인데 문제는 아지르의 소환수인 모래 병사들은 타겟팅 지정 불가 + 무적이다. 게다가미드 메이지 챔피언 중에서 사거리까지 긴 편이라서 하이머딩거의 견제에 고통받을 일도 없다. 즉 똑같이 소환수를 소환하면 아지르는 하이머딩거의 사거리 밖에서 편안하게 모래 병사로 하이머딩거의 포탑들을 다 치울 수 있는 반면 하이머딩거는 아지르의 모래 병사를 처리할 방법이 전무하다. 때문에 극초반 푸시력부터 상대가 안 되며 템이 나오면 나올수록 모래 병사의 딜이 더 강해지기 때문에 포탑이 치워지는 속도 역시 더 빨라진다. 그나마 아지르의 마나 소모량이 커서 함부로 스킬들을 남발하지는 못하는 점이 있기는 하지만 이마저도 사실 아지르가 쓸데없이 스킬을 하이머딩거에게 꽂아넣지 않고 모래 병사로 하이머딩거의 포탑 치우기에만 집중하면 딱히 마나 소모량으로 고통받지도 않는다. 성장성도 아지르가 월등하게 높기 때문에 굉장히 골치 아픈 존재.
진(원딜): 상대 승률 20%에 이르는 바텀 하이머딩거 최악의 하드 카운터. 만나면 그냥 닷지하는 것을 추천한다. 진의 특성상 원거리에서 춤추는 유탄(Q)이나 살상연희(W)로 포킹하는 것이 대다수인데 하이머딩거는 근중거리에서 포탑으로 지속 딜을 넣는 챔피언이기에 진이 장거리에서 포탑을 부수기도 좋고 생존력이 떨어지는 하이머딩거는 6레벨 이후 W의 속박-커튼 콜(R) 연계 시 그냥 죽는다고 봐야 할 수준이다.


    """
    # ⭐️⭐️⭐️⭐️⭐️
    
    print("--- 텍스트 파싱 시작 ---")
    
    # 2. 파싱 실행
    parsed_data = parse_champion_descriptions(RAW_TEXT_INPUT)

    print("--- 파싱 완료 (줄바꿈 없이 한 줄로 출력) ---")
    
# 3. ⭐️ 수정된 출력 로직 (마지막 콤마 제거)
    for i, item in enumerate(parsed_data):
        json_line = json.dumps(item, ensure_ascii=False)
        print(json_line, end="") # 객체만 출력

        print(", ", end="")
            
    # 마지막에만 줄바꿈을 한 번 실행 (터미널 프롬프트가 붙는 것 방지)
    print()


if __name__ == '__main__':
    main()