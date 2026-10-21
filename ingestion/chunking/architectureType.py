import json
import logging

from pathlib import Path

from core.load_settings import load_settings
from core.setup_logging import setup_logging

settings = load_settings()
logger = logging.getLogger("ingestion")

def chunk_architecture_types():
    file_path = Path(settings["data"]["processed_dir"]) / "architectureTypes.json"

    # Kiểm tra sự tồn tại của file trước khi mở
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []

    # LOAD DATA
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            architecture_types = json.load(file)
            logger.info(f"Loaded {len(architecture_types)} records from {file_path}")
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return []

    if isinstance(architecture_types, dict):
        architecture_types = [architecture_types] # gan dict thanh list de xu ly tiep

    if not isinstance(architecture_types, list):
        logger.error(f"Architecture types data is not a list or dict: {type(architecture_types)}")
        return []

    if not architecture_types:
        logger.warning(f"No architecture types data found in {file_path}")
        return []

    # chunk architecture types
    chunks = []

    for idx, architecture_type in enumerate(architecture_types):
        if not isinstance(architecture_type, dict):
            logger.warning(f"Skipping non-dict architecture type at index {idx}: {type(architecture_type)}")
            continue

        if not architecture_type:
            logger.warning(f"Skipping empty architecture type at index {idx}")
            continue

        architecture_type_id = architecture_type.get("id")

        architecture_type_isActive = architecture_type.get("isActive", True)
        if architecture_type_isActive is False:
            logger.info(f"Skipping inactive architecture type at index {idx}")
            continue

        # name va slug la bat buoc
        architecture_type_name = architecture_type.get("name", "")
        if not architecture_type_name or not isinstance(architecture_type_name, str):
            logger.warning(f"Skipping architecture type with missing or invalid name at index {idx}")
            continue

        architecture_type_slug = architecture_type.get("slug", "")
        if not architecture_type_slug or not isinstance(architecture_type_slug, str):
            logger.warning(f"Skipping architecture type with missing or invalid slug at index {idx}")
            continue

        # cac truong con lai co the null -> chi giu lai neu la str
        architecture_type_description = architecture_type.get("description") or ""
        if not isinstance(architecture_type_description, str):
            logger.warning(f"Invalid description for architecture type at index {idx}, ignored")
            architecture_type_description = ""

        architecture_type_imageUrl = architecture_type.get("imageUrl") or ""
        if not isinstance(architecture_type_imageUrl, str):
            logger.warning(f"Invalid imageUrl for architecture type at index {idx}, ignored")
            architecture_type_imageUrl = ""

        architecture_type_imageAlt = architecture_type.get("imageAlt") or ""
        if not isinstance(architecture_type_imageAlt, str):
            logger.warning(f"Invalid imageAlt for architecture type at index {idx}, ignored")
            architecture_type_imageAlt = ""

        architecture_type_seoTitle = architecture_type.get("seoTitle") or ""
        if not isinstance(architecture_type_seoTitle, str):
            logger.warning(f"Invalid seoTitle for architecture type at index {idx}, ignored")
            architecture_type_seoTitle = ""

        architecture_type_seoDescription = architecture_type.get("seoDescription") or ""
        if not isinstance(architecture_type_seoDescription, str):
            logger.warning(f"Invalid seoDescription for architecture type at index {idx}, ignored")
            architecture_type_seoDescription = ""

        architecture_type_order = architecture_type.get("order")

        text_parts = [
            f"Loại hình kiến trúc: {architecture_type_name}",
            f"Mô tả: {architecture_type_name}: {architecture_type_description}" if architecture_type_description else "",
            f"SEO Title: {architecture_type_name}: {architecture_type_seoTitle}" if architecture_type_seoTitle else "",
            f"SEO Description: {architecture_type_name}: {architecture_type_seoDescription}" if architecture_type_seoDescription else "",
            f"Hình ảnh: {architecture_type_name}: {architecture_type_imageAlt}" if architecture_type_imageAlt else "",
        ]

        text = "\n".join(filter(None, text_parts))

        chunks.append(
            {
                "text": text,
                "metadata": {
                    "type": "architecture_type",
                    "source": "architectureTypes.json",
                    "architecture_type_id": architecture_type_id,
                    "architecture_type_name": architecture_type_name,
                    "architecture_type_slug": architecture_type_slug,
                    "architecture_type_description": architecture_type_description,
                    "architecture_type_imageUrl": architecture_type_imageUrl,
                    "architecture_type_imageAlt": architecture_type_imageAlt,
                    "architecture_type_seoTitle": architecture_type_seoTitle,
                    "architecture_type_seoDescription": architecture_type_seoDescription,
                    "architecture_type_order": architecture_type_order,
                },
            }
        )

    if not chunks:
        logger.warning(f"No chunks created for architecture types from {file_path}")

    logger.info(f"Created {len(chunks)} chunks for architecture types")
    return chunks
