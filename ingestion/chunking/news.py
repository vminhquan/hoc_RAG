import html
import json
import logging
import re

from pathlib import Path

from core.load_settings import load_settings
from core.setup_logging import setup_logging

settings = load_settings()
logger = logging.getLogger("ingestion")

# content cua news la HTML dai -> can lam sach va chia nho
CHUNK_SIZE = settings.get("chunking", {}).get("chunk_size", 1000)
CHUNK_OVERLAP = settings.get("chunking", {}).get("chunk_overlap", 100)


def clean_html(raw_html):
    if not raw_html or not isinstance(raw_html, str):
        return ""
    text = re.sub(r"<(br|/p|/h[1-6]|/li|/div)\s*/?>", "\n", raw_html, flags=re.IGNORECASE) # the dong khoi -> xuong dong
    text = re.sub(r"<[^>]+>", " ", text) # bo cac the html con lai
    text = html.unescape(text) # &agrave; -> à
    text = re.sub(r"[ \t\xa0]+", " ", text)
    text = re.sub(r"\s*\n\s*", "\n", text)
    return text.strip()


def split_text(text, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    if len(text) <= chunk_size:
        return [text] if text else []

    # gom cac doan (paragraph) lai cho den khi du chunk_size
    pieces = []
    current = ""
    for paragraph in text.split("\n"):
        while len(paragraph) > chunk_size: # doan qua dai -> cat cung
            pieces.append(paragraph[:chunk_size])
            paragraph = paragraph[chunk_size - chunk_overlap:]

        if current and len(current) + len(paragraph) + 1 > chunk_size:
            pieces.append(current)
            current = current[-chunk_overlap:] + "\n" + paragraph # giu lai phan overlap
        else:
            current = f"{current}\n{paragraph}" if current else paragraph

    if current:
        pieces.append(current)
    return pieces


def chunk_news():
    file_path = Path(settings["data"]["processed_dir"]) / "news.json"

    # Kiểm tra sự tồn tại của file trước khi mở
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []

    # LOAD DATA
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            news_list = json.load(file)
            logger.info(f"Loaded {len(news_list)} records from {file_path}")
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return []

    if isinstance(news_list, dict):
        news_list = [news_list] # gan dict thanh list de xu ly tiep

    if not isinstance(news_list, list):
        logger.error(f"News data is not a list or dict: {type(news_list)}")
        return []

    if not news_list:
        logger.warning(f"No news data found in {file_path}")
        return []

    # chunk news
    chunks = []

    for idx, news in enumerate(news_list):
        if not isinstance(news, dict):
            logger.warning(f"Skipping non-dict news at index {idx}: {type(news)}")
            continue

        if not news:
            logger.warning(f"Skipping empty news at index {idx}")
            continue

        news_id = news.get("id")

        news_status = news.get("status", "")
        if news_status != "PUBLISHED":
            logger.info(f"Skipping unpublished news at index {idx}: {news_status}")
            continue

        # title va slug la bat buoc
        news_title = news.get("title", "")
        if not news_title or not isinstance(news_title, str):
            logger.warning(f"Skipping news with missing or invalid title at index {idx}")
            continue

        news_slug = news.get("slug", "")
        if not news_slug or not isinstance(news_slug, str):
            logger.warning(f"Skipping news with missing or invalid slug at index {idx}")
            continue

        # cac truong con lai co the null
        news_excerpt = news.get("excerpt") or ""
        if not isinstance(news_excerpt, str):
            logger.warning(f"Invalid excerpt for news at index {idx}, ignored")
            news_excerpt = ""

        news_author = news.get("author") or ""
        if not isinstance(news_author, str):
            logger.warning(f"Invalid author for news at index {idx}, ignored")
            news_author = ""

        news_publishedAt = news.get("publishedAt") or ""
        if not isinstance(news_publishedAt, str):
            logger.warning(f"Invalid publishedAt for news at index {idx}, ignored")
            news_publishedAt = ""
        news_publishedAt = news_publishedAt[:10] # chi lay YYYY-MM-DD

        news_readingTime = news.get("readingTime")
        if news_readingTime is not None and not isinstance(news_readingTime, int):
            logger.warning(f"Invalid readingTime for news at index {idx}, ignored")
            news_readingTime = None

        # category la dict long ben trong -> chi lay name
        news_category = news.get("category") or {}
        news_category_name = news_category.get("name", "") if isinstance(news_category, dict) else ""

        news_projectId = news.get("projectId")
        news_isFeatured = news.get("isFeatured", False)
        news_thumbnailUrl = news.get("thumbnailUrl") or ""
        news_content = clean_html(news.get("content"))

        metadata = {
            "type": "news",
            "source": "news.json",
            "news_id": news_id,
            "news_title": news_title,
            "news_slug": news_slug,
            "news_author": news_author,
            "news_publishedAt": news_publishedAt,
            "news_readingTime": news_readingTime,
            "news_category_name": news_category_name,
            "news_projectId": news_projectId,
            "news_isFeatured": news_isFeatured,
            "news_thumbnailUrl": news_thumbnailUrl,
        }

        # chunk 1: thong tin tong quan cua bai viet
        text_parts = [
            f"Tin tức: {news_title}",
            f"Danh mục: {news_title}: {news_category_name}" if news_category_name else "",
            f"Tác giả: {news_title}: {news_author}" if news_author else "",
            f"Ngày đăng: {news_title}: {news_publishedAt}" if news_publishedAt else "",
            f"Thời gian đọc: {news_title}: {news_readingTime} phút" if news_readingTime else "",
            f"Tóm tắt: {news_title}: {news_excerpt}" if news_excerpt else "",
        ]

        text = "\n".join(filter(None, text_parts))

        chunks.append(
            {
                "text": text,
                "metadata": {**metadata, "chunk_type": "overview", "chunk_index": 0},
            }
        )

        # chunk 2..n: noi dung chi tiet (content) da chia nho
        for content_idx, content_piece in enumerate(split_text(news_content), start=1):
            chunks.append(
                {
                    "text": f"Tin tức: {news_title}\n{content_piece}",
                    "metadata": {**metadata, "chunk_type": "content", "chunk_index": content_idx},
                }
            )

    if not chunks:
        logger.warning(f"No chunks created for news from {file_path}")

    logger.info(f"Created {len(chunks)} chunks for news")
    return chunks
