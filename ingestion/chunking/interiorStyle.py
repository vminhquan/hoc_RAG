import json
import logging

from pathlib import Path

from core.load_settings import load_settings
from core.setup_logging import setup_logging

settings = load_settings()
logger = logging.getLogger("ingestion")

def chunk_interior_styles():
    file_path = Path(settings["data"]["processed_dir"]) / "interiorStyles.json"

    # Kiểm tra sự tồn tại của file trước khi mở
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []

    # LOAD DATA
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            interior_styles = json.load(file)
            logger.info(f"Loaded {len(interior_styles)} records from {file_path}")
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return []

    if isinstance(interior_styles, dict):
        interior_styles = [interior_styles] # gan dict thanh list de xu ly tiep

    if not isinstance(interior_styles, list):
        logger.error(f"Interior styles data is not a list or dict: {type(interior_styles)}")
        return []

    if not interior_styles:
        logger.warning(f"No interior styles data found in {file_path}")
        return []

    # chunk interior styles
    chunks = []

    for idx, interior_style in enumerate(interior_styles):
        if not isinstance(interior_style, dict):
            logger.warning(f"Skipping non-dict interior style at index {idx}: {type(interior_style)}")
            continue

        if not interior_style:
            logger.warning(f"Skipping empty interior style at index {idx}")
            continue

        interior_style_id = interior_style.get("id")

        interior_style_isActive = interior_style.get("isActive", True)
        if interior_style_isActive is False:
            logger.info(f"Skipping inactive interior style at index {idx}")
            continue

        # name va slug la bat buoc
        interior_style_name = interior_style.get("name", "")
        if not interior_style_name or not isinstance(interior_style_name, str):
            logger.warning(f"Skipping interior style with missing or invalid name at index {idx}")
            continue

        interior_style_slug = interior_style.get("slug", "")
        if not interior_style_slug or not isinstance(interior_style_slug, str):
            logger.warning(f"Skipping interior style with missing or invalid slug at index {idx}")
            continue

        # cac truong con lai co the null -> chi giu lai neu la str
        interior_style_description = interior_style.get("description") or ""
        if not isinstance(interior_style_description, str):
            logger.warning(f"Invalid description for interior style at index {idx}, ignored")
            interior_style_description = ""

        interior_style_imageUrl = interior_style.get("imageUrl") or ""
        if not isinstance(interior_style_imageUrl, str):
            logger.warning(f"Invalid imageUrl for interior style at index {idx}, ignored")
            interior_style_imageUrl = ""

        interior_style_imageAlt = interior_style.get("imageAlt") or ""
        if not isinstance(interior_style_imageAlt, str):
            logger.warning(f"Invalid imageAlt for interior style at index {idx}, ignored")
            interior_style_imageAlt = ""

        interior_style_seoTitle = interior_style.get("seoTitle") or ""
        if not isinstance(interior_style_seoTitle, str):
            logger.warning(f"Invalid seoTitle for interior style at index {idx}, ignored")
            interior_style_seoTitle = ""

        interior_style_seoDescription = interior_style.get("seoDescription") or ""
        if not isinstance(interior_style_seoDescription, str):
            logger.warning(f"Invalid seoDescription for interior style at index {idx}, ignored")
            interior_style_seoDescription = ""

        interior_style_order = interior_style.get("order")

        text_parts = [
            f"Phong cách nội thất: {interior_style_name}",
            f"Mô tả: {interior_style_name}: {interior_style_description}" if interior_style_description else "",
            f"SEO Title: {interior_style_name}: {interior_style_seoTitle}" if interior_style_seoTitle else "",
            f"SEO Description: {interior_style_name}: {interior_style_seoDescription}" if interior_style_seoDescription else "",
            f"Hình ảnh: {interior_style_name}: {interior_style_imageAlt}" if interior_style_imageAlt else "",
        ]

        text = "\n".join(filter(None, text_parts))

        chunks.append(
            {
                "text": text,
                "metadata": {
                    "type": "interior_style",
                    "source": "interiorStyles.json",
                    "interior_style_id": interior_style_id,
                    "interior_style_name": interior_style_name,
                    "interior_style_slug": interior_style_slug,
                    "interior_style_description": interior_style_description,
                    "interior_style_imageUrl": interior_style_imageUrl,
                    "interior_style_imageAlt": interior_style_imageAlt,
                    "interior_style_seoTitle": interior_style_seoTitle,
                    "interior_style_seoDescription": interior_style_seoDescription,
                    "interior_style_order": interior_style_order,
                },
            }
        )

    if not chunks:
        logger.warning(f"No chunks created for interior styles from {file_path}")

    logger.info(f"Created {len(chunks)} chunks for interior styles")
    return chunks
