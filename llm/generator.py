# Generator nhận câu hỏi của user, gọi retriever để lấy các chunk liên quan, ghép thành prompt (context + question) rồi gọi LLM để sinh câu trả lời.

import logging
import time

from openai import OpenAI, APIConnectionError, APITimeoutError, RateLimitError, APIStatusError

from core.load_settings import load_settings
from llm.prompt import build_prompt, format_context
from retrieval.retriever import retriever

settings = load_settings()
logger = logging.getLogger("llm")

LLM_CONFIG = settings.get("llm", {})
LLM_MODEL = LLM_CONFIG.get("model_name", "gpt-4o-mini")
LLM_BASE_URL = LLM_CONFIG.get("base_url")
LLM_TEMPERATURE = LLM_CONFIG.get("temperature", 0.2)
LLM_MAX_TOKENS = LLM_CONFIG.get("max_tokens", 512)
LLM_TIMEOUT = LLM_CONFIG.get("timeout", 60)

FALLBACK_ANSWER = "Xin lỗi bạn, hệ thống đang gặp sự cố một chút. Bạn thử lại sau ít phút nha! 🙏"
EMPTY_QUESTION_ANSWER = "Bạn muốn hỏi gì về NMK Architects nè? 😊"

_client = None

def get_client() -> OpenAI:
    global _client
    if _client is None:
        logger.info(
            f"Initializing OpenAI LLM client: model={LLM_MODEL}, base_url={LLM_BASE_URL}, "
            f"temperature={LLM_TEMPERATURE}, max_tokens={LLM_MAX_TOKENS}, timeout={LLM_TIMEOUT}s"
        )
        _client = OpenAI(base_url=LLM_BASE_URL, timeout=LLM_TIMEOUT)  # doc OPENAI_API_KEY tu .env
    return _client

def generate(prompt: str) -> str:
    client = get_client()
    logger.debug(f"Sending prompt to LLM ({len(prompt)} chars):\n{prompt}")

    start = time.perf_counter()
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
        )
    except APITimeoutError as e:
        logger.error(f"LLM request timed out after {LLM_TIMEOUT}s (model={LLM_MODEL}): {e}")
        raise
    except RateLimitError as e:
        logger.error(f"LLM rate limit exceeded (model={LLM_MODEL}): {e}")
        raise
    except APIConnectionError as e:
        logger.error(f"Cannot connect to LLM API (base_url={LLM_BASE_URL}): {e}")
        raise
    except APIStatusError as e:
        logger.error(f"LLM API returned status {e.status_code} (model={LLM_MODEL}): {e}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during LLM generation (model={LLM_MODEL}): {e}")
        raise
    elapsed = time.perf_counter() - start

    choice = response.choices[0]
    answer = (choice.message.content or "").strip()
    usage = response.usage

    if usage:
        logger.info(
            f"LLM responded in {elapsed:.2f}s: prompt_tokens={usage.prompt_tokens}, "
            f"completion_tokens={usage.completion_tokens}, total_tokens={usage.total_tokens}"
        )
    else:
        logger.info(f"LLM responded in {elapsed:.2f}s (no usage info).")

    if choice.finish_reason == "length":
        logger.warning(f"Answer was truncated because it reached max_tokens={LLM_MAX_TOKENS}.")
    if not answer:
        logger.warning(f"LLM returned an empty answer (finish_reason={choice.finish_reason}).")

    logger.debug(f"LLM answer ({len(answer)} chars):\n{answer}")
    return answer

def generate_answer(question: str) -> str:
    if not question or not question.strip():
        logger.warning("Empty question received.")
        return EMPTY_QUESTION_ANSWER

    logger.info(f"Received question: {question}")
    start = time.perf_counter()

    try:
        documents = retriever(question)
        logger.info(f"Retriever returned {len(documents)} documents.")
        if not documents:
            logger.warning("No relevant documents found, LLM will answer with empty context.")

        context = format_context([doc.text for doc in documents])
        prompt = build_prompt(context, question)
        answer = generate(prompt)
    except Exception as e:
        logger.error(f"Failed to answer question '{question}': {e}")
        return FALLBACK_ANSWER

    logger.info(f"Answered question in {time.perf_counter() - start:.2f}s.")
    return answer
