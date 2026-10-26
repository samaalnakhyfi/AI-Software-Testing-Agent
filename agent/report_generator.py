import json
from pathlib import Path

def generate_report():
    results_path = Path("reports/test_results.json")
    analysis_path = Path("reports/ai_analysis.txt")

    with results_path.open("r", encoding="utf-8") as file:
        results = json.load(file)

    with analysis_path.open("r", encoding="utf-8") as file:
        ai_analysis = file.read()

        html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>AI Software Testing Dashboard</title>
     
    <style>
    body {
        font-family: Arial, sans-serif;
        background-color: #f4f7fc;
        color: #1e293b;
        margin: 0;
        padding: 40px;
    }

    h1 {
        color: #1e3a8a;
        text-align: center;
    }

    h2 {
        color: #334155;
    }

    p {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        font-size: 18px;
    }
       pre {
        background: white;
        padding: 20px;
        border-radius: 12px;
        font-size: 15px;
        line-height: 1.8;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
        font-family: Arial, sans-serif;
    }
</style>    
    </head>
    <body>
        <h1>AI Software Testing Dashboard</h1>
        <h2>Test Results</h2>

        <p>Total Tests: TOTAL_PLACEHOLDER</p>
        <p>Passed: PASSED_PLACEHOLDER</p>
        <p>Failed: FAILED_PLACEHOLDER</p>
        <p>Success Rate: SUCCESS_RATE_PLACEHOLDER%</p>
        <h2>AI Test Analysis</h2>
        <pre>AI_ANALYSIS_PLACEHOLDER</pre>
    </body>
    </html>
    """
    html = html.replace("TOTAL_PLACEHOLDER", str(results["total_tests"]))
    html = html.replace("PASSED_PLACEHOLDER", str(results["passed"]))
    html = html.replace("FAILED_PLACEHOLDER", str(results["failed"]))
    success_rate = (results["passed"] / results["total_tests"] * 100) if results["total_tests"] > 0 else 0

    html = html.replace("SUCCESS_RATE_PLACEHOLDER", f"{success_rate:.2f}")
    analysis_path = Path("reports/ai_analysis.txt")

    if analysis_path.exists():
       ai_analysis = analysis_path.read_text(encoding="utf-8")
    else:
       ai_analysis = "No AI analysis available."

    html = html.replace("AI_ANALYSIS_PLACEHOLDER", ai_analysis)
    html = html.replace("SUCCESS_RATE_PLACEHOLDER", f"{(results['passed'] / results['total_tests'] * 100):.2f}" if results['total_tests'] > 0 else "0.00")

    report_path = Path("reports/dashboard.html")

    with report_path.open("w", encoding="utf-8") as file:
        file.write(html)

    print("HTML Dashboard generated successfully!")    