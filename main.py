python
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

# 한국 시간 기준 어제
yesterday = (
    datetime.now(ZoneInfo("Asia/Seoul"))
    - timedelta(days=1)
).strftime("%Y%m%d")

try:
    api_key = st.secrets["KOBIS_KEY"]

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

    df = pd.DataFrame(movies)

    # 숫자 변환
    for col in ["audiCnt", "audiAcc", "scrnCnt"]:
        df[col] = pd.to_numeric(df[col])

    # 관객수 적은 순
    df = df.sort_values("audiCnt")

    st.subheader("🌑 어제 가장 덜 본 영화")

    movie = df.iloc[0]

    col1, col2, col3 = st.columns(3)

    col1.metric("영화", movie["movieNm"])
    col2.metric("관객수", f"{movie['audiCnt']:,}")
    col3.metric("누적관객", f"{movie['audiAcc']:,}")

    st.subheader("📉 관객수 적은 순")

    st.dataframe(
        df[
            [
                "movieNm",
                "openDt",
                "audiCnt",
                "audiAcc",
                "scrnCnt"
            ]
        ],
        use_container_width=True
    )

except Exception as e:
    st.error("데이터를 불러오지 못했습니다.")
    st.write(e)
