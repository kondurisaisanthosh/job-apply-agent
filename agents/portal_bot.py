import os
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import Page

from agents.llm_field_mapper import map_fields_with_llm


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / "secrets" / ".env")


APPLICANT = {
    "first_name": os.getenv("APPLICANT_FIRST_NAME", ""),
    "last_name": os.getenv("APPLICANT_LAST_NAME", ""),
    "email": os.getenv("APPLICANT_EMAIL", ""),
    "phone": os.getenv("APPLICANT_PHONE", ""),
    "linkedin": os.getenv("APPLICANT_LINKEDIN", ""),
    "city": os.getenv("APPLICANT_CITY", ""),
    "state": os.getenv("APPLICANT_STATE", ""),
    "country": os.getenv("APPLICANT_COUNTRY", ""),
}


def safe_click_apply(page: Page) -> bool:
    labels = [
        "Apply",
        "Apply Now",
        "Apply for this job",
        "Start application"
    ]

    for label in labels:
        try:
            target = page.get_by_role("button", name=label).first
            if target.count() > 0 and target.is_visible(timeout=2000):
                target.click()
                page.wait_for_timeout(5000)
                return True
        except Exception:
            pass

        try:
            target = page.get_by_role("link", name=label).first
            if target.count() > 0 and target.is_visible(timeout=2000):
                target.click()
                page.wait_for_timeout(5000)
                return True
        except Exception:
            pass

    return False


def collect_visible_fields(page: Page) -> tuple:
    fields = []

    # Search main page + all iframes
    all_frames = page.frames

    for frame_index, frame in enumerate(all_frames):
        try:
            inputs = frame.locator("input, textarea, select").all()

            for field in inputs:
                try:
                    if not field.is_visible(timeout=1000):
                        continue

                    tag = field.evaluate("el => el.tagName.toLowerCase()")

                    field_info = {
                        "field_index": len(fields),
                        "frame_index": frame_index,
                        "tag": tag,
                        "type": field.get_attribute("type") or "",
                        "name": field.get_attribute("name") or "",
                        "id": field.get_attribute("id") or "",
                        "placeholder": field.get_attribute("placeholder") or "",
                        "aria_label": field.get_attribute("aria-label") or "",
                        "label_text": "",
                    }

                    fields.append(field_info)

                except Exception:
                    continue

        except Exception:
            continue

    return fields, all_frames

def fill_field_by_index(page: Page, frames: list, visible_fields: list, field_index: int, value: str) -> bool:
    if value == "":
        return False

    try:
        field_meta = visible_fields[field_index]
        frame = frames[field_meta["frame_index"]]

        selectors = []

        if field_meta.get("id"):
            selectors.append(f"#{field_meta['id']}")

        if field_meta.get("name"):
            selectors.append(f"[name='{field_meta['name']}']")

        if field_meta.get("placeholder"):
            selectors.append(f"[placeholder='{field_meta['placeholder']}']")

        for selector in selectors:
            try:
                field = frame.locator(selector).first
                if field.count() > 0 and field.is_visible(timeout=1000):
                    field.fill(value)
                    return True
            except Exception:
                continue

    except Exception:
        return False

    return False


def upload_resume(page: Page, resume_path: Path) -> bool:
    for frame in page.frames:
        try:
            file_inputs = frame.locator("input[type='file']")
            if file_inputs.count() > 0:
                file_inputs.first.set_input_files(str(resume_path))
                page.wait_for_timeout(3000)
                return True
        except Exception:
            continue

    return False


def fill_basic_application(page: Page, resume_path: Path) -> dict:
    result = {
        "clicked_apply": False,
        "uploaded_resume": False,
        "llm_mapped_fields": [],
        "filled_fields": [],
        "status": "Started"
    }

    result["clicked_apply"] = safe_click_apply(page)
    page.wait_for_timeout(5000)

    visible_fields, frames = collect_visible_fields(page)
    print(f"Visible fields found: {len(visible_fields)}")
    print(f"Frames found: {len(frames)}")
    print(visible_fields)

    mappings = map_fields_with_llm(visible_fields, APPLICANT)
    result["llm_mapped_fields"] = mappings

    for mapping in mappings:
        try:
            field_index = mapping.get("field_index")
            value = mapping.get("value", "")
            label = mapping.get("field_label", "")

            if fill_field_by_index(page, frames, visible_fields, field_index, value):
                result["filled_fields"].append(label)

        except Exception:
            continue

    result["uploaded_resume"] = upload_resume(page, resume_path)
    result["status"] = "Ready for human review"

    return result