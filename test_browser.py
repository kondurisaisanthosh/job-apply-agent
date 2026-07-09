from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        slow_mo=500
    )

    page = browser.new_page()
    page.goto("https://www.google.com")

    input("Browser should be open now. Press Enter to close...")
    browser.close()