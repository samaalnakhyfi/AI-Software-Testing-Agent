from agent.report_generator import generate_report
from agent.result_analyzer import summarize_results


def test_summary_excludes_skipped_from_success_rate():
    summary = summarize_results([
        {"status": "passed"},
        {"status": "passed"},
        {"status": "passed"},
        {"status": "failed"},
        {"status": "skipped"},
    ])
    assert summary == {"total_tests": 5, "passed": 3, "failed": 1, "skipped": 1, "success_rate": 75.0}


def test_summary_of_no_tests():
    assert summarize_results([])["success_rate"] == 0.0


def test_report_shows_results_and_escapes_html(tmp_path):
    results = {
        "website": "https://example.com",
        "generated_at": "2026-10-26T21:00:00",
        "duration_seconds": 1.5,
        "test_source": "ai",
        **summarize_results([{"status": "passed"}, {"status": "failed"}]),
        "test_details": [
            {"name": "<script>alert(1)</script>", "test_type": "page_title", "status": "passed", "error": None},
            {"name": "Load", "test_type": "page_load", "status": "failed", "error": "HTTP 500"},
        ],
    }

    path = generate_report(results, "## Summary\n<img src=x onerror=alert(1)>", tmp_path / "dashboard.html")
    page = path.read_text(encoding="utf-8")

    assert "50%" in page
    assert "HTTP 500" in page
    assert "<h2>Summary</h2>" in page
    assert "<script>alert(1)</script>" not in page
    assert "<img" not in page
