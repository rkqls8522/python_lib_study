from fastapi import FastAPI
from pydantic import BaseModel
from 특화프로젝트.S12P21A408.AI.chatbot.chat.gemini import process_gemini_request
from fastapi.middleware.cors import CORSMiddleware
from 특화프로젝트.S12P21A408.AI.chatbot.chat.schedule_api import router as schedule_router

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

class ChatMessage(BaseModel):
    userId: str
    message: str

@app.post("/chat")
async def chat_endpoint(chat_message: ChatMessage):
    response = process_gemini_request(chat_message.userId, chat_message.message)
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
