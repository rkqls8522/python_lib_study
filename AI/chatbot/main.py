from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from time import time
from chat.gemini import process_gemini_request
from chat.schedule_api import router as schedule_router
from recommend.content_extractor import extract_main_content
from recommend.keyword_extractor import extract_keywords_yake
from recommend.google_search import google_search
from recommend.thumbnail_fetcher import get_thumbnails


# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 오리진 허용 (개발 중)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 스케줄 라우터 추가
app.include_router(schedule_router)

# Pydantic 모델 정의 (입력 데이터 검증)
class TextRequest(BaseModel):
    text: str

class URLRequest(BaseModel):
    url: str

class ChatMessage(BaseModel):
    userId: str
    message: str

# /chat 엔드포인트 추가 (기존 코드)
@app.post("/chat")
async def chat_endpoint(chat_message: ChatMessage):
    response = process_gemini_request(chat_message.userId, chat_message.message)
    return response

# /extract_keywords 엔드포인트 추가
@app.post("/extract_keywords")
async def extract_keywords_endpoint(data: TextRequest):
    text = data.text
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    
    top_keywords, elapsed_time = extract_keywords_yake(text)
    return JSONResponse(content={
        'yake': {
            'keywords': top_keywords,
            'execution_time': elapsed_time
        }
    })

# /recommend 엔드포인트 추가
@app.post("/recommend")
async def recommend(data: URLRequest):
    start_time = time()  # 시작 시간 기록
    
    url = data.url
    if not url:
        raise HTTPException(status_code=400, detail="No url provided")
    
    # a. 본문 텍스트 추출
    extract_start_time = time()
    main_text = extract_main_content(url)
    extract_elapsed_time = time() - extract_start_time
    print(f"본문 텍스트 추출 소요 시간: {extract_elapsed_time:.2f}초")
    
    if not main_text:
        raise HTTPException(status_code=400, detail="Could not extract main content")

    # b. 키워드 추출
    keyword_start_time = time()
    top_keywords, _ = extract_keywords_yake(main_text)
    keyword_elapsed_time = time() - keyword_start_time
    print(f"키워드 추출 소요 시간: {keyword_elapsed_time:.2f}초")
    
    # c. 구글 검색 실행
    search_start_time = time()
    query = " AND ".join(top_keywords)
    search_results = google_search(query)
    search_elapsed_time = time() - search_start_time
    print(f"구글 검색 소요 시간: {search_elapsed_time:.2f}초")
    
    if not search_results:
        raise HTTPException(status_code=400, detail="No search results found")

    # d. 썸네일 이미지 가져오기
    thumbnail_start_time = time()
    result_urls = [item["link"] for item in search_results]
    thumbnails = await get_thumbnails(result_urls)  # 여기에서 await 사용
    thumbnail_elapsed_time = time() - thumbnail_start_time
    print(f"썸네일 이미지 가져오기 소요 시간: {thumbnail_elapsed_time:.2f}초")


    recommendations = []
    for idx, item in enumerate(search_results):
        recommendations.append({
            "title": item["title"],
            "link": item["link"],
            "thumbnail": thumbnails[idx] if idx < len(thumbnails) else ""
        })

    total_elapsed_time = time() - start_time
    print(f"전체 소요 시간: {total_elapsed_time:.2f}초")

    return JSONResponse(content={
        "keywords": top_keywords,
        "query": query,
        "recommendations": recommendations
    })


# FastAPI 앱 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
