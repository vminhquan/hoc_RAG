import json
import logging
from pathlib import Path

from core.load_settings import load_settings
from core.setup_logging import setup_logging

settings = load_settings()
logger = logging.getLogger("ingestion")

def chunk_hero_slides():
    file_path = Path(settings(["data"]["priority_dir"])) / "heroSlides.json"

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

        # name and slug are mandatory
        hero_slide_title = hero_slide.get("title", "")
        if not hero_slide_title or not isinstance(hero_slide_title, str):
            logger.warning(f"Skipping hero slide with missing title at index {idx}")
            continue

        hero_slide_subtitle = hero_slide.get("subtitle", "")
        if not hero_slide_subtitle or not isinstance(hero_slide_subtitle, str):
            logger.warning(f"Skipping hero slide with missing subtitle at index {idx}")
            continue

        hero_slide_description = hero_slide.get("description", "")
        if not hero_slide_description or not isinstance(hero_slide_description, str):
            logger.warning(f"Skipping hero slide with missing description at index {idx}")
            continue

        hero_slide_image = hero_slide.get("image", "")
        if not hero_slide_image or not isinstance(hero_slide_image, str):
            logger.warning(f"Skipping hero slide with missing image at index {idx}")
            continue

        hero_slide_video = hero_slide.get("video", "")

        hero_slide_page = hero_slide.get("page", "")
        if not hero_slide_page or not isinstance(hero_slide_page, str):
            logger.warning(f"Skipping hero slide with missing page at index {idx}")
            continue

        hero_slide_order = hero_slide.get("order", 0)
        if not isinstance(hero_slide_order, int):
            logger.warning(f"Invalid order for hero slide at index {idx}, defaulting to 0")
            hero_slide_order = 0

        hero_slide_isActive = hero_slide.get("isActive", True)
        if not isinstance(hero_slide_isActive, bool):
            logger.warning(f"Invalid isActive for hero slide at index {idx}, defaulting to True")
            hero_slide_isActive = True

        hero_slide_imageAlt = hero_slide.get("imageAlt", "")
        if not isinstance(hero_slide_imageAlt, str):
            logger.warning(f"Invalid imageAlt for hero slide at index {idx}, defaulting to empty string")
            hero_slide_imageAlt = ""

        hero_slide_videoTitle = hero_slide.get("videoTitle", "")

        hero_slide_createdAt = hero_slide.get("createdAt", "")
        hero_slide_updatedAt = hero_slide.get("updatedAt", "")

    text_paths = [
        f"Tiêu đề: {hero_slide_title}",
        f"Tiêu đề phụ: {hero_slide_subtitle}",
        f"Mô tả: {hero_slide_description}",
        f"Hình ảnh: {hero_slide_image}",
        f"Video: {hero_slide_video}" if hero_slide_video else "",
        f"Trang: {hero_slide_page}",
        f"Thứ tự: {hero_slide_order}",
        f"Đang hiển thị: {hero_slide_isActive}",
        f"Mô tả hình ảnh: {hero_slide_imageAlt}" if hero_slide_imageAlt else "",
        f"Tiêu đề video: {hero_slide_videoTitle}" if hero_slide_videoTitle else "",
        f"Ngày tạo: {hero_slide_createdAt}" if hero_slide_createdAt else "",
        f"Ngày cập nhật: {hero_slide_updatedAt}" if hero_slide_updatedAt else "",
    ]

    text = "\n".join(filter(None, text_paths))  # Join non-empty parts

    chunks.append(
        {
        "text": "\n".join(filter(None, text_paths)),
        "metadata": {
            "id": hero_slide_id,
            "title": hero_slide_title,
            "subtitle": hero_slide_subtitle,
            "description": hero_slide_description,
            "image": hero_slide_image,
            "video": hero_slide_video,
            "page": hero_slide_page,
            "order": hero_slide_order,
            "isActive": hero_slide_isActive,
            "imageAlt": hero_slide_imageAlt,
            "videoTitle": hero_slide_videoTitle,
            "createdAt": hero_slide_createdAt,
            "updatedAt": hero_slide_updatedAt
        }
    }
    )
    if not chunks:
        logger.warning(f"No chunks created for hero slides from {file_path}")

    return chunks