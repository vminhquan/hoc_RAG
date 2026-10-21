import html
import json
import logging
import re

from pathlib import Path

from core.load_settings import load_settings
from core.setup_logging import setup_logging

settings = load_settings()
logger = logging.getLogger("ingestion")

# content cua project la HTML dai -> can lam sach va chia nho
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


def chunk_projects():
    file_path = Path(settings["data"]["processed_dir"]) / "projects.json"

    # Kiểm tra sự tồn tại của file trước khi mở
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []

    # LOAD DATA
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            projects = json.load(file)
            logger.info(f"Loaded {len(projects)} records from {file_path}")
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return []

    if isinstance(projects, dict):
        projects = [projects] # gan dict thanh list de xu ly tiep

    if not isinstance(projects, list):
        logger.error(f"Projects data is not a list or dict: {type(projects)}")
        return []

    if not projects:
        logger.warning(f"No projects data found in {file_path}")
        return []

    # chunk projects
    chunks = []

    for idx, project in enumerate(projects):
        if not isinstance(project, dict):
            logger.warning(f"Skipping non-dict project at index {idx}: {type(project)}")
            continue

        if not project:
            logger.warning(f"Skipping empty project at index {idx}")
            continue

        project_id = project.get("id")

        project_status = project.get("status", "")
        if project_status != "PUBLISHED":
            logger.info(f"Skipping unpublished project at index {idx}: {project_status}")
            continue

        # title va slug la bat buoc
        project_title = project.get("title", "")
        if not project_title or not isinstance(project_title, str):
            logger.warning(f"Skipping project with missing or invalid title at index {idx}")
            continue

        project_slug = project.get("slug", "")
        if not project_slug or not isinstance(project_slug, str):
            logger.warning(f"Skipping project with missing or invalid slug at index {idx}")
            continue

        # cac truong con lai co the null
        project_description = project.get("description") or ""
        if not isinstance(project_description, str):
            logger.warning(f"Invalid description for project at index {idx}, ignored")
            project_description = ""

        project_location = project.get("location") or ""
        if not isinstance(project_location, str):
            logger.warning(f"Invalid location for project at index {idx}, ignored")
            project_location = ""

        project_investor = project.get("investor") or ""
        if not isinstance(project_investor, str):
            logger.warning(f"Invalid investor for project at index {idx}, ignored")
            project_investor = ""

        project_area = project.get("area")
        if project_area is not None and not isinstance(project_area, (int, float)):
            logger.warning(f"Invalid area for project at index {idx}, ignored")
            project_area = None

        project_completedDate = project.get("completedDate") or ""
        if not isinstance(project_completedDate, str):
            logger.warning(f"Invalid completedDate for project at index {idx}, ignored")
            project_completedDate = ""
        project_completedDate = project_completedDate[:10] # chi lay YYYY-MM-DD

        # category / architectureType / interiorStyle la dict long ben trong -> chi lay name
        project_category = project.get("category") or {}
        project_category_name = project_category.get("name", "") if isinstance(project_category, dict) else ""

        project_architectureType = project.get("architectureType") or {}
        project_architectureType_name = project_architectureType.get("name", "") if isinstance(project_architectureType, dict) else ""

        project_interiorStyle = project.get("interiorStyle") or {}
        project_interiorStyle_name = project_interiorStyle.get("name", "") if isinstance(project_interiorStyle, dict) else ""

        project_isFeatured = project.get("isFeatured", False)
        project_thumbnailUrl = project.get("thumbnailUrl") or ""
        project_thumbnailAlt = project.get("thumbnailAlt") or ""
        project_seoTitle = project.get("seoTitle") or ""
        project_content = clean_html(project.get("content"))

        metadata = {
            "type": "project",
            "source": "projects.json",
            "project_id": project_id,
            "project_title": project_title,
            "project_slug": project_slug,
            "project_location": project_location,
            "project_investor": project_investor,
            "project_area": project_area,
            "project_completedDate": project_completedDate,
            "project_category_name": project_category_name,
            "project_architectureType_name": project_architectureType_name,
            "project_interiorStyle_name": project_interiorStyle_name,
            "project_isFeatured": project_isFeatured,
            "project_thumbnailUrl": project_thumbnailUrl,
            "project_thumbnailAlt": project_thumbnailAlt,
            "project_seoTitle": project_seoTitle,
        }

        # chunk 1: thong tin tong quan cua du an
        text_parts = [
            f"Dự án: {project_title}",
            f"Danh mục: {project_title}: {project_category_name}" if project_category_name else "",
            f"Loại hình kiến trúc: {project_title}: {project_architectureType_name}" if project_architectureType_name else "",
            f"Phong cách nội thất: {project_title}: {project_interiorStyle_name}" if project_interiorStyle_name else "",
            f"Địa điểm: {project_title}: {project_location}" if project_location else "",
            f"Diện tích: {project_title}: {project_area} m²" if project_area else "",
            f"Chủ đầu tư: {project_title}: {project_investor}" if project_investor else "",
            f"Ngày hoàn thành: {project_title}: {project_completedDate}" if project_completedDate else "",
            f"Mô tả: {project_title}: {project_description}" if project_description else "",
        ]

        text = "\n".join(filter(None, text_parts))

        chunks.append(
            {
                "text": text,
                "metadata": {**metadata, "chunk_type": "overview", "chunk_index": 0},
            }
        )

        # chunk 2..n: noi dung chi tiet (content) da chia nho
        for content_idx, content_piece in enumerate(split_text(project_content), start=1):
            chunks.append(
                {
                    "text": f"Dự án: {project_title}\n{content_piece}",
                    "metadata": {**metadata, "chunk_type": "content", "chunk_index": content_idx},
                }
            )

    if not chunks:
        logger.warning(f"No chunks created for projects from {file_path}")

    logger.info(f"Created {len(chunks)} chunks for projects")
    return chunks
