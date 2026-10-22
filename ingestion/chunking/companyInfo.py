import json
import logging

from pathlib import Path


from core.load_settings import load_settings
from core.setup_logging import setup_logging

settings = load_settings()
logger = logging.getLogger("ingestion")


def get_str(record, key, idx):
    value = record.get(key) or ""
    if not isinstance(value, str):
        logger.warning(f"Invalid {key} for company info at index {idx}, ignored")
        return ""
    return value.strip()


def get_int(record, key, idx):
    value = record.get(key)
    if value is not None and (isinstance(value, bool) or not isinstance(value, int)):
        logger.warning(f"Invalid {key} for company info at index {idx}, ignored")
        return None
    return value


def get_str_list(record, key, idx):
    value = record.get(key) or []
    if not isinstance(value, list):
        logger.warning(f"Invalid {key} for company info at index {idx}, ignored")
        return []
    return [str(item) for item in value if item]


def dict_to_text(value):
    # {"zalo": "...", "x": None} -> "zalo: ..." (bo cac gia tri rong)
    if not isinstance(value, dict):
        return ""
    return ", ".join(
        f"{k}: {json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v}"
        for k, v in value.items() if v
    )


def chunk_company_info():
    file_path = Path(settings["data"]["processed_dir"]) / "companyInfo.json"

    # Kiểm tra sự tồn tại của file trước khi mở
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []

    # LOAD DATA
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            company_infos = json.load(file)
            logger.info(f"Loaded {len(company_infos)} records from {file_path}")
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return []

    if isinstance(company_infos, dict):
        company_infos = [company_infos] # gan dict thanh list de xu ly tiep

    if not isinstance(company_infos, list):
        logger.error(f"Company info data is not a list or dict: {type(company_infos)}")
        return []

    if not company_infos:
        logger.warning(f"No company info data found in {file_path}")
        return []

    # chunk company info
    chunks = []

    for idx, company in enumerate(company_infos):
        if not isinstance(company, dict):
            logger.warning(f"Skipping non-dict company info at index {idx}: {type(company)}")
            continue

        if not company:
            logger.warning(f"Skipping empty company info at index {idx}")
            continue

        company_id = company.get("id")

        # companyName la bat buoc
        company_name = company.get("companyName", "")
        if not company_name or not isinstance(company_name, str):
            logger.warning(f"Skipping company info with missing or invalid companyName at index {idx}")
            continue

        # cac truong con lai co the null
        company_slogan = get_str(company, "companySlogan", idx)
        company_description = get_str(company, "companyDescription", idx)
        company_hotlines = get_str_list(company, "hotlines", idx)
        company_emails = get_str_list(company, "emails", idx)
        company_mainAddress = get_str(company, "mainAddress", idx)
        company_secondaryAddress = get_str(company, "secondaryAddress", idx)
        company_workingHours = get_str(company, "workingHours", idx)
        company_website = get_str(company, "website", idx)
        company_total_employees = get_int(company, "totalEmployees", idx)
        company_total_engineers = get_int(company, "totalEngineers", idx)
        company_total_architects = get_int(company, "totalArchitects", idx)
        company_total_projects = get_int(company, "totalProjects", idx)
        company_founded_year = company.get("foundedYear") or ""
        company_industry = get_str(company, "industry", idx)
        company_thumbnailUrl = get_str(company, "thumbnailUrl", idx)
        company_thumbnailAlt = get_str(company, "thumbnailAlt", idx)
        company_thumbnailTitle = get_str(company, "thumbnailTitle", idx)
        company_seoTitle = get_str(company, "seoTitle", idx)
        company_seoDescription = get_str(company, "seoDescription", idx)

        # socialLinks / structuredData la dict -> chuyen thanh text
        company_socialLinks = dict_to_text(company.get("socialLinks"))
        company_structuredData = dict_to_text(company.get("structuredData"))

        text_parts = [
            f"Tên Công ty: {company_name}",
            f"Khẩu hiệu: {company_name}: {company_slogan}" if company_slogan else "",
            f"Mô tả: {company_name}: {company_description}" if company_description else "",
            f"Hotlines: {company_name}: {', '.join(company_hotlines)}" if company_hotlines else "",
            f"Emails: {company_name}: {', '.join(company_emails)}" if company_emails else "",
            f"Địa chỉ: {company_name}: {company_mainAddress}" if company_mainAddress else "",
            f"Địa chỉ phụ: {company_name}: {company_secondaryAddress}" if company_secondaryAddress else "",
            f"Giờ làm việc: {company_name}: {company_workingHours}" if company_workingHours else "",
            f"Số lượng nhân viên: {company_name}: {company_total_employees}" if company_total_employees is not None else "",
            f"Số lượng kỹ sư: {company_name}: {company_total_engineers}" if company_total_engineers is not None else "",
            f"Số lượng kiến trúc sư: {company_name}: {company_total_architects}" if company_total_architects is not None else "",
            f"Số lượng dự án: {company_name}: {company_total_projects}" if company_total_projects is not None else "",
            f"Năm thành lập: {company_name}: {company_founded_year}" if company_founded_year else "",
            f"Ngành nghề: {company_name}: {company_industry}" if company_industry else "",
            f"Mạng xã hội: {company_name}: {company_socialLinks}" if company_socialLinks else "",
            f"Website: {company_name}: {company_website}" if company_website else "",
        ]

        text = "\n".join(filter(None, text_parts))

        chunks.append(
            {
                "text": text,
                "metadata": {
                    "type": "company_info",
                    "source": "companyInfo.json",
                    "company_id": company_id,
                    "company_name": company_name,
                    "company_slogan": company_slogan,
                    "company_hotlines": company_hotlines,
                    "company_emails": company_emails,
                    "company_mainAddress": company_mainAddress,
                    "company_workingHours": company_workingHours,
                    "company_website": company_website,
                    "company_socialLinks": company_socialLinks,
                    "company_total_employees": company_total_employees,
                    "company_total_engineers": company_total_engineers,
                    "company_total_architects": company_total_architects,
                    "company_total_projects": company_total_projects,
                    "company_founded_year": company_founded_year,
                    "company_industry": company_industry,
                    "company_thumbnailUrl": company_thumbnailUrl,
                    "company_thumbnailAlt": company_thumbnailAlt,
                    "company_thumbnailTitle": company_thumbnailTitle,
                    "company_seoTitle": company_seoTitle,
                    "company_seoDescription": company_seoDescription,
                    "company_structuredData": company_structuredData,
                },
            }
        )

    if not chunks:
        logger.warning(f"No chunks created for company info from {file_path}")

    logger.info(f"Created {len(chunks)} chunks for company info")
    return chunks
