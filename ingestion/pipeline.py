import logging

from core.load_settings import load_settings
from core.setup_logging import setup_logging

from ingestion.chunking.project import chunk_projects
from ingestion.chunking.projectCategory import chunk_project_categories
from ingestion.chunking.heroSlides import chunk_hero_slides
from ingestion.chunking.news import chunk_news
from ingestion.chunking.newsCategory import chunk_news_categories
from ingestion.chunking.architectureType import chunk_architecture_types
from ingestion.chunking.companyInfo import chunk_company_info
from ingestion.chunking.interiorStyle import chunk_interior_styles

from vectorstore.upsert import upsert_chunks

setup_logging()
settings = load_settings()
logger = logging.getLogger("ingestion")

def upload_chunks():
    all_chunks = []

    all_chunks.extend(chunk_projects())
    all_chunks.extend(chunk_project_categories())
    all_chunks.extend(chunk_hero_slides())
    all_chunks.extend(chunk_news())
    all_chunks.extend(chunk_news_categories())
    all_chunks.extend(chunk_architecture_types())
    all_chunks.extend(chunk_company_info())
    all_chunks.extend(chunk_interior_styles())

    logger.info(f"Total chunks to upload: {len(all_chunks)}")

    upsert_chunks(all_chunks)

    logger.info("All chunks uploaded successfully.")

if __name__ == "__main__":
    upload_chunks()


