import streamlit as st
import requests

st.set_page_config(page_title="유튜브 요약 & 퀴즈", page_icon="📚")

# ==========================================
# [중요] Render 백엔드 주소 (그대로 두세요)
# ==========================================
BACKEND_URL = "https://youtube-backend-bc2u.onrender.com"

st.title("📹 유튜브 AI 공부 도우미")
st.markdown("---")

url = st.text_input("유튜브 URL을 입력하세요", placeholder="https://www.youtube.com/watch?v=...")

if url:
    st.video(url)
    
    tab1, tab2 = st.tabs(["📝 3줄 요약", "❓ OX 퀴즈"])

    with tab1:
        if st.button("요약하기"):
            with st.spinner("AI가 영상을 분석 중입니다..."):
                try:
                    response = requests.post(f"{BACKEND_URL}/summarize", json={"url": url})
                    if response.status_code == 200:
                        st.success("완료!")
                        st.write(response.json()["summary"])
                    else:
                        # [수정] 왜 오류가 났는지 상세 메시지를 보여줍니다.
                        error_msg = response.json().get('detail', '알 수 없는 오류')
                        st.error(f"실패 원인: {error_msg}")
                except Exception as e:
                    st.error(f"서버 연결 실패: {e}")

    with tab2:
        if st.button("퀴즈 만들기"):
            with st.spinner("문제를 출제 중입니다..."):
                try:
                    response = requests.post(f"{BACKEND_URL}/quiz", json={"url": url})
                    if response.status_code == 200:
                        st.success("완료!")
                        st.write(response.json()["quiz"])
                    else:
                        # [수정] 상세 메시지 출력
                        error_msg = response.json().get('detail', '알 수 없는 오류')
                        st.error(f"실패 원인: {error_msg}")
                except Exception as e:
                    st.error(f"서버 연결 실패: {e}")

# 사이드바 상태 확인
with st.sidebar:
    st.header("⚙️ 상태 확인")
    try:
        if requests.get(BACKEND_URL, timeout=1).status_code == 200:
            st.success("🟢 AI 서버 연결됨")
        else:
            st.warning("🟡 서버 깨우는 중...")
    except:
         st.warning("🟡 서버 연결 시도 중...")
