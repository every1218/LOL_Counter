import streamlit as st
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# LLM 초기화
try:
    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)
except Exception as e:
    st.error(f"LLM을 초기화하는 중 오류가 발생했습니다: {e}")
    llm = None

# 데이터 로드 함수 (캐싱 사용)
# ⭐️ 딕셔너리로 로드하도록 수정 (빠른 검색을 위해)
@st.cache_data
def load_champion_data(file_path):
    """JSONL 파일에서 챔피언 데이터를 딕셔너리로 로드하고 인덱싱합니다."""
    champion_dict = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                # 챔피언 이름을 키로, 데이터를 값으로 저장
                champion_dict[data['champion']] = data
                
                # 별칭(alias_of)이 있는 경우, 원본 데이터를 참조하도록 추가
                if 'alias_of' in data and data['alias_of'] in champion_dict:
                    champion_dict[data['champion']] = champion_dict[data['alias_of']]
                    
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.error(f"오류: '{file_path}' 파일을 읽을 수 없습니다. ({e})")
        return {} # 빈 딕셔너리 반환
    return champion_dict

def format_hard_counters(counters):
    """하드 카운터 목록의 형식을 지정합니다."""
    if not counters:
        return "정보 없음"
    return "\n".join([f"  - **{counter.get('name', 'N/A')}**: {counter.get('reason', 'N/A')}" for counter in counters])

def format_general_counters(counters):
    """일반 카운터 목록의 형식을 지정합니다."""
    if not counters:
        return "정보 없음"
    return ", ".join([f"**{counter}**" for counter in counters])

def main():
    """Streamlit 웹 앱의 메인 함수입니다."""
    st.title("👑 LOL 챔피언 카운터 챗봇 👑")

    # 데이터 로드 (딕셔너리)
    champion_data_store = load_champion_data('champ.jsonl')

    if not champion_data_store:
        st.warning("챔피언 데이터가 없습니다. 'champ.jsonl' 파일을 확인해주세요.")
        return

    # ⭐️ 1. st.form 생성
    with st.form(key="champion_form"):
        # ⭐️ 2. 텍스트 입력을 form 안에 배치
        champion_name_query = st.text_input("카운터 정보를 알고 싶은 챔피언 이름을 입력하세요(ex 이렐리아)", "")
        
        # ⭐️ 3. st.button을 st.form_submit_button으로 변경
        submit_button = st.form_submit_button("분석하기")

    # ⭐️ 4. if 조건문을 submit_button 변수로 변경
    if submit_button and llm:
        if champion_name_query:
            # ⭐️ 5. 데이터 조회 (딕셔너리 .get() 사용으로 변경)
            found_data = champion_data_store.get(champion_name_query)

            if not found_data:
                st.error(f"'{champion_name_query}'에 대한 데이터를 찾을 수 없습니다. 챔피언 이름을 다시 확인해주세요.")
                return # ⭐️ return으로 변경 (st.stop() 대신)

            with st.spinner('AI가 카운터 전략을 분석 중입니다...'):
                # 프롬프트 엔지니어링
                hard_counters_str = format_hard_counters(found_data.get('hard_counters', []))
                general_counters_str = format_general_counters(found_data.get('general_counters', []))

                # ChatPromptTemplate을 사용하여 메시지 목록 생성
                prompt = ChatPromptTemplate.from_messages(
                    [
                        ("system", "You are a helpful assistant who is an expert on the game League of Legends."),
                        ("user", """너는 리그 오브 레전드 전문가야. 아래 [데이터]를 참고해서 다음 [출력 형식]에 맞춰 답변해줘.

[출력 형식]
### 💀 하드 카운터
{hard_counters}

---

### 🔥 일반 카운터
{general_counters}                 
""")
                    ]
                )

                input_data = {
                    'champion_name': found_data['champion'],
                    'hard_counters': hard_counters_str, # "정보 없음" 처리는 포맷 함수가 하도록 수정
                    'general_counters': general_counters_str # "정보 없음" 처리는 포맷 함수가 하도록 수정
                }

                # LLM 체인 구성 및 실행
                chain = prompt | llm | StrOutputParser()
                
                # 스트리밍 응답을 화면에 출력
                st.subheader(f"🤖 AI의 {found_data['champion']} 카운터 분석 결과")
                st.write_stream(chain.stream(input_data))
        else:
            st.warning("챔피언 이름을 입력해주세요.")

if __name__ == "__main__":
    main()