import json

from playwright.sync_api import sync_playwright

from agent.ai_client import ask_model
from agent.config import PAGE_TIMEOUT_MS

SUPPORTED_TEST_TYPES = ("page_title", "page_load", "https_security", "link_presence")


def generate_test_cases(website_url):
    """
    Generate basic test cases for a website.
    Used as a fallback when the AI model is unavailable.
    """
    return [
        {
            "name": "Page Title Test",
            "test_type": "page_title",
            "expected_result": "The page has a non-empty title",
            "url": website_url,
        },
        {
            "name": "Page Load Test",
            "test_type": "page_load",
            "expected_result": "The website responds with a successful HTTP status",
            "url": website_url,
        },
        {
            "name": "HTTPS Security Test",
            "test_type": "https_security",
            "expected_result": "The website is served over HTTPS",
            "url": website_url,
        },
        {
            "name": "Link Presence Test",
            "test_type": "link_presence",
            "expected_result": "The page contains at least one link",
            "url": website_url,
        },
    ]


def inspect_website(website_url):
    """Collect the visible facts about a page that the AI may build tests on."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(website_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
            return {
                "url": page.url,
                "title": page.title(),
                "headings": _clean_texts(page.locator("h1, h2").all_text_contents()),
                "links": _clean_texts(page.locator("a").all_text_contents()),
                "buttons": _clean_texts(page.locator("button").all_text_contents()),
            }
        finally:
            browser.close()


def _clean_texts(texts, limit=30):
    """Collapse whitespace, drop empty and duplicate entries, and cap the list size."""
    cleaned = []
    for text in texts:
        text = " ".join(text.split())
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned[:limit]


def generate_ai_test_cases(website_url, count=3):
    website_info = inspect_website(website_url)

    prompt = f"""
Generate exactly {count} software test cases for {website_url}.

Actual website information (JSON):
{json.dumps(website_info, indent=2, ensure_ascii=False)}

Rules:
- Only use features that exist in the website information above.
- Do not invent login, search, or registration features.
- Return ONLY a valid JSON array, with no explanation and no markdown.

Each test case is a JSON object with these fields:
- "name": a short descriptive name
- "test_type": one of {", ".join(SUPPORTED_TEST_TYPES)}
- "steps": a list of strings
- "expected_result": a string
- "expected_title": (page_title only) text the page title must contain, copied from the title above
- "link_text": (link_presence only) the exact text of one link from the links above
"""

    return parse_test_cases(ask_model(prompt))


def parse_test_cases(content):
    """Extract and validate the JSON array of test cases from a model reply."""
    start = content.find("[")
    end = content.rfind("]")

    if start == -1 or end < start:
        raise ValueError(f"AI did not return a JSON array: {content[:300]!r}")

    try:
        test_cases = json.loads(content[start:end + 1])
    except json.JSONDecodeError as error:
        raise ValueError(f"AI returned invalid JSON: {error}") from error

    if not isinstance(test_cases, list):
        raise ValueError("AI test cases must be a list")

    valid_cases = [
        test_case
        for test_case in test_cases
        if isinstance(test_case, dict)
        and test_case.get("name")
        and test_case.get("test_type") in SUPPORTED_TEST_TYPES
    ]

    if not valid_cases:
        raise ValueError("AI did not return any usable test cases")

    return valid_cases


if __name__ == "__main__":
    for test in generate_test_cases("https://example.com"):
        print(test)
