from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from time import time
# from chat.gemini import process_gemini_request
# from chat.schedule_api import router as schedule_router
from recommend.content_extractor import extract_main_content
from recommend.google_search import google_search

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 오리진 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 스케줄 라우터 추가
# app.include_router(schedule_router)

# Pydantic 모델 정의 (입력 데이터 검증)
class TextRequest(BaseModel):
    text: str

class URLRequest(BaseModel):
    url: str

class ChatMessage(BaseModel):
    userId: str
    message: str

# /chat 엔드포인트 추가
@app.post("/chat")
async def chat_endpoint(chat_message: ChatMessage):
    response = process_gemini_request(chat_message.userId, chat_message.message)
    return response

# /recommendations 엔드포인트 추가
@app.post("/recommendations")
async def recommend(data: URLRequest):
    start_time = time()  # 시작 시간 기록
    
    url = data.url
    if not url:
        return JSONResponse(status_code=400, content={
            "status": {"code": "400", "message": "No url provided"},
            "content": {}
        })
    
    # a. 본문 텍스트 추출
    try:
        extract_start_time = time()
        main_text = extract_main_content(url)
        extract_elapsed_time = time() - extract_start_time
        print(f"본문 텍스트 추출 소요 시간: {extract_elapsed_time:.2f}초")
    except Exception as e:
        print("본문 텍스트 추출 중 오류:", e)
        return JSONResponse(status_code=500, content={
            "status": {"code": "500", "message": "본문 텍스트 추출 중 오류"},
            "content": {}
        })
    
    # 추출은 성공했으나 내용이 없는 경우
    if not main_text or main_text.strip() == "":
        return JSONResponse(status_code=200, content={
            "status": {"code": "200", "message": "추출할 본문이 없습니다"},
            "content": {}
        })
    
    # b. 키워드 추출 (상위 10개 키워드와 점수를 터미널에 출력하고, 상위 4개를 사용)
    try:
        from time import time as time_func  # 중복 사용 방지
        import yake
        keyword_start_time = time()
        kw_extractor = yake.KeywordExtractor(lan="en", n=1, top=10, dedupLim=0.3)
        all_keywords = kw_extractor.extract_keywords(main_text)
        sorted_keywords = sorted(all_keywords, key=lambda x: x[1])
        print("상위 10 키워드 (키워드, 점수):")
        for kw, score in sorted_keywords[:10]:
            print(kw, score)
        top_keywords = [kw for kw, score in sorted_keywords[:4]]
        keyword_elapsed_time = time() - keyword_start_time
        print(f"키워드 추출 소요 시간: {keyword_elapsed_time:.2f}초")
    except Exception as e:
        print("키워드 추출 중 오류:", e)
        return JSONResponse(status_code=500, content={
            "status": {"code": "500", "message": "키워드 추출 중 오류"},
            "content": {}
        })
    
    # c. 구글 검색 실행
    try:
        search_start_time = time()
        query = " AND ".join(top_keywords)
        search_results = google_search(query)
        search_elapsed_time = time() - search_start_time
        print(f"구글 검색 소요 시간: {search_elapsed_time:.2f}초")
    except Exception as e:
        print("구글 검색 중 오류:", e)
        return JSONResponse(status_code=500, content={
            "status": {"code": "500", "message": "구글 검색 중 오류"},
            "content": {}
        })
    
    if not search_results:
        return JSONResponse(status_code=200, content={
            "status": {"code": "200", "message": "관련 글이 없습니다."},
            "content": {}
        })
    
    # 추천 항목 구성
    recommendations = []
    for item in search_results:
        recommendations.append({
            "title": item["title"],
            "link": item["link"],
            "thumbnail": item["thumbnail"]
        })
    
    total_elapsed_time = time() - start_time
    print(f"전체 소요 시간: {total_elapsed_time:.2f}초")
    
    return JSONResponse(content={
        "status": {"code": "200", "message": "success"},
        "content": recommendations
    })

# FastAPI 앱 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
