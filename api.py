# Web API cho chatbot NMK Architects.
# - POST /api/chat : nhận câu hỏi từ giao diện web, gọi generate_answer (retriever + prompt + LLM) và trả về câu trả lời.
# - GET  /api/health: kiểm tra server còn sống.
# - GET  /          : trả về giao diện hỏi đáp (web/index.html, style.css, app.js).
# Chạy local:  uvicorn api:app --reload --port 8000  -> mở http://localhost:8000
# Chạy Docker: docker compose --profile web up web

import logging
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from core.load_settings import load_settings
from core.setup_logging import setup_logging
from llm.generator import generate_answer

# Cấu hình logging trước khi chạy, log sẽ ghi ra console và file logs/application.log
setup_logging()
settings = load_settings()
logger = logging.getLogger("chat")

APP_NAME = settings.get("app", {}).get("name", "NMK-chatbot-app")
APP_VERSION = settings.get("app", {}).get("version", "")

# Thư mục chứa giao diện HTML/CSS/JS
WEB_DIR = Path(__file__).parent / "web"

# Giới hạn độ dài câu hỏi để tránh user gửi đoạn text quá dài làm tốn token
MAX_QUESTION_LENGTH = 1000

app = FastAPI(title=APP_NAME, version=APP_VERSION)

# Dữ liệu request gửi lên từ giao diện: {"question": "..."}
class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=MAX_QUESTION_LENGTH)

# Dữ liệu response trả về cho giao diện: {"answer": "..."}
class ChatResponse(BaseModel):
    answer: str

@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "app": APP_NAME, "version": APP_VERSION}

# Dùng "def" (không phải "async def") vì generate_answer là hàm đồng bộ, gọi Qdrant + OpenAI mất vài giây.
# FastAPI sẽ tự chạy hàm này trong threadpool nên không chặn các request khác.
@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    start = time.perf_counter()
    logger.info(f"[web] Received question ({len(request.question)} chars).")

    # generate_answer đã tự bắt lỗi bên trong và trả về câu xin lỗi nếu có sự cố
    answer = generate_answer(request.question)

    logger.info(f"[web] Responded in {time.perf_counter() - start:.2f}s.")
    return ChatResponse(answer=answer)

# Mount giao diện ở cuối cùng để không đè lên các route /api/*
# html=True: truy cập "/" sẽ tự trả về web/index.html
app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
