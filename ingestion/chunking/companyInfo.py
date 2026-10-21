import json
import logging

from pathlib import Path

from altair import value
from importlib_metadata import metadata

from core.load_settings import load_settings
from core.setup_logging import setup_logging

settings = load_settings()
logger = logging.getLogger("ingestion")

def chunk_company_info():
    file_path = Path(settings["data"]["processed_dir"]) / "companyInfo.json"

    # Kiểm tra sự tồn tại của file trước khi mở
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []

    # LOAD DATA
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            company_info = json.load(file_path)
            logger.info(f"Loaded {len(company_info)} records from {file_path}")
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return []

    if isinstance(company_info, dict):
        company_info = [company_info] # gan dict thanh list de xu ly tiep

    if not isinstance(company_info, list):
        logger.error(f"Company info data is not a list or dict: {type(company_info)}")
        return []

    if not company_info:
        logger.warning(f"No company info data found in {file_path}")
        return []

    # chunk company info
    chunks = []

    for idx, company_info in enumerate(company_info):
        if not isinstance(company_info, dict):
            logger.warning(f"Skipping non-dict company info at index {idx}: {type(company_info)}")
            continue

        if not company_info:
            logger.warning(f"Skipping empty company info at index {idx}")
            continue

        company_id = company_info.get("id")

        company_name = company_info.get("companyName", "")
        if not company_name or not isinstance(company_name, str):
            logger.warning(f"Skipping company info with missing or invalid companyName at index {idx}")
            continue
        
        company_sologan = company_info.get("companySlogan", "")
        if not company_sologan or not isinstance(company_sologan, str):
            logger.warning(f"Skipping company info with missing or invalid companySlogan at index {idx}")
            continue
        
        company_description = company_info.get("companyDescription", "")
        if not company_description or not isinstance(company_description, str):
            logger.warning(f"Skipping company info with missing or invalid companyDescription at index {idx}")
            continue

        company_hotlines = company_info.get("hotlines", [])
        company_emails = company_info.get("emails", [])

        company_mainAddress = company_info.get("mainAddress", "")
        if not isinstance(company_mainAddress, str):
            logger.warning(f"Skipping company info with missing or invalid companyMainAddress at index {idx}")
            continue

        company_workingHours = company_info.get("workingHours", "")
        if not isinstance(company_workingHours, str):
            logger.warning(f"Skipping company info with missing or invalid companyWorkingHours at index {idx}")
            continue

        company_website = company_info.get("website", "")
        if not company_website or not isinstance(company_website, str):
            logger.warning(f"Skipping company info with missing or invalid companyWebsite at index {idx}")
            continue

        company_socialLinks = company_info.get("socialLinks", {})
        if not company_socialLinks or not isinstance(company_socialLinks, dict):   
            # nếu có items trong structureData thì vẫn chấp nhận, nếu không có items thì bỏ qua 
            company_socialLinks = ", ".join([f"{k}: {v}" for k, v in company_socialLinks.items() if value])

        company_total_employees = company_info.get("totalEmployees", "")
        if not company_total_employees or not isinstance(company_total_employees, str):
            logger.warning(f"Skipping company info with missing or invalid companyTotalEmployees at index {idx}")
            continue
        
        company_total_engineers = company_info.get("totalEngineers", "")
        if not company_total_engineers or not isinstance(company_total_engineers, int):
            logger.warning(f"Skipping company info with missing or invalid companyTotalEngineers at index {idx}")
            continue

        company_total_architects = company_info.get("totalArchitects", "")
        if not company_total_architects or not isinstance(company_total_architects, int):
            logger.warning(f"Skipping company info with missing or invalid companyTotalArchitects at index {idx}")
            continue

        company_total_projects = company_info.get("totalProjects", "")
        if not company_total_projects or not isinstance(company_total_projects, int):
            logger.warning(f"Skipping company info with missing or invalid companyTotalProjects at index {idx}")
            continue

        company_total_architects = company_info.get("totalArchitects", "")
        if not company_total_architects or not isinstance(company_total_architects, int):
            logger.warning(f"Skipping company info with missing or invalid companyTotalArchitects at index {idx}")
            continue

        company_founded_year = company_info.get("foundedYear", "")
        if not company_founded_year or not isinstance(company_founded_year, str):
            logger.warning(f"Skipping company info with missing or invalid companyFoundedYear at index {idx}")
            continue

        company_industry = company_info.get("industry", "")
        if not company_industry or not isinstance(company_industry, str):
            logger.warning(f"Skipping company info with missing or invalid companyIndustry at index {idx}")
            continue

        company_thumbnailUrl = company_info.get("thumbnailUrl", "")
        if not company_thumbnailUrl or not isinstance(company_thumbnailUrl, str):
            logger.warning(f"Skipping company info with missing or invalid companyThumbnailUrl at index {idx}")
            continue

        company_thumbnailAlt = company_info.get("thumbnailAlt", "")
        if not company_thumbnailAlt or not isinstance(company_thumbnailAlt, str):
            logger.warning(f"Skipping company info with missing or invalid companyThumbnailAlt at index {idx}")
            continue

        company_thumbnailTitle = company_info.get("thumbnailTitle", "")
        if not company_thumbnailTitle or not isinstance(company_thumbnailTitle, str):
            logger.warning(f"Skipping company info with missing or invalid companyThumbnailTitle at index {idx}")
            continue    

        company_seoTitle = company_info.get("seoTitle", "")
        if not company_seoTitle or not isinstance(company_seoTitle, str):   
            logger.warning(f"Skipping company info with missing or invalid companySeoTitle at index {idx}")
            continue

        company_seoDescription = company_info.get("seoDescription", "")
        if not company_seoDescription or not isinstance(company_seoDescription, str):
            logger.warning(f"Skipping company info with missing or invalid companySeoDescription at index {idx}")
            continue

        company_structureData = company_info.get("structureData", {})
        if not company_structureData or not isinstance(company_structureData, dict):   
            # nếu có items trong structureData thì vẫn chấp nhận, nếu không có items thì bỏ qua 
            company_structureData = ", ".join([f"{k}: {v}" for k, v in company_structureData.items() if value])

        text_parts = [
            f"Tên Công ty: {company_name}",
            f"Khẩu hiệu: {company_name}: {company_sologan}" if company_sologan else "",
            f"Mô tả: {company_name}: {company_description}",
            f"Hotlines: {company_name}: {', '.join(company_hotlines) if company_hotlines else 'N/A'}",
            f"Emails: {company_name}: {', '.join(company_emails) if company_emails else 'N/A'}",
            f"Địa chỉ: {company_name}: {company_mainAddress if company_mainAddress else 'N/A'}",
            f"Giờ làm việc: {company_name}: {company_workingHours if company_workingHours else 'N/A'}",
            f"Số lượng nhân viên: {company_name}: {company_total_employees if company_total_employees else 'N/A'}",
            f"Số lượng kỹ sư: {company_name}: {company_total_engineers if company_total_engineers else 'N/A'}",
            f"Số lượng dự án: {company_name}: {company_total_projects if company_total_projects else 'N/A'}",
            f"Số lượng kiến trúc sư: {company_name}: {company_total_architects if company_total_architects else 'N/A'}",
            f"Năm thành lập: {company_name}: {company_founded_year if company_founded_year else 'N/A'}",
            f"Ngành nghề: {company_name}: {company_industry if company_industry else 'N/A'}",
            f"Thumbnail URL: {company_name}: {company_thumbnailUrl if company_thumbnailUrl else 'N/A'}",
            f"Thumbnail Alt: {company_name}: {company_thumbnailAlt if company_thumbnailAlt else 'N/A'}",
            f"Thumbnail Title: {company_name}: {company_thumbnailTitle if company_thumbnailTitle else 'N/A'}",
            f"SEO Title: {company_name}: {company_seoTitle if company_seoTitle else 'N/A'}",
            f"SEO Description: {company_name}: {company_seoDescription if company_seoDescription else 'N/A'}",
            f"Structure Data: {company_name}: {company_structureData if company_structureData else 'N/A'}",
            f"Social Links: {company_name}: {', '.join(company_socialLinks) if company_socialLinks else 'N/A'}",
            f"Website: {company_name}: {company_website}" if company_website else "",
        ]

        text = "\n".join(filter(None, text_parts))

        chunks.append(
            {
                "text": "\n".join(filter(None, text_parts)),
                "metadata": {
                    "type": "company_info",
                    "source": "companyInfo.json",
                    "company_id": company_id,
                    "company_name": company_name,
                    "company_sologan": company_sologan,
                    "company_description": company_description,
                    "company_hotlines": company_hotlines,
                    "company_emails": company_emails,
                    "company_mainAddress": company_mainAddress,
                    "company_workingHours": company_workingHours,
                    "company_website": company_website,
                    "company_socialLinks": company_socialLinks,
                    "company_total_employees": company_total_employees,
                    "company_total_engineers": company_total_engineers,
                    "company_total_projects": company_total_projects,
                    "company_total_architects": company_total_architects,
                    "company_founded_year": company_founded_year,
                    "company_industry": company_industry,
                    "company_thumbnailUrl": company_thumbnailUrl,
                    "company_thumbnailAlt": company_thumbnailAlt,
                    "company_thumbnailTitle": company_thumbnailTitle,
                    "company_seoTitle": company_seoTitle,
                    "company_seoDescription": company_seoDescription,
                    "company_structureData": company_structureData,
                },
            }
        )
    if not chunks:
        logger.warning(f"Skipping empty chunk for company info at index {idx}")

    return chunks