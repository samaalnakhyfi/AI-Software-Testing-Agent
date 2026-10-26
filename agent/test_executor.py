import time


def run_test_case(page, test_case, response=None):
    """
    Run one test case against an already loaded page.

    `response` is the navigation response returned by page.goto(); the
    page_load check uses it to verify the HTTP status.
    """
    test_type = test_case.get("test_type")
    result = {
        "name": test_case.get("name", "Unnamed test"),
        "test_type": test_type,
        "expected_result": test_case.get("expected_result", ""),
        "status": "passed",
        "error": None,
        "duration_ms": 0,
    }

    check = CHECKS.get(test_type)
    if check is None:
        result.update(status="skipped", error=f"Unknown test type: {test_type!r}")
        return result

    started = time.perf_counter()
    try:
        check(page, test_case, response)
    except AssertionError as error:
        result.update(status="failed", error=str(error) or "Assertion failed")
    except Exception as error:
        result.update(status="failed", error=f"{type(error).__name__}: {error}")
    result["duration_ms"] = round((time.perf_counter() - started) * 1000)

    return result


def _check_page_title(page, test_case, response):
    title = page.title().strip()
    assert title, "The page has no title"

    expected = test_case.get("expected_title")
    if expected:
        assert expected.lower() in title.lower(), (
            f"Expected the title to contain {expected!r}, got {title!r}"
        )


def _check_page_load(page, test_case, response):
    assert response is not None, "No navigation response was received"
    assert response.ok, f"The page responded with HTTP {response.status}"


def _check_https(page, test_case, response):
    assert page.url.startswith("https://"), f"The page is not served over HTTPS: {page.url}"


def _check_link_presence(page, test_case, response):
    link_text = test_case.get("link_text")
    if link_text:
        assert page.get_by_role("link", name=link_text).count() > 0, (
            f"No link named {link_text!r} was found"
        )
    else:
        assert page.locator("a").count() > 0, "The page has no links"


CHECKS = {
    "page_title": _check_page_title,
    "page_load": _check_page_load,
    "https_security": _check_https,
    "link_presence": _check_link_presence,
}
