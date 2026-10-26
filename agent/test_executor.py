
from playwright.sync_api import sync_playwright


def run_test_case(page, test_case):
    test_name = test_case["name"]
    test_type = test_case.get("test_type")

    try:
        if test_type == "page_title" or test_name == "Page Title Test":       
             assert page.title() != ""

        elif test_type == "page_load" or test_name == "Page Load Test":
            assert page.locator("body").count() > 0

        elif test_type == "https_security" or test_name == "HTTPS Security Test":
            assert page.url.startswith("https://")
        elif test_type == "link_presence" or test_name == "Learn More Link Test":
            assert page.get_by_role("link", name="Learn More").count() > 0
        else:
            return {
                "name": test_name,
                "status": "skipped",
                "error": "Unknown test case"
            }

        return {
            "name": test_name,
            "status": "passed",
            "error": None
        }

    except Exception as error:
        return {
            "name": test_name,
            "status": "failed",
            "error": str(error)
        }
