from playwright.sync_api import sync_playwright
from urllib.parse import urljoin


JOB_KEYWORDS = [
    "software engineer",
    "software developer",
    "backend engineer",
    "java developer",
    "full stack",
    "spring boot",
    "developer",
    "engineer"
]


def find_jobs_on_page(company_name: str, careers_url: str) -> list:
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # visible browser for debugging
        page = browser.new_page()

        try:
            print(f"Opening {company_name}: {careers_url}")

            page.goto(careers_url, wait_until="networkidle", timeout=90000)
            page.wait_for_timeout(8000)

            # Try search box if available
            search_inputs = page.locator("input").all()

            for input_box in search_inputs:
                try:
                    placeholder = input_box.get_attribute("placeholder") or ""
                    aria = input_box.get_attribute("aria-label") or ""

                    field_text = f"{placeholder} {aria}".lower()

                    if "search" in field_text or "keyword" in field_text:
                        input_box.fill("software engineer")
                        input_box.press("Enter")
                        page.wait_for_timeout(8000)
                        break
                except Exception:
                    continue

            # Collect visible text blocks
            elements = page.locator("a, div, span, h2, h3").all()

            seen = set()

            for element in elements:
                try:
                    text = element.inner_text(timeout=1000).strip()
                    if not text:
                        continue

                    text_clean = " ".join(text.split())
                    text_lower = text_clean.lower()

                    if len(text_clean) < 5 or len(text_clean) > 150:
                        continue

                    if not any(keyword in text_lower for keyword in JOB_KEYWORDS):
                        continue

                    href = None

                    try:
                        href = element.get_attribute("href")
                    except Exception:
                        pass

                    if href:
                        href = urljoin(careers_url, href)
                    else:
                        href = careers_url

                    unique_key = f"{company_name}-{text_clean}-{href}"

                    if unique_key in seen:
                        continue

                    seen.add(unique_key)

                    jobs.append({
                        "company": company_name,
                        "job_title": text_clean,
                        "job_url": href,
                        "job_text": text_clean
                    })

                except Exception:
                    continue

        except Exception as e:
            print(f"Failed to read {company_name}: {e}")

        finally:
            browser.close()

    print(f"Found {len(jobs)} possible jobs at {company_name}")
    return jobs