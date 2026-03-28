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
        # ⭐️ 이름 패턴에 &와 콤마(,) 문자 추가 ⭐️
        r'([가-힣A-Za-z\s()（）&,]+?)\s*:\s*(.*?)(?=\n[가-힣A-Za-z\s()（）&,]+?\s*:|\Z)', 
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

소나 : 체급이 워낙 구리고 거의 안 나오는 챔프라 대부분이 모르지만 서로 운용법을 안다 가정하고 라인전만 본다면 블리츠크랭크, 자이라 급의 하드카운터다. 소나 입장에서는 최악의 약점인 물몸 문제는 맞딜을 안해주면서 짤짤이만 넣으면 그만이고 6렙 이후에는 거리조절하면서 궁으로 아웃복싱만 해줘도 룰루쪽이 알아서 말라 죽는다. 후반으로 가도 소나의 무지막지한 후반 한타 기여도 때문에 룰루쪽시 밀리는데, 아무리 룰루가 맞딜이 더 좋다한들 소나를 단독으로 말리기는 매우 어렵고 갱호응기는 사거리가 소나 q보다 200 정도 짧은 변이와 맞히기 다소 어려운 둔화 Q, 그리고 초근접 시에만 에어본이 되는 궁극기밖에 없다. 결국 갱으로도 말리기 어렵다는 게 문제. 그렇기에 소나쪽이 맞딜을 자제하고 변이 각만 안주면서 성장을 도모하고 한타 위주의 운영을 하면 원체 한타가 다른 유틸폿에 비해 취약한 룰루인데 정면 한타구도에선 웬만한 라이너도 능가하는 기여도를 지닌 소나를 이길 수 없게 된다. 소나를 정 말리려면 라인전에선 원딜 상성이 유리하단 전제하에 아군 원딜이 싸움을 열어서 맞딜을 강제해야 하며 그것도 안 된다면 룰루 쪽이 좀 더 유리한 스플릿 운영을 유도해야 한다.

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