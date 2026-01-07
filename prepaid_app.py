import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="선결제 장부 확인", page_icon="💳")

st.title("💳 선결제 잔액 조회")
st.markdown("---")

# 1. 구글 시트 데이터 연결 및 읽기
# ttl=0 옵션은 캐시를 남기지 않고 매번 새로고침하여 최신 데이터를 가져옵니다.
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# 데이터가 잘 읽혔는지 확인하기 위한 전처리 (날짜 형식 통일 등)
# 실제 시트의 컬럼명('날짜', '거래처', '잔액')에 맞춰 수정 필요
if '날짜' in df.columns:
    df['날짜'] = pd.to_datetime(df['날짜']).dt.strftime('%Y-%m-%d')

# 2. 거래처 목록 추출 (중복 제거)
# 시트에 있는 '거래처' 열에서 고유한 값들만 뽑아옵니다.
if '거래처' in df.columns:
    store_list = df['거래처'].unique().tolist()
else:
    store_list = []

# 3. 화면 구성: 거래처 선택 버튼
st.subheader("📋 선결제 내역 선택")

# 라디오 버튼이나 셀렉트박스로 거래처 선택
selected_store = st.radio(
    "확인할 거래처를 선택하세요:",
    store_list,
    index=0 if store_list else None
)

st.markdown("---")

# 4. 선택한 거래처의 최신 정보 조회 로직
if selected_store:
    # 해당 거래처 데이터만 필터링
    filtered_df = df[df['거래처'] == selected_store]
    
    if not filtered_df.empty:
        # 가장 마지막 행(=최신 내역) 가져오기
        latest_entry = filtered_df.iloc[-1]
        
        last_date = latest_entry['날짜']
        current_balance = latest_entry['잔액']
        
        # 결과 보여주기
        st.header(f"🏪 {selected_store}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="최근 갱신 날짜", value=str(last_date))
        with col2:
            # 잔액에 천단위 콤마 찍어서 보여주기
            st.metric(label="현재 잔액", value=f"{current_balance:,.0f} 원")
            
        # 상세 내역 (옵션: 펼쳐서 보기)
        with st.expander("지난 내역 보기"):
            st.dataframe(filtered_df.sort_index(ascending=False)) # 최신순 정렬
            
    else:
        st.warning("내역이 없습니다.")
else:
    st.info("데이터가 없거나 거래처를 불러올 수 없습니다.")