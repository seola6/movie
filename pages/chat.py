import time
import streamlit as st
from openai import OpenAI

# =========================
# 페이지 기본 설정
# =========================
st.set_page_config(
    page_title="앙칼진 아기 고양이 양아치 선배",
    page_icon="🐱",
)

# =========================
# Gemini API 설정
# =========================
# Streamlit Secrets에서 API 키 가져오기
# .streamlit/secrets.toml 에 저장된 값을 사용
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.info("비밀 금고에 GEMINI_API_KEY가 설정되지 않았어.")
    st.stop()

# OpenAI 라이브러리로 Gemini 연결
client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# =========================
# AI 성격 설정
# =========================
SYSTEM_PROMPT = """
너는 중고등학생에게 앙칼지고 까칠하지만 츤데레 같은 성격의 귀여운 아기 고양이 양아치 선배야.
말이 끝날때마다 마지막에 반드시 "흥." 을 붙여.
반드시 순수 한국어로만 답해.
영어, 일본어, 중국어, 기호 남용을 하지 마.
"""

# =========================
# 상단 프로필
# =========================

col1, col2 = st.columns([1, 4])

with col1:
    st.image(
        "/mnt/data/16e98dc7-a8fd-4e82-8e31-916657357f65.png",
        width=140,
    )

with col2:
    st.title("앙칼진 아기 고양이 양아치 선배")
    st.caption("까칠하지만 은근히 챙겨주는 고양이 선배")

st.divider()

# =========================
# 채팅 기록 저장
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# 이전 대화 출력
# =========================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================
# 사용자 입력
# =========================
user_input = st.chat_input("메시지를 입력해 봐")

if user_input:

    # 사용자 메시지 저장
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    # 사용자 말풍선 출력
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI 답변 생성
    with st.chat_message("assistant"):

        message_box = st.empty()

        try:
            # Gemini에 보낼 전체 대화 구성
            messages_for_api = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                }
            ]

            # 이전 대화까지 모두 전달
            for m in st.session_state.messages:
                messages_for_api.append(
                    {
                        "role": m["role"],
                        "content": m["content"],
                    }
                )

            # 스트리밍 응답 요청
            stream = client.chat.completions.create(
                model="gemini-3.5-flash-lite",
                messages=messages_for_api,
                stream=True,
            )

            full_response = ""

            # 실시간 출력
            for chunk in stream:

                try:
                    delta = chunk.choices[0].delta.content
                except Exception:
                    delta = None

                if delta:
                    full_response += delta
                    message_box.markdown(full_response + "▌")

            message_box.markdown(full_response)

            # 답변 저장
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response,
                }
            )

        except Exception:
            # 빨간 오류 대신 안내 문구만 표시
            message_box.markdown(
                "지금은 선배가 잠깐 자리를 비웠어. 잠시 후 다시 말 걸어 줘."
            )
