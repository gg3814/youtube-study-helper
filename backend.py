import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.document_loaders import YoutubeLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

app = FastAPI(title="YouTube Study Helper API (Gemini)")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 데이터 모델 ---
class VideoRequest(BaseModel):
    url: str

# --- LangChain 설정 ---

# [보안 핵심] 코드에 키를 적지 않고, 서버(Render)의 환경변수에서 가져옵니다.
api_key = os.environ.get("GOOGLE_API_KEY")

# 키가 없는 경우 에러 방지 (서버 로그용)
if not api_key:
    print("⚠️ 경고: GOOGLE_API_KEY 환경변수가 설정되지 않았습니다!")

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
    google_api_key=api_key
)

summary_prompt = PromptTemplate(
    input_variables=["transcript"],
    template="""
    다음 유튜브 영상의 자막 내용을 읽고, 핵심 내용을 3줄로 요약해줘.
    반드시 한국어로 답변해줘.
    
    자막 내용:
    {transcript}
    """
)

quiz_prompt = PromptTemplate(
    input_variables=["transcript"],
    template="""
    다음 유튜브 영상의 자막 내용을 바탕으로, 내용을 이해했는지 확인할 수 있는 OX 퀴즈 3문제를 만들어줘.
    정답과 해설도 같이 포함해줘.
    반드시 한국어로 답변해줘.
    
    형식:
    Q1. (문제)
    A1. (O/X) - (해설)
    
    자막 내용:
    {transcript}
    """
)

summary_chain = summary_prompt | llm | StrOutputParser()
quiz_chain = quiz_prompt | llm | StrOutputParser()

# --- 유틸리티 ---
def get_transcript(url: str):
    try:
        loader = YoutubeLoader.from_youtube_url(url, add_video_info=False, language=["ko", "en"])
        docs = loader.load()
        return docs[0].page_content
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"자막을 가져올 수 없습니다: {str(e)}")

# --- API ---
@app.get("/")
def read_root():
    # 접속 테스트용 메시지
    if api_key:
        return {"message": "Server is running securely! (Key Loaded)"}
    else:
        return {"message": "Server is running, but API Key is missing!"}

@app.post("/summarize")
def summarize_video(request: VideoRequest):
    if not api_key:
        raise HTTPException(status_code=500, detail="API Key가 설정되지 않았습니다.")
    transcript = get_transcript(request.url)
    safe_transcript = transcript[:10000] 
    result = summary_chain.invoke({"transcript": safe_transcript})
    return {"summary": result}

@app.post("/quiz")
def generate_quiz(request: VideoRequest):
    if not api_key:
        raise HTTPException(status_code=500, detail="API Key가 설정되지 않았습니다.")
    transcript = get_transcript(request.url)
    safe_transcript = transcript[:10000] 
    result = quiz_chain.invoke({"transcript": safe_transcript})
    return {"quiz": result}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)