import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ------------------------------------------------------------
# 페이지 기본 설정 (제목, 아이콘, 레이아웃)
# ------------------------------------------------------------
st.set_page_config(
    page_title="주가 조회 앱",
    page_icon="📈",
    layout="centered",
)

# ------------------------------------------------------------
# 따뜻한 크림·노란색 톤을 위한 커스텀 CSS
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFF8E7;
    }
    div[data-testid="stMetric"] {
        background-color: #FFF3CD;
        border-radius: 16px;
        padding: 16px;
        border: 1px solid #FFE08A;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# 제목과 간단한 설명
# ------------------------------------------------------------
st.title("📈 내 손안의 주가 조회")
st.write(
    "종목 코드를 입력하면 최근 1년간의 주가 흐름을 그래프로 보여드려요. "
    "예: 삼성전자는 `005930.KS`, 애플은 `AAPL` 처럼 입력해 주세요 :)"
)

# ------------------------------------------------------------
# 종목 코드 입력창
# ------------------------------------------------------------
ticker_input = st.text_input(
    "종목 코드를 입력하세요",
    value="AAPL",
    placeholder="예: 005930.KS (삼성전자), AAPL (애플)",
)

# 조회 버튼 (누르면 아래 코드가 실행됨)
조회버튼 = st.button("조회하기")

# ------------------------------------------------------------
# 버튼을 누르거나 입력값이 있을 때 데이터 조회 시작
# ------------------------------------------------------------
if 조회버튼 and ticker_input:
    # 입력값 앞뒤 공백 제거 및 대문자로 변환 (yfinance는 대문자를 기준으로 함)
    ticker_symbol = ticker_input.strip().upper()

    with st.spinner("주가 데이터를 불러오는 중이에요..."):
        try:
            # 오늘 날짜와 1년 전 날짜 계산
            오늘 = datetime.today()
            일년전 = 오늘 - timedelta(days=365)

            # yfinance로 해당 종목의 티커 객체 생성
            stock = yf.Ticker(ticker_symbol)

            # 최근 1년치 일별 주가 데이터 가져오기
            history_df = stock.history(start=일년전, end=오늘)

            # 데이터가 비어있으면 잘못된 종목 코드일 가능성이 높음
            if history_df.empty:
                st.error(
                    "데이터를 찾을 수 없어요. 종목 코드를 다시 확인해 주세요. "
                    "(예: 005930.KS, AAPL)"
                )
            else:
                # 종목의 회사 이름 가져오기 (없으면 입력한 코드 그대로 사용)
                info = stock.info
                company_name = info.get("longName", ticker_symbol)

                # 현재가 = 가장 최근 종가
                현재가 = history_df["Close"].iloc[-1]
                # 1년 전 가격 = 가장 오래된 종가
                일년전가격 = history_df["Close"].iloc[0]
                # 등락률 계산 (%)
                등락률 = (현재가 - 일년전가격) / 일년전가격 * 100

                # 통화 단위 추정 (원화 종목은 KS/KQ로 끝남)
                통화단위 = "원" if ticker_symbol.endswith((".KS", ".KQ")) else "$"

                st.subheader(f"{company_name} ({ticker_symbol})")

                # ------------------------------------------------------------
                # 지표 카드 2개: 현재가 / 1년 등락률
                # ------------------------------------------------------------
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        label="현재가",
                        value=f"{현재가:,.2f} {통화단위}",
                    )
                with col2:
                    st.metric(
                        label="1년 등락률",
                        value=f"{등락률:+.2f}%",
                        delta=f"{등락률:+.2f}%",
                    )

                # ------------------------------------------------------------
                # plotly 꺾은선 그래프 그리기
                # ------------------------------------------------------------
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=history_df.index,
                        y=history_df["Close"],
                        mode="lines",
                        name="종가",
                        line=dict(color="#F4A300", width=2),
                    )
                )

                # 그래프 배경과 폰트 등을 따뜻한 톤으로 설정
                fig.update_layout(
                    title="최근 1년 주가 흐름",
                    xaxis_title="날짜",
                    yaxis_title=f"주가 ({통화단위})",
                    plot_bgcolor="#FFFDF5",
                    paper_bgcolor="#FFFDF5",
                    font=dict(color="#6D4C1B"),
                    hovermode="x unified",
                )

                st.plotly_chart(fig, use_container_width=True)

                st.caption(
                    "※ 본 데이터는 참고용이며, 실제 투자 판단은 신중하게 해주세요."
                )

        except Exception as e:
            # 예상치 못한 오류가 발생했을 때 사용자에게 안내
            st.error(f"오류가 발생했어요: {e}")

else:
    # 아직 조회 버튼을 누르지 않았을 때 보여줄 안내 문구
    st.info("종목 코드를 입력하고 '조회하기' 버튼을 눌러주세요 👆")
