import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="홍대병 있는 너를 위한 인기 없는 영화들!!",
    page_icon="🌈",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        -45deg,
        #ff0080,
        #7928ca,
        #0070f3,
        #00dfd8,
        #f5d300,
        #ff4d4d
    );
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
}

@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

.block {
    background: rgba(0,0,0,0.6);
    padding: 20px;
    border-radius: 20px;
    margin-bottom: 15px;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("🌈 홍대병 있는 너를 위한 인기 없는 영화들!!")
st.caption("대중은 외면했지만... 어쩌면 네 취향일지도")

movies = [
    ["플로우", "2025-03-19", 1200, 25000, 45],
    ["장손", "2024-09-11", 980, 18000, 32],
    ["숨", "2024-12-04", 750, 13000, 20],
    ["여름의 카메라", "2025-01-15", 620, 9500, 18],
    ["검은 강", "2025-02-08", 410, 7200, 11]
]

df = pd.DataFrame(
    movies,
    columns=[
        "영화명",
        "개봉일",
        "관객수",
        "누적관객",
        "스크린수"
    ]
)

best = df.iloc[-1]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("영화명", best["영화명"])

with col2:
    st.metric("관객수", f"{best['관객수']:,}")

with col3:
    st.metric("누적관객", f"{best['누적관객']:,}")

st.subheader("🎬 영화 전시관")

for _, row in df.iterrows():
    st.markdown(
        f"""
        <div class="block">
        <h3>{row['영화명']}</h3>
        <p>
        개봉일 : {row['개봉일']}<br>
        관객수 : {row['관객수']:,}명<br>
        누적관객 : {row['누적관객']:,}명<br>
        스크린수 : {row['스크린수']}개
        </p>
        <p><i>🦋 모두가 좋아하는 영화보다, 네가 좋아하는 영화가 더 중요할지도.</i></p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.subheader("📊 영화 목록")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
