from agent.test_executor import run_test_case
from fakes import FakePage, FakeResponse


def run(test_case, page=None, response=None):
    return run_test_case(page or FakePage(), test_case, response or FakeResponse())


def test_page_title_passes():
    result = run({"name": "Title", "test_type": "page_title", "expected_title": "example"})
    assert result["status"] == "passed"
    assert result["error"] is None


def test_page_title_fails_on_unexpected_title():
    result = run({"name": "Title", "test_type": "page_title", "expected_title": "Shop"})
    assert result["status"] == "failed"
    assert "Shop" in result["error"]


def test_page_title_fails_when_empty():
    result = run({"name": "Title", "test_type": "page_title"}, page=FakePage(title="  "))
    assert result["status"] == "failed"


def test_page_load_checks_http_status():
    assert run({"name": "Load", "test_type": "page_load"})["status"] == "passed"

    result = run({"name": "Load", "test_type": "page_load"}, response=FakeResponse(500))
    assert result["status"] == "failed"
    assert "500" in result["error"]


def test_page_load_fails_without_response():
    result = run_test_case(FakePage(), {"name": "Load", "test_type": "page_load"}, None)
    assert result["status"] == "failed"


def test_https_fails_for_plain_http():
    result = run({"name": "HTTPS", "test_type": "https_security"}, page=FakePage(url="http://example.com/"))
    assert result["status"] == "failed"


def test_link_presence_uses_link_text_from_test_case():
    assert run({"name": "Link", "test_type": "link_presence", "link_text": "Learn more"})["status"] == "passed"
    assert run({"name": "Link", "test_type": "link_presence", "link_text": "Contact"})["status"] == "failed"


def test_link_presence_without_link_text_needs_any_link():
    assert run({"name": "Link", "test_type": "link_presence"}, page=FakePage(links=()))["status"] == "failed"


def test_unknown_type_is_skipped():
    result = run({"name": "Login", "test_type": "login"})
    assert result["status"] == "skipped"


def test_unexpected_error_is_reported_as_failure():
    class BrokenPage(FakePage):
        def title(self):
            raise RuntimeError("browser crashed")

    result = run({"name": "Title", "test_type": "page_title"}, page=BrokenPage())
    assert result["status"] == "failed"
    assert "browser crashed" in result["error"]
