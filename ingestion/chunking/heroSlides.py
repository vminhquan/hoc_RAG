import json
import logging
from pathlib import Path

from core.load_settings import load_settings
from core.setup_logging import setup_logging

settings = load_settings()
logger = logging.getLogger("ingestion")

def chunk_hero_slides():
    file_path = Path(settings["data"]["processed_dir"]) / "heroSlides.json"

    # Kiểm tra sự tồn tại của file trước khi mở
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []

    # LOAD DATA
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            hero_slides = json.load(file)
            logger.info(f"Loaded {len(hero_slides)} records from {file_path}")
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return []

    if isinstance(hero_slides, dict):
        hero_slides = [hero_slides]  # Convert dict to list for further processing
    
    if not isinstance(hero_slides, list):
        logger.error(f"Hero slides data is not a list or dict: {type(hero_slides)}")
        return []

    if not hero_slides:
        logger.warning(f"No hero slides data found in {file_path}")
        return []

    # chunk hero slides
    chunks = []

    for idx, hero_slide in enumerate(hero_slides):
        if not isinstance(hero_slide, dict):
            logger.warning(f"Skipping non-dict hero slide at index {idx}: {type(hero_slide)}")
            continue

        if not hero_slide:
            logger.warning(f"Skipping empty hero slide at index {idx}")
            continue

        hero_slide_id = hero_slide.get("id")

        hero_slide_isActive = hero_slide.get("isActive", True)
        if hero_slide_isActive is False:
            logger.info(f"Skipping inactive hero slide at index {idx}")
            continue

        # title la bat buoc
        hero_slide_title = hero_slide.get("title") or ""
        if not hero_slide_title or not isinstance(hero_slide_title, str):
            logger.warning(f"Skipping hero slide with missing title at index {idx}")
            continue

        # cac truong con lai co the null
        hero_slide_subtitle = hero_slide.get("subtitle") or ""
        if not isinstance(hero_slide_subtitle, str):
            logger.warning(f"Invalid subtitle for hero slide at index {idx}, ignored")
            hero_slide_subtitle = ""

        hero_slide_description = hero_slide.get("description") or ""
        if not isinstance(hero_slide_description, str):
            logger.warning(f"Invalid description for hero slide at index {idx}, ignored")
            hero_slide_description = ""

        hero_slide_page = hero_slide.get("page") or ""
        if not isinstance(hero_slide_page, str):
            logger.warning(f"Invalid page for hero slide at index {idx}, ignored")
            hero_slide_page = ""

        hero_slide_order = hero_slide.get("order", 0)
        if not isinstance(hero_slide_order, int):
            logger.warning(f"Invalid order for hero slide at index {idx}, defaulting to 0")
            hero_slide_order = 0

        hero_slide_imageUrl = hero_slide.get("imageUrl") or ""
        hero_slide_imageAlt = hero_slide.get("imageAlt") or ""
        hero_slide_videoUrl = hero_slide.get("videoUrl") or ""
        hero_slide_videoTitle = hero_slide.get("videoTitle") or ""

        text_parts = [
            f"Tiêu đề: {hero_slide_title}",
            f"Tiêu đề phụ: {hero_slide_title}: {hero_slide_subtitle}" if hero_slide_subtitle else "",
            f"Mô tả: {hero_slide_title}: {hero_slide_description}" if hero_slide_description else "",
            f"Trang: {hero_slide_title}: {hero_slide_page}" if hero_slide_page else "",
        ]

        text = "\n".join(filter(None, text_parts))

        chunks.append(
            {
                "text": text,
                "metadata": {
                    "type": "hero_slide",
                    "source": "heroSlides.json",
                    "hero_slide_id": hero_slide_id,
                    "hero_slide_title": hero_slide_title,
                    "hero_slide_subtitle": hero_slide_subtitle,
                    "hero_slide_page": hero_slide_page,
                    "hero_slide_order": hero_slide_order,
                    "hero_slide_imageUrl": hero_slide_imageUrl,
                    "hero_slide_imageAlt": hero_slide_imageAlt,
                    "hero_slide_videoUrl": hero_slide_videoUrl,
                    "hero_slide_videoTitle": hero_slide_videoTitle,
                },
            }
        )

    if not chunks:
        logger.warning(f"No chunks created for hero slides from {file_path}")

    logger.info(f"Created {len(chunks)} chunks for hero slides")
    return chunks
