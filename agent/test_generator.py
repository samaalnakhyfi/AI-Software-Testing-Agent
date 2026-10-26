import ollama 
from playwright.sync_api import sync_playwright
def generate_test_cases(website_url):
    """
    Generate basic test cases for a website.
    """
    test_cases = [
        {
            "name": "Page Title Test",
            "description": "Verify that the page has a title",
            "url": website_url
        },
        {
            "name": "Page Load Test",
            "description": "Verify that the website loads successfully",
            "url": website_url
        },
        {
            "name": "HTTPS Security Test",
            "description": "Verify that the website uses HTTPS",
            "url": website_url
        }
    ]

    return test_cases


if __name__ == "__main__":
    website = "https://example.com"

    tests = generate_test_cases(website)

    for test in tests:
        print(test)
def generate_ai_test_cases(website_url):
    website_info = inspect_website(website_url)

    prompt = f"""
Generate exactly 3 software test cases for {website_url}.

Actual website information:
{website_info}

Only use features that exist on the website.
Do not invent login, search, or registration features.

Return ONLY a valid JSON array.

Each test case must contain:
•⁠  ⁠name
•⁠  ⁠test_type
•⁠  ⁠steps
•⁠  ⁠expected_result

The test_type must be one of:
•⁠  ⁠page_title
•⁠  ⁠page_load
•⁠  ⁠https_security
•⁠  ⁠link_presence

Choose only a test type that can be verified
using the actual website information.
"""

    response = ollama.chat(
        model="qwen2.5-coder:7b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response["message"]["content"].strip()

    if content.startswith("⁠```"):
        content = content.split("\n", 1)[1]

    if content.endswith("```"):
        content = content[:-3]

    return content.strip()

def inspect_website(website_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(
                website_url, 
                wait_until="domcontentloaded",
                timeout=60000
            )
            website_info = {
                "title": page.title(),
                "headings": page.locator("h1").all_text_contents(),
                "links": page.locator("a").all_text_contents(),
                "buttons": page.locator("button").all_text_contents(),

            }
            return website_info
        finally:
            browser.close()     