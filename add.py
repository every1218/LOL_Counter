import re
import json
import sys

def parse_champion_descriptions(raw_text):
    """
    "이름 : 설명" 형식의 여러 문단 텍스트를
    [{"name": "...", "reason": "..."}, ...] JSON 리스트로 변환합니다.
    """
    
    # 1. 각 챔피언 항목을 분리합니다.
    entries = re.split(r'\n(?=\s*[가-힣A-Z\s]+?\s*:)', raw_text.strip())
    
    champion_list = []
    
    for entry in entries:
        if not entry.strip():
            continue
            
        # 2. 각 항목을 "이름"과 "설명"으로 분리합니다.
        parts = entry.split(':', 1)
        
        if len(parts) == 2:
            # 3. 이름과 설명에서 공백 제거
            name = parts[0].strip()
            reason = parts[1].strip()
            
            # 4. 설명(reason)에서 각주 번호([47] 등) 제거
            reason = re.sub(r'\[\d+\]', '', reason).strip()
            
            # 5. 리스트에 딕셔너리 형태로 추가
            champion_list.append({"name": name, "reason": reason})
        else:
            print(f"⚠️ 경고: 다음 항목은 '이름 : 설명' 형식이 아닙니다. 건너뜁니다.\n{entry[:50]}...", file=sys.stderr)
            
    return champion_list

# --- 4. 메인 실행 함수 ---
def main():
    
    # ⭐️⭐️⭐️⭐️⭐️
    # 1. 여기에 위키에서 복사한 "기타" 섹션 등의 텍스트를 붙여넣기
    RAW_TEXT_INPUT = """
다르킨학살자 케인 : 케인의 로그인 화면에서도 다르킨 학살자가 사이온의 몸을 찢고 나올 정도로 공인된 카운터다. 다르킨 케인의 주력기인 q스킬은 최대 체력 비례 피해라서 사이온과 싸움을 좀 길게 하다 보면 순식간에 사이온의 체력을 거덜내버리며, 그만큼 사이온이 cs를 파밍하고 체력을 높히며 성장을 하면 할 수록 다르킨 케인에게 얻어맞는 피해량도 엄청나게 증가한다. 일단 기본적으로 케인은 정글로 가기 때문에 사이온과 맞라인전을 할 일이 없으며, 몸이 약한데다 뚜벅이인 초반 사이온은 케인에게 정수 모으기 딱 좋은 챔피언이여서 초반엔 갱킹 압박에 시달리고 후반엔 다르킨으로 변신한 케인에게 포션으로 전락해버린다. 붙으면 무조건 지기 때문에 다가오지 못하게 막아야하지만 접근기가 2개나 있고 일단 접근을 허용하면 궁을 쓰지 않는 이상 도망도 못 친다.
애니비아 : 주 라인이 서로 달라 만날 일은 드물지만 미드 사이온을 골랐을 때 애니비아가 후픽으로 나온다면 마음 편히 닷지하자. 벽과 기절로 대량 학살 강타가 끊기는데다 6렙 이후에는 리그 오브 레전드 최강의 푸시력으로 미드 타워에 라인을 박아넣는다. 만약 애니비아가 블루를 받았다면 미니언을 먹으려는 사이온에게 무한 디나이를 시전할 수 있다. 더 큰 문제는 소규모 교전과 한타인데, 사이온의 핵심 스킬인 멈출 수 없는 맹공이 지형 생성 스킬인 결정화에 완벽하게 카운터당한다. 당연히 궁극기와 일반 스킬을 교환한 꼴로 사이온이 손해이며 벽에 박힌 사이온은 점멸이 없다면 상대팀의 집중포화에 무조건 죽어야 한다.
    """
    # ⭐️⭐️⭐️⭐️⭐️
    
    print("--- 텍스트 파싱 시작 ---")
    
    # 2. 파싱 실행
    parsed_data = parse_champion_descriptions(RAW_TEXT_INPUT)

    print("--- 파싱 완료 (줄바꿈 없이 한 줄로 출력) ---")
    
    # 3. ⭐️ 수정된 출력 로직
    # print() 함수의 'end' 파라미터를 ''로 설정하여 줄바꿈을 방지
    for item in parsed_data:
        json_line = json.dumps(item, ensure_ascii=False)
        
        # 콤마를 붙여서 출력하되, 줄바꿈(end='\n') 대신 빈 문자열(end='')을 사용
        print(json_line + ",", end="") # <-- 여기가 핵심!
    
    # 마지막에만 줄바꿈을 한 번 실행 (터미널 프롬프트가 붙는 것 방지)
    print()


if __name__ == '__main__':
    main()