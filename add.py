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

자야 : 자야의 대표적인 카운터 격 되는 라인전 강캐로, 자야가 OP로 뜨던 시기에도 자야의 카운터 픽으로 종종 모습을 비췄을 정도이다.
애쉬 : 애쉬의 핵심인 궁을 맞궁으로 피할 수 있다는 건 장점이긴 하나 자야의 궁쿨은 애쉬보다도 길다. 또 기본적으로 라인전 능력에서 현저히 밀리고, 궁이 없더라도 지속적인 둔화와 사거리 차이 때문에 킬각은커녕 접근도 힘들다. 2022년부터 자주 나오는 서폿 애쉬는 원딜보다 훨씬 자주 W와 R을 날리기 때문에 원딜 애쉬 이상으로 강력한 카운터 픽이다.
진 : 사거리 차이가 극심한 데다가 후반 캐리력까지 뛰어나기 때문에 여러모로 대처하기 까다롭다. 대신 맞딜이 약하고 중반에 존재감이 떨어져 라인전을 꼭 이겨야만 하는 챔프인데, 자야 상대로는 그게 전혀 어렵지가 않다. 또한 궁극기 성능 차이가 심해서 궁극기 교환을 하게 된다면 자야만 손해를 보게 된다.

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