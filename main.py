import json 
from agent.test_generator import generate_test_cases
from agent.test_generator import generate_ai_test_cases
from agent.test_executor import run_test_case
from playwright.sync_api import sync_playwright
from agent.result_analyzer import analyze_results
from agent.report_generator import generate_report

website = "https://example.com"
test_cases = generate_test_cases(website)
ai_test_cases = generate_ai_test_cases(website)

if isinstance(ai_test_cases, str):
    content = ai_test_cases.strip()

    start = content.find("[")
    end = content.rfind("]")

    if start == -1 or end == -1 or end < start:
        raise ValueError(
            f"AI did not return a JSON array: {content[:300]!r}"
        )

    content = content[start:end + 1]
    ai_test_cases = json.loads(content)

if not isinstance(ai_test_cases, list):
    raise ValueError("AI test cases must be a list")

print("\n=== AI GENERATED TEST CASES ===")
print(ai_test_cases)

with open("reports/ai_test_cases.txt", "w", encoding="utf-8") as file:
     json.dump(ai_test_cases, file, indent=4, ensure_ascii=False)

passed = 0
failed = 0
test_results = []
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    try:
        page = browser.new_page()
        page.goto(website)

        for test_case in ai_test_cases:
            result = run_test_case(page, test_case)
            test_results.append(result)
            print(f"Test: {result['name']}")
            print(f"Status: {result['status']}\n")
            if result["status"] == "passed":
                passed += 1
            else:
                failed += 1 
    finally:
        input("Press Enter to close the browser...")
        browser.close()
print ("==== TEST SUMMARY ====")
print (f"Total Tests: {passed + failed}")
print ("Passed:", passed)
print ("Failed:", failed)
results = {
    "website": website,
    "total_tests": passed + failed,
    "passed": passed,
    "failed": failed,
    "test_details": test_results
}
with open("reports/test_results.json", "w") as file:
    json.dump(results, file, indent=4)

analyze_results("reports/test_results.json")
generate_report()