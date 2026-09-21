```python
import streamlit as st
import pandas as pd
import requests
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# ==========================================================
# 페이지 설정
# ==========================================================
st.set_page_config(
    page_title="홍대병 있는 너를 위한 인기 없는 영화들!!",
    page_icon="🖤",
    layout="wide"
)

# ==========================================================
# 다크 감성 CSS
# ==========================================================
st.markdown("""
<style>

.stApp{
    background-color:#0d0d0d;
    color:#e6e6e6;
}

h1{
    text-align:center;
    color:white;
}

div[data-testid="stMetric"]{
    background:#1a1a1a;
    border:1px solid #333333;
    border-radius:15px;
    padding:10px;
}

.movie-card{
    background:#1a1a1a;
    border-left:4px solid #555555;
    border-radius:15px;
    padding:15px;
    margin-bottom:12px;
}

.comment{
    color:#bfbfbf;
    font-style:italic;
    margin-top:10px;
}

.small-text{
    color:#9a9a9a;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# 제목
# ==========================================================
st.title("🖤 홍대병 있는 너를 위한 인기 없는 영화들!!")
st.caption("어제 박스오피스 TOP10 중 사람들이 가장 덜 본 영화들을 모아봤습니다.")

# ==========================================================
# 영화 감성 문구
# ==========================================================
COMMENTS = [
    "🥀 대중은 지나쳤지만 누군가는 인생 영화라고 말합니다.",
    "🌙 이 영화를 본 사람보다 이 카드를 본 사람이 더 많을지도 모릅니다.",
    "🕯️ 흥행과 예술은 가끔 같은 길을 걷지 않습니다.",
    "🦇 관객보다 분위기가 먼저 도착한 영화.",
    "🌧️ 조용히 상영 중입니다.",
    "☁️ 세상의 관심을 살짝 비껴간 작품.",
    "🖤 모두가 찾는 영화는 아니지만 누군가에겐 특별할 수 있습니다.",
    "🌑 숫자로는 설명되지 않는 영화도 있습니다."
]

# ==========================================================
# 숫자 예쁘게 표시
# ==========================================================
def comma(value):
    try:
        return f"{int(value):,}"
    except:
        return value

# ==========================================================
# 한국 시간 기준 어제 계산
# ==========================================================
korea_now = datetime.now(ZoneInfo("Asia/Seoul"))
yesterday = korea_now - timedelta(days=1)

target_dt = yesterday.strftime("%Y%m%d")

st.info(
    f"조회일 : {yesterday.strftime('%Y-%m-%d')} (한국 시간 기준 어제)"
)

# ==========================================================
# KOBIS 조회 함수
# ==========================================================
@st.cache_data(ttl=3600)
def load_movies():

    api_key = st.secrets.get("KOBIS_KEY")

    if not api_key:
        raise ValueError(
            "Streamlit Secrets에 KOBIS_KEY가 없습니다."
        )

    url = (
        "https://www.kobis.or.kr/"
        "kobisopenapi/webservice/rest/"
        "boxoffice/searchDailyBoxOfficeList.json"
    )

    params = {
        "key": api_key,
        "targetDt": target_dt
    }

    response = requests.get(
        url,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    # KOBIS는 인증 오류도 200으로 응답함
    if "faultInfo" in data:

        message = (
            data["faultInfo"]
            .get("message", "인증 오류")
        )

        raise ValueError(
            f"KOBIS 오류 : {message}"
        )

    if "boxOfficeResult" not in data:
        raise ValueError(
            "boxOfficeResult가 존재하지 않습니다."
        )

    movies = (
        data["boxOfficeResult"]
        .get("dailyBoxOfficeList", [])
    )

    if len(movies) == 0:
        raise ValueError(
            "영화 목록이 비어 있습니다."
        )

    return movies

# ==========================================================
# 오류 안내
# ==========================================================
def show_help(error_message):

    st.error("데이터를 불러오지 못했습니다.")

    st.markdown(f"""
### 확인해 볼 사항

**오류 내용**

```

{error_message}

````

1. Streamlit Secrets에 KOBIS_KEY가 등록되어 있는지 확인
2. KOBIS 인증키가 올바른지 확인
3. KOBIS 서버가 정상 동작 중인지 확인
4. 해당 날짜 데이터가 아직 집계되지 않았는지 확인
5. 인터넷 연결 상태 확인

### Secrets 예시

```toml
KOBIS_KEY = "발급받은인증키"
````

""")

# ==========================================================

# 데이터 불러오기

# ==========================================================

try:

```
movies = load_movies()

df = pd.DataFrame(movies)

# 문자열 숫자를 숫자로 변환
for col in [
    "rank",
    "audiCnt",
    "audiAcc",
    "scrnCnt",
    "showCnt"
]:
    if col in df.columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

# ======================================================
# 관객수 적은 순 정렬
# ======================================================
df = df.sort_values(
    "audiCnt",
    ascending=True
).reset_index(drop=True)

# ======================================================
# 가장 인기 없는 영화
# ======================================================
least_movie = df.iloc[0]

st.subheader("🌑 어제 가장 조용했던 영화")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "영화명",
        least_movie["movieNm"]
    )

with c2:
    st.metric(
        "관객수",
        f"{int(least_movie['audiCnt']):,}명"
    )

with c3:
    st.metric(
        "누적관객",
        f"{int(least_movie['audiAcc']):,}명"
    )

st.divider()

# ======================================================
# 가장 인기 없는 TOP5 그래프
# ======================================================
st.subheader("📉 가장 덜 본 영화 TOP 5")

chart_df = (
    df.head(5)
    .set_index("movieNm")
)

st.bar_chart(chart_df["audiCnt"])

st.divider()

# ======================================================
# 영화 카드
# ======================================================
st.subheader("🖤 인기 없는 영화 전시관")

for _, row in df.iterrows():

    comment = random.choice(COMMENTS)

    st.markdown(
        f"""
        <div class="movie-card">

        <h4>{row['movieNm']}</h4>

        <div class="small-text">
        개봉일 : {row['openDt']}<br>
        관객수 : {int(row['audiCnt']):,}명<br>
        누적관객 : {int(row['audiAcc']):,}명<br>
        스크린수 : {int(row['scrnCnt']):,}개
        </div>

        <p class="comment">
        {comment}
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

# ======================================================
# 표
# ======================================================
st.subheader("📋 전체 목록")

table_df = pd.DataFrame({
    "순위": df["rank"],
    "영화명": df["movieNm"],
    "개봉일": df["openDt"],
    "관객수": df["audiCnt"].apply(comma),
    "누적관객": df["audiAcc"].apply(comma),
    "스크린수": df["scrnCnt"].apply(comma)
})

st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True
)
```

except Exception as e:

```
show_help(str(e))
```

````

`requirements.txt`

requests
tzdata

Streamlit Cloud의 **Secrets**에는 다음처럼 넣으면 돼.

```toml
KOBIS_KEY = "발급받은_KOBIS_인증키"
````

이 버전은 한국 시간 기준 어제 박스오피스를 가져와서 **관객 수가 적은 순으로 재정렬**하고, 검은 배경의 홍대병 감성 UI로 보여줘.
