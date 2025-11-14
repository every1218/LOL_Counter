import streamlit as st
import json
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
# (참고: Streamlit Community Cloud에 배포할 땐 .env 대신 Secrets를 써야 함)
load_dotenv()

# --- LLM 관련 라이브러리/초기화 코드 전부 삭제 ---
# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# llm = ChatOpenAI(...) # <-- 삭제

# 데이터 로드 함수 (캐싱 사용)
@st.cache_data
def load_champion_data(file_path):
    """JSONL 파일에서 챔피언 데이터를 로드합니다."""
    # ⭐️ 딕셔너리로 로드/인덱싱하는 게 훨씬 빠름!
    champion_dict = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                # 챔피언 이름을 키로, 데이터를 값으로 저장
                champion_dict[data['champion']] = data
                
                # ⭐️ 만약 'alias_of' 필드가 있다면, 별칭도 키로 추가
                if 'alias_of' in data and data['alias_of'] in champion_dict:
                    # 원본 데이터를 별칭 키에 연결
                    champion_dict[data['champion']] = champion_dict[data['alias_of']]
                    
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.error(f"오류: '{file_path}' 파일을 읽을 수 없습니다. ({e})")
        return {} # 리스트 대신 빈 딕셔너리 반환
        
    return champion_dict


def format_hard_counters(counters):
    """하드 카운터 목록의 형식을 지정합니다."""
    # counters가 리스트가 아니거나 비어있으면 빈 문자열 반환
    if not isinstance(counters, list) or not counters:
        return "정보 없음"
    return "\n".join([f"  - **{counter.get('name', 'N/A')}**: {counter.get('reason', 'N/A')}" for counter in counters])

def format_general_counters(counters):
    """일반 카운터 목록의 형식을 지정합니다."""
    if not isinstance(counters, list) or not counters:
        return "정보 없음"
    return ", ".join(counters)

def main():
    """Streamlit 웹 앱의 메인 함수입니다."""
    st.title("👑 LOL 챔피언 카운터 조회 👑") # AI 챗봇이 아니므로 제목 변경

    # 데이터 로드 (딕셔너리 형태로)
    champion_data_store = load_champion_data('top.jsonl')

    if not champion_data_store:
        st.warning("챔피언 데이터가 없습니다. 'top.jsonl' 파일을 확인해주세요.")
        return

    # 사용자 입력
    champion_name_query = st.text_input("카운터 정보를 알고 싶은 챔피언 이름을 입력하세요:", "")

    # ⭐️ '분석하기' 버튼 클릭 시 (LLM 체크 삭제)
    if st.button("조회하기"):
        if champion_name_query:
            
            # ⭐️ 딕셔너리에서 데이터 조회 (반복문 대신 .get() 사용)
            found_data = champion_data_store.get(champion_name_query)

            if not found_data:
                st.error(f"'{champion_name_query}'에 대한 데이터를 찾을 수 없습니다. 챔피언 이름(별칭 포함)을 다시 확인해주세요.")
                return

            # ⭐️ LLM 스피너 문구 변경
            with st.spinner('챔피언 카운터 정보를 조회 중입니다...'):
                
                # 1. 데이터 포맷팅
                hard_counters_str = format_hard_counters(found_data.get('hard_counters'))
                general_counters_str = format_general_counters(found_data.get('general_counters'))

                # 2. ⭐️ LLM 호출 대신, f-string으로 마크다운 텍스트 직접 생성
                output_markdown = f"""
                ### 💀 하드 카운터
                {hard_counters_str}

                ---

                ### 🔥 일반 카운터
                {general_counters_str}
                """
                
                # 3. ⭐️ LLM 관련 코드 (Prompt, chain, input_data) 모두 삭제

                # 4. ⭐️ st.write_stream 대신 st.markdown으로 결과 한 번에 출력
                st.markdown("---")
                st.subheader(f"📜 {found_data['champion']} 카운터 조회 결과")
                st.markdown(output_markdown)
                
        else:
            st.warning("챔피언 이름을 입력해주세요.")

if __name__ == "__main__":
    main()