from playwright.sync_api import sync_playwright

def test_website():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        try:
            page = browser.new_page()
            page.goto("https://example.com")

            assert page.title() == "Example Domain"

            print("Website test passed successfully!")
        finally:
            browser.close()