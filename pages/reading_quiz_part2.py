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
    B:........
    ''')
    prompt = f"""
    {key_expression}을 이용하여CEFR A1 수준의 영어 지문을 4-6문장으로 작성해주세요. 
    그 다음, 지문에 관한 간단한 질문을 한국어로 만들어주세요. 
    질문을 만들 때, 지문에 맞는 화자를 포함해서 질문해 주세요. 예를 들어, 화자가 I면 "내가...", 화자가 Tom이면 "톰이..." 로 시작하는 질문을 생성해 주세요. A가 또는 B가로 시작하는 말은 하지마세요.
    마지막으로, 질문에 대한 4개의 선택지를 한국어로 제공해주세요. 
    정답은 선택지 중 하나여야 합니다.
    출력 형식:
    질문: (한국어 질문)
    지문: (영어 지문)
    선택지:
    1. (선택지 1)
    2. (선택지 2)
    3. (선택지 3)
    4. (선택지 4)
    정답: (정답 번호)
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content" : "너는 EFL 환경의 초등학교 영어교사야. 초등학생에 맞는 쉬운 한국어와 영어를 사용해."},
            {"role": "user", "content": prompt}]
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

def explain_wrong_answer(passage, question, user_answer, correct_answer):
    prompt = f"""
    지문: {passage}
    질문: {question}
    사용자의 답변: {user_answer}
    정답: {correct_answer}

    위 정보를 바탕으로, 사용자가 왜 틀렸는지 간단히 설명해주세요. 그리고 정답이 왜 맞는지도 설명해주세요.
    답변은 한국어로 작성해주세요.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

def main():
    # Streamlit UI

    # 메인 화면 구성
    st.header("✨인공지능 영어 퀴즈 선생님 퀴즐링👱🏾‍♂️")
    st.markdown("**❓어제 한 일에 대한 읽기 퀴즈**")
    st.divider()

    #확장 설명
    with st.expander("❗❗ 글상자를 펼쳐 사용방법을 읽어보세요 👆✅", expanded=False):
        st.markdown(
    """     
    1️⃣ [새 문제 만들기] 버튼을 눌러 문제 만들기.<br>
    2️⃣ 질문과 대화를 읽어보기<br> 
    3️⃣ 정답을 선택하고 [정답 확인] 버튼 누르기.<br>
    4️⃣ 정답 확인하기.<br>
    <br>
    🙏 퀴즐링은 완벽하지 않을 수 있어요.<br> 
    🙏 그럴 때에는 [새 문제 만들기] 버튼을 눌러주세요.
    """
    ,  unsafe_allow_html=True)

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

        st.subheader("질문")
        st.write(question)

        st.divider()
        st.write(passage)

        
        st.subheader("다음 중 알맞은 답을 골라보세요.")
        for i, option in enumerate(options, 1):
            if st.checkbox(option, key=f"option_{i}", value=st.session_state.selected_option == i):
                st.session_state.selected_option = i

        if st.button("정답 확인"):
            st.session_state.show_answer = True

        if st.session_state.show_answer:
            if st.session_state.selected_option is not None:
                if st.session_state.selected_option == correct_answer:
                    st.success("정답입니다!")
                else:
                    st.error(f"틀렸습니다. 정답은 {correct_answer}번입니다.")
                    explanation = explain_wrong_answer(
                        passage, 
                        question, 
                        options[st.session_state.selected_option - 1], 
                        options[correct_answer - 1]
                    )
                    st.write("오답 설명:", explanation)
            else:
                st.warning("선택지를 선택해주세요.")

if __name__ == "__main__":
    main()
