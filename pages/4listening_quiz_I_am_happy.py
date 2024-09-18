import streamlit as st
from openai import OpenAI
import random
import base64

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets["openai_api_key"])

def generate_question():
    prompt = """초등학생 수준의 간단한 영어 대화를 생성해주세요. 그 후 대화 내용에 관한 객관식 질문을 한국어로 만들어주세요.
    형식:
    [영어 대화]
    A: ...
    B: ...
    A: ...
    B: ...

    [한국어 질문]
    질문: (한국어로 된 질문) 예시: 대화를 듣고 오늘의 날씨가 어떤지 골라보세요.
    A. (선택지)
    B. (선택지)
    C. (선택지)
    D. (선택지)
    정답: (정답 선택지)
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

def text_to_speech(text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    
    audio_bytes = response.content
    
    audio_base64 = base64.b64encode(audio_bytes).decode()
    audio_tag = f'<audio controls><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
    
    return audio_tag

st.title("초등학생 영어 듣기 문제 생성기")

# 세션 상태 초기화
if 'question_generated' not in st.session_state:
    st.session_state.question_generated = False

if st.button("새 문제 생성"):
    full_content = generate_question()
    
    dialogue, question_part = full_content.split("[한국어 질문]")
    
    question_lines = question_part.strip().split("\n")
    question = question_lines[0].replace("질문:", "").strip()
    options = question_lines[1:5]
    correct_answer = question_lines[5].replace("정답:", "").strip()
    
    st.session_state.question = question
    st.session_state.dialogue = dialogue.strip()
    st.session_state.options = options
    st.session_state.correct_answer = correct_answer
    st.session_state.question_generated = True

if st.session_state.question_generated:
    st.markdown("### 질문")
    st.write(st.session_state.question)
    
    audio_tag = text_to_speech(st.session_state.dialogue)
    st.markdown(audio_tag, unsafe_allow_html=True)
    
    st.markdown("### 대화")
    st.text(st.session_state.dialogue)
    
    with st.form(key='answer_form'):
        selected_option = st.radio("정답을 선택하세요:", st.session_state.options, index=None)
        submit_button = st.form_submit_button(label='정답 확인')
        
        if submit_button:
            if selected_option:
                st.info(f"선택한 답: {selected_option}")
                #st.info(f"정답: {st.session_state.correct_answer}")  # 정답 출력
                # 공백 제거 후 비교
                if selected_option.strip() == st.session_state.correct_answer.strip():  
                    st.success("정답입니다!")
                else:
                    st.error(f"틀렸습니다. 정답은 {st.session_state.correct_answer}입니다.")
            else:
                st.warning("답을 선택해주세요.")
