import json
import logging

from pathlib import Path

from core.load_settings import load_settings
from core.setup_logging import setup_logging

settings = load_settings()
logger = logging.getLogger("ingestion")

def chunk_news_categories():
    file_path = Path(settings["data"]["processed_dir"]) / "newsCategories.json"

    # Kiểm tra sự tồn tại của file trước khi mở
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []

    # LOAD DATA
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            news_categories = json.load(file)
            logger.info(f"Loaded {len(news_categories)} records from {file_path}")
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return []

    if isinstance(news_categories, dict):
        news_categories = [news_categories] # gan dict thanh list de xu ly tiep

    if not isinstance(news_categories, list):
        logger.error(f"News categories data is not a list or dict: {type(news_categories)}")
        return []

    if not news_categories:
        logger.warning(f"No news categories data found in {file_path}")
        return []

    # chunk news categories
    chunks = []

    for idx, news_category in enumerate(news_categories):
        if not isinstance(news_category, dict):
            logger.warning(f"Skipping non-dict news category at index {idx}: {type(news_category)}")
            continue

        if not news_category:
            logger.warning(f"Skipping empty news category at index {idx}")
            continue

        news_category_id = news_category.get("id")

        news_category_isActive = news_category.get("isActive", True)
        if news_category_isActive is False:
            logger.info(f"Skipping inactive news category at index {idx}")
            continue

        # name va slug la bat buoc
        news_category_name = news_category.get("name", "")
        if not news_category_name or not isinstance(news_category_name, str):
            logger.warning(f"Skipping news category with missing or invalid name at index {idx}")
            continue

        news_category_slug = news_category.get("slug", "")
        if not news_category_slug or not isinstance(news_category_slug, str):
            logger.warning(f"Skipping news category with missing or invalid slug at index {idx}")
            continue

        # cac truong con lai co the null -> chi giu lai neu la str
        news_category_description = news_category.get("description") or ""
        if not isinstance(news_category_description, str):
            logger.warning(f"Invalid description for news category at index {idx}, ignored")
            news_category_description = ""

        news_category_seoTitle = news_category.get("seoTitle") or ""
        if not isinstance(news_category_seoTitle, str):
            logger.warning(f"Invalid seoTitle for news category at index {idx}, ignored")
            news_category_seoTitle = ""

        news_category_seoDescription = news_category.get("seoDescription") or ""
        if not isinstance(news_category_seoDescription, str):
            logger.warning(f"Invalid seoDescription for news category at index {idx}, ignored")
            news_category_seoDescription = ""

        news_category_order = news_category.get("order")

        text_parts = [
            f"Danh mục tin tức: {news_category_name}",
            f"Mô tả: {news_category_name}: {news_category_description}" if news_category_description else "",
            f"SEO Title: {news_category_name}: {news_category_seoTitle}" if news_category_seoTitle else "",
            f"SEO Description: {news_category_name}: {news_category_seoDescription}" if news_category_seoDescription else "",
        ]

        text = "\n".join(filter(None, text_parts))

        chunks.append(
            {
                "text": text,
                "metadata": {
                    "type": "news_category",
                    "source": "newsCategories.json",
                    "news_category_id": news_category_id,
                    "news_category_name": news_category_name,
                    "news_category_slug": news_category_slug,
                    "news_category_description": news_category_description,
                    "news_category_seoTitle": news_category_seoTitle,
                    "news_category_seoDescription": news_category_seoDescription,
                    "news_category_order": news_category_order,
                },
            }
        )

    if not chunks:
        logger.warning(f"No chunks created for news categories from {file_path}")

    logger.info(f"Created {len(chunks)} chunks for news categories")
    return chunks
