import json
import sys
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
load_dotenv()

# LLM 초기화
llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)

# 데이터 로드 함수
def load_champion_data(file_path):
    """JSONL 파일에서 챔피언 데이터를 로드합니다."""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def format_hard_counters(counters):
    """하드 카운터 목록의 형식을 지정합니다."""
    return "\n".join([f"  - **{counter['name']}**: {counter['reason']}" for counter in counters])

def format_general_counters(counters):
    """일반 카운터 목록의 형식을 지정합니다."""
    return ", ".join(counters)

def main():
    """챗봇의 메인 실행 함수입니다."""
    # 1. 커맨드 라인에서 챔피언 이름 가져오기
    if len(sys.argv) < 2:
        print("사용법: python chat.py [챔피언 이름]")
        return

    champion_name_query = sys.argv[1]

    # 2. 데이터 로드
    try:
        champion_data_store = load_champion_data('champ.jsonl')
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"오류: 'champ.jsonl' 파일을 읽을 수 없습니다. ({e})")
        return

    # 3. 데이터 조회
    found_data = None
    for champion_data in champion_data_store:
        if champion_data['champion'] == champion_name_query:
            found_data = champion_data
            break

    if not found_data:
        print(f"'{champion_name_query}'에 대한 데이터를 찾을 수 없습니다.")
        return

    # 4. 프롬프트 엔지니어링
    hard_counters_str = format_hard_counters(found_data['hard_counters'])
    general_counters_str = format_general_counters(found_data['general_counters'])

    # ChatPromptTemplate을 사용하여 메시지 목록 생성
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant who is an expert on the game League of Legends."),
            ("user", """너는 리그 오브 레전드 전문가야. 아래 [데이터]를 참고해서 다음 [출력 형식]에 맞춰 답변해줘.

[출력 형식]
## 챔피언: {champion_name}

### 하드 카운터
{hard_counters}

---

### 일반 카운터
{general_counters}
""")
        ]
    )

    input_data = {
        'champion_name': found_data['champion'],
        'hard_counters': hard_counters_str,
        'general_counters': general_counters_str
    }


    # 5. LLM 체인 구성 및 실행
    chain = prompt | llm | StrOutputParser()
    
    # print(chain.invoke(input_data))

    for token in chain.stream(input_data):
        print(token, end="", flush=True)  #줄바꿈 없이 출력, 버퍼 즉시지움


if __name__ == "__main__":
    main()