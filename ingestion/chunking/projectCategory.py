import json
import logging

from pathlib import Path

from core.load_settings import load_settings
from core.setup_logging import setup_logging

settings = load_settings()
logger = logging.getLogger("ingestion")

def chunk_project_categories():
    file_path = Path(settings["data"]["processed_dir"]) / "projectCategories.json"

    # Kiểm tra sự tồn tại của file trước khi mở
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []

    # LOAD DATA
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            project_categories = json.load(file)
            logger.info(f"Loaded {len(project_categories)} records from {file_path}")
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return []

    if isinstance(project_categories, dict):
        project_categories = [project_categories] # gan dict thanh list de xu ly tiep

    if not isinstance(project_categories, list):
        logger.error(f"Project categories data is not a list or dict: {type(project_categories)}")
        return []

    if not project_categories:
        logger.warning(f"No project categories data found in {file_path}")
        return []

    # chunk project categories
    chunks = []

    for idx, project_category in enumerate(project_categories):
        if not isinstance(project_category, dict):
            logger.warning(f"Skipping non-dict project category at index {idx}: {type(project_category)}")
            continue

        if not project_category:
            logger.warning(f"Skipping empty project category at index {idx}")
            continue

        project_category_id = project_category.get("id")

        project_category_isActive = project_category.get("isActive", True)
        if project_category_isActive is False:
            logger.info(f"Skipping inactive project category at index {idx}")
            continue

        # name va slug la bat buoc
        project_category_name = project_category.get("name", "")
        if not project_category_name or not isinstance(project_category_name, str):
            logger.warning(f"Skipping project category with missing or invalid name at index {idx}")
            continue

        project_category_slug = project_category.get("slug", "")
        if not project_category_slug or not isinstance(project_category_slug, str):
            logger.warning(f"Skipping project category with missing or invalid slug at index {idx}")
            continue

        # cac truong con lai co the null -> chi giu lai neu la str
        project_category_description = project_category.get("description") or ""
        if not isinstance(project_category_description, str):
            logger.warning(f"Invalid description for project category at index {idx}, ignored")
            project_category_description = ""

        project_category_icon = project_category.get("icon") or ""
        if not isinstance(project_category_icon, str):
            logger.warning(f"Invalid icon for project category at index {idx}, ignored")
            project_category_icon = ""

        project_category_seoTitle = project_category.get("seoTitle") or ""
        if not isinstance(project_category_seoTitle, str):
            logger.warning(f"Invalid seoTitle for project category at index {idx}, ignored")
            project_category_seoTitle = ""

        project_category_seoDescription = project_category.get("seoDescription") or ""
        if not isinstance(project_category_seoDescription, str):
            logger.warning(f"Invalid seoDescription for project category at index {idx}, ignored")
            project_category_seoDescription = ""

        project_category_order = project_category.get("order")

        text_parts = [
            f"Danh mục dự án: {project_category_name}",
            f"Mô tả: {project_category_name}: {project_category_description}" if project_category_description else "",
            f"SEO Title: {project_category_name}: {project_category_seoTitle}" if project_category_seoTitle else "",
            f"SEO Description: {project_category_name}: {project_category_seoDescription}" if project_category_seoDescription else "",
        ]

        text = "\n".join(filter(None, text_parts))

        chunks.append(
            {
                "text": text,
                "metadata": {
                    "type": "project_category",
                    "source": "projectCategories.json",
                    "project_category_id": project_category_id,
                    "project_category_name": project_category_name,
                    "project_category_slug": project_category_slug,
                    "project_category_description": project_category_description,
                    "project_category_icon": project_category_icon,
                    "project_category_seoTitle": project_category_seoTitle,
                    "project_category_seoDescription": project_category_seoDescription,
                    "project_category_order": project_category_order,
                },
            }
        )

    if not chunks:
        logger.warning(f"No chunks created for project categories from {file_path}")

    logger.info(f"Created {len(chunks)} chunks for project categories")
    return chunks
