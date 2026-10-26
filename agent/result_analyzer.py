import json
from pathlib import Path

from agent.ai_client import AIUnavailableError, ask_model

STATUSES = ("passed", "failed", "skipped")


def summarize_results(test_results):
    """Count results by status. Skipped tests are left out of the success rate."""
    counts = {
        status: sum(1 for result in test_results if result["status"] == status)
        for status in STATUSES
    }
    executed = counts["passed"] + counts["failed"]
    success_rate = counts["passed"] / executed * 100 if executed else 0.0

    return {
        "total_tests": len(test_results),
        **counts,
        "success_rate": round(success_rate, 2),
    }


def analyze_results(results, output_path=None):
    """Ask the AI model to explain the results and return its analysis text."""
    print("\n==== TEST SUMMARY ====")
    print(f"Total Tests:  {results['total_tests']}")
    print(f"Passed:       {results['passed']}")
    print(f"Failed:       {results['failed']}")
    print(f"Skipped:      {results['skipped']}")
    print(f"Success Rate: {results['success_rate']:.2f}%")

    prompt = f"""
You are an expert software testing engineer.

Analyze the following test results for {results['website']}:
{json.dumps(results['test_details'], indent=2, ensure_ascii=False)}

Explain, using short Markdown sections:
1. Overall testing status.
2. Any failed or skipped tests and their possible causes.
3. Recommended improvements and additional tests worth adding.

Formatting: use "###" headings, bullet points and short paragraphs only.
Do not include code blocks or JSON.

Do not invent failures.
"""

    try:
        analysis = ask_model(prompt)
    except AIUnavailableError as error:
        print(f"\nAI analysis skipped: {error}")
        analysis = f"AI analysis is not available.\n\n{error}"

    print("\n=== AI TEST ANALYSIS ===")
    print(analysis)

    if output_path:
        Path(output_path).write_text(analysis, encoding="utf-8")

    return analysis
