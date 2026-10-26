import pytest
from playwright.sync_api import sync_playwright


@pytest.mark.network
def test_website():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto("https://example.com")

            assert page.title() == "Example Domain"
        finally:
            browser.close()
