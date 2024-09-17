import streamlit as st
from openai import OpenAI
import os
import re
import random

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets["openai_api_key"])

def generate_question():
    answer1 = random.choice([" I went to the history museum.", "I played badminton.", 
                             " I watched a movie."," I went to the space center."," I made a car.","I went fishing.","I went shopping","I went to the park.","I went to the library.","I went to the museum.",
                             "I played soccer","I played basketball", "I played baseball","I played tennis"])       
    key_expression = (f'''
    A:What did you do yesterday?
    B:{answer1}
    A:What did you do there?
    B:I learned about Korean history
    ''')
    prompt = f"""
    {key_expression}을 이용하여CEFR A1 수준의 영어 지문을 4-6문장으로 작성해주세요. 
    그 다음, 지문에 관한 간단한 질문을 한국어로 만들어주세요. 
    마지막으로, 질문에 대한 4개의 선택지를 한국어로 제공해주세요. 
    정답은 선택지 중 하나여야 합니다.
    출력 형식:
    지문: (영어 지문)
    질문: (한국어 질문)
    선택지:
    1. (선택지 1)
    2. (선택지 2)
    3. (선택지 3)
    4. (선택지 4)
    정답: (정답 번호)
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

def parse_question_data(data):
    lines = data.split('\n')
    passage = ""
    question = ""
    options = []
    correct_answer = None

    for line in lines:
        if line.startswith("지문:"):
            passage = line.replace("지문:", "").strip()
        elif line.startswith("질문:"):
            question = line.replace("질문:", "").strip()
        elif re.match(r'^\d+\.', line):
            options.append(line.strip())
        elif line.startswith("정답:"):
            correct_answer = line.replace("정답:", "").strip()

    # 정답을 숫자로 변환
    if correct_answer:
        correct_answer = int(re.search(r'\d+', correct_answer).group())

    return passage, question, options, correct_answer

def main():
    st.title("영어 문제 생성기")

    # 세션 상태 초기화
    if 'question_data' not in st.session_state:
        st.session_state.question_data = None
        st.session_state.selected_option = None
        st.session_state.show_answer = False

    if st.button("새로운 문제 생성"):
        st.session_state.question_data = generate_question()
        st.session_state.selected_option = None
        st.session_state.show_answer = False

    if st.session_state.question_data:
        # 문제 데이터 파싱
        passage, question, options, correct_answer = parse_question_data(st.session_state.question_data)

        st.subheader("영어 지문")
        st.write(passage)

        st.subheader("질문")
        st.write(question)

        st.subheader("선택지")
        for i, option in enumerate(options, 1):
            if st.checkbox(option, key=f"option_{i}", value=st.session_state.selected_option == i):
                st.session_state.selected_option = i

        if submit_button:
            if selected_option:
                st.info(f"선택한 답: {selected_option}")
                if selected_option.strip() == st.session_state.correct_answer.strip():  
                    st.success("정답입니다!")
                else:
                    st.error(f"틀렸습니다. 정답은 {st.session_state.correct_answer}입니다.")
            
            # 오답 풀이 추가
                    explanation_response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "당신은 초등학생을 위한 영어 학습 도우미입니다."},
                            {"role": "user", "content": f"다음 대화와 질문에 대해 {st.session_state.correct_answer}가 정답인 이유를 초등학생이 이해할 수 있게 한국어로 간단히 설명해주세요:\n\n대화:\n{st.session_state.dialogue}\n\n질문:\n{st.session_state.question}"}
                        ]
                    )
                    explanation = explanation_response.choices[0].message.content
                    st.markdown("### 오답 풀이")
                    st.write(explanation)
            else:
                st.warning("답을 선택해주세요.")
