import streamlit as st
import requests

st.set_page_config(page_title="유튜브 요약 & 퀴즈", page_icon="📚")

# ==========================================
# [배포 후 수정할 부분]
# Render에서 백엔드를 배포하면 "https://...onrender.com" 주소를 줍니다.
# 그 주소를 여기에 복사해서 붙여넣으세요.
# ==========================================
# BACKEND_URL = "http://localhost:8000"  # 로컬 테스트용
BACKEND_URL = "https://youtube-backend-bc2u.onrender.com" # 배포용 (예: https://my-app.onrender.com)

# 만약 주소를 아직 안 바꿨으면 경고
if "여기에" in BACKEND_URL:
    st.warning("⚠️ 아직 백엔드 주소가 설정되지 않았습니다. 로컬 테스트라면 코드를 수정해주세요.")
    BACKEND_URL = "http://localhost:8000"

st.title("📹 유튜브 AI 공부 도우미")
st.markdown("---")

# 사이드바
with st.sidebar:
    st.header("⚙️ 상태 확인")
    try:
        if requests.get(BACKEND_URL).status_code == 200:
            st.success("🟢 서버 연결됨")
        else:
            st.error("🔴 서버 연결 안됨")
    except:
         st.error("🔴 서버 연결 실패")

url = st.text_input("유튜브 URL을 입력하세요", placeholder="https://www.youtube.com/watch?v=...")

if url:
    st.video(url)
    tab1, tab2 = st.tabs(["📝 3줄 요약", "❓ OX 퀴즈"])

    with tab1:
        if st.button("요약하기"):
            with st.spinner("분석 중..."):
                try:
                    response = requests.post(f"{BACKEND_URL}/summarize", json={"url": url})
                    if response.status_code == 200:
                        st.success("완료!")
                        st.write(response.json()["summary"])
                    else:
                        st.error("오류 발생")
                except Exception as e:
                    st.error(f"에러: {e}")

    with tab2:
        if st.button("퀴즈 만들기"):
            with st.spinner("출제 중..."):
                try:
                    response = requests.post(f"{BACKEND_URL}/quiz", json={"url": url})
                    if response.status_code == 200:
                        st.success("완료!")
                        st.write(response.json()["quiz"])
                    else:
                        st.error("오류 발생")
                except Exception as e:
                    st.error(f"에러: {e}")