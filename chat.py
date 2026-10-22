# Chatbot CLI: cho phép user hỏi đáp trực tiếp với chatbot NMK Architects trên terminal.
# Luồng xử lý: user nhập câu hỏi -> generate_answer (retriever + prompt + LLM) -> in câu trả lời ra màn hình.
# Chạy local:  python chat.py
# Chạy Docker: docker compose --profile chat run --rm chat

import logging

from core.load_settings import load_settings
from core.setup_logging import setup_logging
from llm.generator import generate_answer

# Cấu hình logging trước khi chạy, log sẽ ghi ra console và file logs/application.log
setup_logging()
settings = load_settings()
logger = logging.getLogger("chat")

APP_NAME = settings.get("app", {}).get("name", "NMK-chatbot-app")
APP_VERSION = settings.get("app", {}).get("version", "")

# Các lệnh để thoát khỏi chatbot
EXIT_COMMANDS = {"exit", "quit", "q", "thoat", "thoát"}

WELCOME_MESSAGE = f"""
==================================================
 {APP_NAME} {APP_VERSION}
 Chatbot tư vấn kiến trúc & nội thất NMK Architects
 Gõ 'exit' hoặc 'quit' để thoát.
==================================================
"""

def chat():
    print(WELCOME_MESSAGE)
    logger.info("Chat session started.")

    # Vòng lặp hỏi đáp: chạy liên tục cho đến khi user gõ lệnh thoát hoặc nhấn Ctrl+C
    while True:
        try:
            question = input("\nBạn: ").strip()
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C hoặc Ctrl+D (hoặc hết input khi chạy trong Docker không có -it) -> thoát êm
            print("\nTạm biệt bạn nha! 👋")
            logger.info("Chat session ended by interrupt.")
            break

        # Bỏ qua khi user chỉ nhấn Enter mà không nhập gì
        if not question:
            continue

        # User gõ lệnh thoát -> kết thúc phiên chat
        if question.lower() in EXIT_COMMANDS:
            print("Tạm biệt bạn nha! 👋")
            logger.info("Chat session ended by user.")
            break

        # Gọi generator để lấy câu trả lời.
        # generate_answer đã tự bắt lỗi bên trong và trả về câu xin lỗi nếu có sự cố,
        # nên ở đây chỉ cần in kết quả ra màn hình.
        answer = generate_answer(question)
        print(f"\nNMK Bot: {answer}")

if __name__ == "__main__":
    chat()
