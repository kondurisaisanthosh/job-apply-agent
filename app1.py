from pathlib import Path
from playwright.sync_api import sync_playwright
from agents.portal_bot import fill_basic_application

BASE_DIR = Path(__file__).resolve().parent


def test_apply_one_job():
    job_url = input("Paste job URL: ").strip()

    if not job_url.startswith("http"):
        raise ValueError(f"Invalid job URL: {job_url}")

    resume_path = BASE_DIR / "resume" / "resume.pdf"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=500
        )

        page = browser.new_page()

        page.goto(job_url, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(5000)

        result = fill_basic_application(page, resume_path)

        print(result)

        input("Press Enter to close browser...")
        browser.close()


if __name__ == "__main__":
    test_apply_one_job()

