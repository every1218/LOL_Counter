import requests
from bs4 import BeautifulSoup
import json
import re
import os
from dotenv import load_dotenv

# .env 파일 로드 (LLM 요약을 위해 필요)
load_dotenv()

# --- 0. 설정 및 상수 ---
NARU_URL = "https://namu.wiki/w/%EB%82%98%EB%A5%B4(%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C)"
CHAMPION_NAME = "나르"
TARGET_FILE = "top.json"
HARD_KEYWORDS = ["하드카운터", "극상성", "닷지", "최악의 상대", "매우 불리하다"] # 기획서 키워드 반영

# 임시 LLM 요약 함수 (실제는 LLM API 호출)
def summarize_reason_llm(long_text, champion):
    """실제 LLM API를 호출하여 긴 텍스트를 요약하는 함수 (현재는 더미)"""
    # 실제 환경에서는 여기서 ChatOpenAI 등을 사용해야 함
    if len(long_text) > 150:
        return f"[LLM 요약됨]: {champion}에게 불리한 이유: {long_text[:120]}... (텍스트가 길어 요약됨)"
    return f"[LLM 요약됨]: {long_text}"


# --- 1. 데이터 로드 및 저장 관리 함수 ---
def load_and_prepare_data(file_path):
    """
    기존 JSON 데이터를 로드합니다.
    파일이 없거나, 비어있거나, JSONL 형식이거나, 단일 객체인 경우를 모두 처리하여 리스트로 반환합니다.
    """
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            # 파일 전체를 하나의 JSON 리스트로 로드 시도
            data = json.load(f)
            if isinstance(data, list):
                return data
            return [data]  # 단일 객체인 경우 리스트로 감싸 반환
        except json.JSONDecodeError:
            # JSON 리스트 로드 실패 시, JSONL(줄바꿈으로 구분된 JSON 객체) 형식으로 처리
            f.seek(0)  # 파일 포인터를 처음으로 되돌림
            return [json.loads(line) for line in f if line.strip()]

def save_data(file_path, data_list):
    """
    수정된 리스트를 사용자가 원하는 '커스텀 포맷'으로 저장합니다.
    (hard_counters의 객체와 general_counters 리스트만 한 줄로 압축)
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('[\n') # 1. 전체 리스트 시작
        
        for i, champ_data in enumerate(data_list):
            f.write('  {\n') # 2. 챔피언 객체 시작 (들여쓰기 2)
            
            # 3. "champion" 키-값 쌍 (들여쓰기 4)
            f.write(f'    "champion": {json.dumps(champ_data["champion"], ensure_ascii=False)},\n')
            
            # 4. "hard_counters" 리스트 시작
            f.write('    "hard_counters": [\n')
            
            hard_counters = champ_data.get("hard_counters", [])
            for j, counter in enumerate(hard_counters):
                # ⭐️ 핵심: hard_counter 객체를 '한 줄로 압축' (indent=None)
                counter_line = json.dumps(counter, ensure_ascii=False)
                f.write(f'      {counter_line}') # (들여쓰기 6)
                
                if j < len(hard_counters) - 1:
                    f.write(',\n') # 리스트의 다음 항목을 위해 쉼표
                else:
                    f.write('\n') # 리스트의 마지막 항목
            
            f.write('    ],\n') # "hard_counters" 리스트 닫기
            
            # 5. "general_counters" 리스트를 '한 줄로 압축'
            gc_list_line = json.dumps(champ_data.get("general_counters", []), ensure_ascii=False)
            f.write(f'    "general_counters": {gc_list_line}\n') # 챔피언 객체의 마지막 항목이므로 쉼표 없음
            
            # 6. 챔피언 객체 닫기
            f.write('  }')
            if i < len(data_list) - 1:
                f.write(',\n') # 다음 챔피언 객체를 위해 쉼표
            else:
                f.write('\n') # 파일의 마지막 객체
        
        f.write(']\n') # 7. 전체 리스트 닫기

# --- 2. 각주 파싱 (1차) ---
def parse_footnotes(soup):
    """HTML에서 각주 섹션을 파싱하여 {번호: 텍스트} 맵을 생성"""
    footnote_map = {}
    footnote_container = soup.find('ol', class_='wiki-list-foot')
    
    if footnote_container:
        for li in footnote_container.find_all('li', id=re.compile(r'fn-')):
            fn_number = li['id'].replace('fn-', '')
            fn_text = li.get_text()
            # 불필요한 번호, 돌아가기 버튼(↩), 빈 공간 제거
            fn_text = re.sub(r'^\s*\d+\.\s*|\[\d+\]\s*|↩\s*|\s*\[\s*\]\s*$', '', fn_text).strip()
            footnote_map[fn_number] = fn_text
    return footnote_map

# --- 3. 본문 카운터 파싱 및 데이터 연결 (2차) ---
def parse_counters(soup, champion_name, footnote_map):
    """카운터 섹션을 찾아 챔피언 이름과 각주 텍스트를 연결 및 분류"""
    all_counters_data = []
    
    # '상대하기 힘든 챔피언' 텍스트를 찾아 콘텐츠 블록 탐색
    # 나르 페이지 기준: '상대하기 힘든 챔피언' 텍스트는 <span class="wiki-word-token"> 등에 있음
    difficult_section_text = soup.find(string=re.compile(r'상대하기 힘든 챔피언|카운터'))
    
    if not difficult_section_text:
        return None

    # 해당 텍스트를 포함하는 부모 컨테이너 찾기
    list_container = difficult_section_text.find_parent('div') 
    
    if not list_container:
        # 상위 div가 없으면 다른 구조를 가진 것으로 간주하고 더 넓게 탐색 가능 (생략)
        return None

    # 컨테이너 내의 모든 링크(챔피언 이름) 검색
    for link in list_container.find_all('a'):
        champion_name_text = link.get_text().strip()
        
        # 유효한 챔피언 이름만 필터링 (너무 짧거나 길지 않은 이름)
        if not champion_name_text or len(champion_name_text) > 10:
            continue
        
        # 각주 번호 추출 시도 (<a> 태그 옆의 <sup> 태그 확인)
        footnote_number = None
        sup_tag = link.find_next_sibling('sup')
        
        if sup_tag and sup_tag.find('a'):
            href = sup_tag.find('a').get('href', '')
            match = re.search(r'fn-(\d+)', href)
            if match:
                footnote_number = match.group(1)
        
        reason_text = footnote_map.get(footnote_number, "") # 각주 맵에서 이유 텍스트 가져옴

        # --- 4. 분류 및 요약 ---
        is_hard_counter = any(keyword in reason_text for keyword in HARD_KEYWORDS)
        
        if is_hard_counter:
            # LLM 요약 요청 (더미 함수 사용)
            summarized_reason = summarize_reason_llm(reason_text, champion_name_text)
            all_counters_data.append({
                'name': champion_name_text,
                'reason': summarized_reason,
                'type': 'hard'
            })
        else:
            all_counters_data.append({
                'name': champion_name_text,
                'type': 'general'
            })
            
    # 최종 JSON 구조로 정리
    hard_counters = [d for d in all_counters_data if d['type'] == 'hard']
    general_counters = [d['name'] for d in all_counters_data if d['type'] == 'general']
    
    return {
        "champion": champion_name,
        "hard_counters": hard_counters,
        "general_counters": general_counters
    }

# --- 메인 실행 함수 ---
def main():
    print(f"--- 챔피언 데이터 처리 시작: {CHAMPION_NAME} ---")
    
    # 1. 크롤링 (HTML 수집)
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(NARU_URL, headers=headers, timeout=10)
        response.raise_for_status() # HTTP 오류가 발생하면 예외 발생
    except requests.exceptions.RequestException as e:
        print(f"오류: 웹 페이지에 접속할 수 없습니다. {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # 2. 1차 파싱 (각주 맵 생성)
    footnote_map = parse_footnotes(soup)
    
    # 3. 2차 파싱 및 분류
    new_champion_data = parse_counters(soup, CHAMPION_NAME, footnote_map)

    if not new_champion_data:
        print(f"경고: {CHAMPION_NAME}의 카운터 섹션을 찾을 수 없거나 데이터가 비어있습니다.")
        return

    # 4. 데이터 로드, 업데이트 및 저장
    all_data_list = load_and_prepare_data(TARGET_FILE)
    
    # 기존 데이터에서 현재 챔피언 데이터를 업데이트하거나 새로 추가
    updated = False
    for i, data in enumerate(all_data_list):
        if data.get('champion') == CHAMPION_NAME:
            all_data_list[i] = new_champion_data
            updated = True
            break
            
    if not updated:
        all_data_list.append(new_champion_data)

    save_data(TARGET_FILE, all_data_list)
    print(f"성공: {CHAMPION_NAME} 데이터가 '{TARGET_FILE}' 파일에 저장(업데이트)되었습니다.")

if __name__ == '__main__':
    main()