import json
import logging
from pathlib import Path

from core.load_settings import load_settings
from core.setup_logging import setup_logging

setup_logging()
settings = load_settings()
logger = logging.getLogger("ingestion")

INPUT_PATH = Path(settings["data"]["raw_dir"])
OUTPUT_PATH = Path(settings["data"]["processed_dir"])


def load_data():
    file_path = INPUT_PATH / "database_export_2026-10-21T00-00-00.json"

    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            logger.info(f"Loaded {len(data)} records from {file_path}")
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return []

    tables = data.get("tables", {})
    logger.info(f"Loaded {len(tables)} tables from {file_path}")

    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    for table_name, table_data in tables.items():
        if not table_data:
            logger.warning(f"No data found for table: {table_name}")
            continue

        logger.info(f"Processing table: {table_name} with {len(table_data)} records")
        output_file = OUTPUT_PATH / f"{table_name}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(table_data, f, ensure_ascii=False, indent=4) # indent=4 la tab dong cho de nhin
            logger.info(f"Saved processed data for table: {table_name} to {output_file}")

    return tables

if __name__ == "__main__":
    load_data()