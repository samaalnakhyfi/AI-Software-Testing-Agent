import argparse
import json
import sys
import time
from datetime import datetime

from playwright.sync_api import sync_playwright

from agent.config import PAGE_TIMEOUT_MS, REPORTS_DIR, WEBSITE_URL
from agent.report_generator import generate_report
from agent.result_analyzer import analyze_results, summarize_results
from agent.test_executor import run_test_case
from agent.test_generator import generate_ai_test_cases, generate_test_cases


def parse_args():
    parser = argparse.ArgumentParser(description="AI-assisted website testing agent")
    parser.add_argument("--url", default=WEBSITE_URL, help=f"website to test (default: {WEBSITE_URL})")
    parser.add_argument("--headed", action="store_true", help="show the browser window while testing")
    parser.add_argument("--pause", action="store_true", help="wait for Enter before closing the browser")
    return parser.parse_args()


def load_test_cases(website):
    """Ask the AI for test cases, falling back to the built-in ones if that fails."""
    try:
        return generate_ai_test_cases(website), "ai"
    except Exception as error:
        print(f"Could not generate AI test cases: {error}")
        print("Falling back to the built-in test cases.")
        return generate_test_cases(website), "fallback"


def run_tests(website, test_cases, headed=False, pause=False):
    test_results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed)
        try:
            page = browser.new_page()
            try:
                response = page.goto(website, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
            except Exception as error:
                print(f"Could not open {website}: {error}")
                response = None

            print("\n=== RUNNING TESTS ===")
            for test_case in test_cases:
                result = run_test_case(page, test_case, response)
                test_results.append(result)
                line = f"[{result['status'].upper():^7}] {result['name']}"
                if result["error"]:
                    line += f" -> {result['error']}"
                print(line)

            if pause:
                input("\nPress Enter to close the browser...")
        finally:
            browser.close()

    return test_results


def main():
    args = parse_args()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now()

    test_cases, source = load_test_cases(args.url)
    print("\n=== TEST CASES ===")
    print(json.dumps(test_cases, indent=2, ensure_ascii=False))
    (REPORTS_DIR / "test_cases.json").write_text(
        json.dumps(test_cases, indent=4, ensure_ascii=False), encoding="utf-8"
    )

    timer = time.perf_counter()
    test_results = run_tests(args.url, test_cases, headed=args.headed, pause=args.pause)

    results = {
        "website": args.url,
        "generated_at": started_at.isoformat(timespec="seconds"),
        "duration_seconds": round(time.perf_counter() - timer, 2),
        "test_source": source,
        **summarize_results(test_results),
        "test_details": test_results,
    }
    (REPORTS_DIR / "test_results.json").write_text(
        json.dumps(results, indent=4, ensure_ascii=False), encoding="utf-8"
    )

    analysis = analyze_results(results, REPORTS_DIR / "ai_analysis.md")
    report_path = generate_report(results, analysis, REPORTS_DIR / "dashboard.html")
    print(f"\nOpen the dashboard: {report_path.resolve()}")

    return 1 if results["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
