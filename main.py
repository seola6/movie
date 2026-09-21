import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="홍대병 있는 너를 위한 인기 없는 영화들!!",
    page_icon="🖤",
    layout="wide"
)

st.title("🖤 홍대병 있는 너를 위한 인기 없는 영화들!!")
st.caption("어제 박스오피스 TOP 10 중 관객 수가 가장 적은 영화들")

try:
    # Streamlit Secrets에서 API 키 가져오기
    api_key = st.secrets["KOBIS_KEY"]

    # 한국 시간 기준 어제 날짜
    korea_now = datetime.now(ZoneInfo("Asia/Seoul"))
    yesterday = (korea_now - timedelta(days=1)).strftime("%Y%m%d")

    # KOBIS API 호출
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"

    response = requests.get(
        url,
        params={
            "key": api_key,
            "targetDt": yesterday
        },
        timeout=10
    )

    data = response.json()

    # 인증키 오류 확인
    if "faultInfo" in data:
        st.error("KOBIS 인증키를 확인해주세요.")
        st.stop()

    movies = data["boxOfficeResult"]["dailyBoxOfficeList"]

    if len(movies) == 0:
        st.error("박스오피스 데이터가 없습니다.")
        st.stop()

    # 데이터프레임 생성
    df = pd.DataFrame(movies)

    # 숫자형 변환
    for col in ["audiCnt", "audiAcc", "scrnCnt"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 관객 수 적은 순 정렬
    df = df.sort_values("audiCnt", ascending=True)

    # 가장 덜 본 영화
    movie = df.iloc[0]

    st.subheader("🌑 어제 가장 덜 본 영화")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("영화명", movie["movieNm"])

    with c2:
        st.metric("관객수", f"{int(movie['audiCnt']):,}명")

    with c3:
        st.metric("누적관객", f"{int(movie['audiAcc']):,}명")

    st.divider()

    st.subheader("📉 인기 없는 영화 순위")

    show_df = df[
        [
            "rank",
            "movieNm",
            "openDt",
            "audiCnt",
            "audiAcc",
            "scrnCnt"
        ]
    ].copy()

    show_df.columns = [
        "순위",
        "영화명",
        "개봉일",
        "관객수",
        "누적관객",
        "스크린수"
    ]

    st.dataframe(
        show_df,
        use_container_width=True,
        hide_index=True
    )

except Exception as e:
    st.error("오류가 발생했습니다.")
    st.write(str(e))
