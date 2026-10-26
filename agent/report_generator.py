import html
import json
from pathlib import Path
from string import Template

import markdown

from agent.config import REPORTS_DIR

STATUS_LABELS = {"passed": "Passed", "failed": "Failed", "skipped": "Skipped"}

REPORT_TEMPLATE = Template("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Test Dashboard</title>
<style>
:root {
  --bg: #f5f7fb;
  --surface: #ffffff;
  --text: #0f172a;
  --muted: #64748b;
  --border: #e2e8f0;
  --track: #e2e8f0;
  --code-bg: #f1f5f9;
  --accent: #4f46e5;
  --passed: #15803d;
  --passed-bg: #dcfce7;
  --failed: #b91c1c;
  --failed-bg: #fee2e2;
  --skipped: #b45309;
  --skipped-bg: #fef3c7;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0b1120;
    --surface: #111827;
    --text: #e5e7eb;
    --muted: #94a3b8;
    --border: #1f2937;
    --track: #1f2937;
    --code-bg: #1e293b;
    --accent: #818cf8;
    --passed: #4ade80;
    --passed-bg: rgba(34, 197, 94, 0.15);
    --failed: #f87171;
    --failed-bg: rgba(239, 68, 68, 0.15);
    --skipped: #fbbf24;
    --skipped-bg: rgba(245, 158, 11, 0.15);
  }
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.5;
}
.container { max-width: 1100px; margin: 0 auto; padding: 40px 16px 48px; }
header { margin-bottom: 28px; }
.eyebrow {
  margin: 0 0 6px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent);
}
h1 { margin: 0; font-size: 30px; letter-spacing: -0.02em; }
.meta { display: flex; flex-wrap: wrap; gap: 6px 22px; margin-top: 10px; color: var(--muted); font-size: 14px; }
.meta strong { color: var(--text); font-weight: 600; }
.meta a { color: var(--accent); text-decoration: none; }
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 22px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}
.summary { display: grid; grid-template-columns: 240px 1fr; gap: 16px; margin-bottom: 16px; }
.rate { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; }
.rate.good { --ring: var(--passed); }
.rate.warn { --ring: var(--skipped); }
.rate.bad { --ring: var(--failed); }
.ring {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  background: conic-gradient(var(--ring) ${success_angle}deg, var(--track) 0);
  display: grid;
  place-items: center;
}
.ring-inner {
  width: 118px;
  height: 118px;
  border-radius: 50%;
  background: var(--surface);
  display: grid;
  place-content: center;
  text-align: center;
}
.ring-value { font-size: 28px; font-weight: 700; font-variant-numeric: tabular-nums; }
.ring-label, .rate-note { font-size: 12px; color: var(--muted); }
.side { display: flex; flex-direction: column; gap: 16px; }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.stat .label { font-size: 13px; font-weight: 600; color: var(--muted); }
.stat .value { margin-top: 4px; font-size: 34px; font-weight: 700; font-variant-numeric: tabular-nums; }
.stat.passed .value { color: var(--passed); }
.stat.failed .value { color: var(--failed); }
.stat.skipped .value { color: var(--skipped); }
.bar { display: flex; height: 12px; border-radius: 999px; overflow: hidden; background: var(--track); }
.bar span { display: block; min-width: 0; }
.bar .passed { background: var(--passed); }
.bar .failed { background: var(--failed); }
.bar .skipped { background: var(--skipped); }
.legend { display: flex; flex-wrap: wrap; gap: 16px; margin-top: 12px; font-size: 13px; color: var(--muted); }
.legend span::before {
  content: "";
  display: inline-block;
  width: 10px;
  height: 10px;
  margin-right: 6px;
  border-radius: 3px;
  background: currentColor;
  vertical-align: -1px;
}
.legend .passed::before { background: var(--passed); }
.legend .failed::before { background: var(--failed); }
.legend .skipped::before { background: var(--skipped); }
section.card { margin-top: 16px; }
h2 { margin: 0 0 14px; font-size: 18px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--muted);
}
td { padding: 14px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }
tr:last-child td { border-bottom: 0; }
td.num { color: var(--muted); font-variant-numeric: tabular-nums; white-space: nowrap; }
.test-name { font-weight: 600; }
.test-type { margin-top: 2px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; color: var(--muted); }
.badge { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; white-space: nowrap; }
.badge.passed { background: var(--passed-bg); color: var(--passed); }
.badge.failed { background: var(--failed-bg); color: var(--failed); }
.badge.skipped { background: var(--skipped-bg); color: var(--skipped); }
.error {
  margin-top: 8px;
  padding: 8px 10px;
  max-height: 160px;
  overflow: auto;
  border-radius: 8px;
  background: var(--failed-bg);
  color: var(--failed);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-word;
}
.empty { text-align: center; color: var(--muted); padding: 28px; }
.analysis { line-height: 1.7; }
.analysis > :first-child { margin-top: 0; }
.analysis h1, .analysis h2, .analysis h3, .analysis h4 { margin: 22px 0 8px; font-size: 16px; }
.analysis ul, .analysis ol { padding-left: 22px; }
.analysis code { padding: 1px 6px; border-radius: 6px; background: var(--code-bg); font-size: 13px; }
.analysis pre { padding: 12px 14px; border-radius: 10px; background: var(--code-bg); overflow: auto; }
.analysis pre code { padding: 0; background: none; }
footer { margin-top: 28px; text-align: center; font-size: 12px; color: var(--muted); }
@media (max-width: 760px) {
  .summary { grid-template-columns: 1fr; }
  .stats { grid-template-columns: repeat(2, 1fr); }
  h1 { font-size: 24px; }
}
</style>
</head>
<body>
<div class="container">
  <header>
    <p class="eyebrow">AI Software Testing Agent</p>
    <h1>Test Dashboard</h1>
    <div class="meta">
      <span>Website: <a href="${website}">${website}</a></span>
      <span>Run at: <strong>${generated_at}</strong></span>
      <span>Duration: <strong>${duration}s</strong></span>
      <span>Test cases: <strong>${source}</strong></span>
    </div>
  </header>

  <div class="summary">
    <div class="card rate ${rate_class}">
      <div class="ring">
        <div class="ring-inner">
          <div class="ring-value">${success_rate}%</div>
          <div class="ring-label">success rate</div>
        </div>
      </div>
      <div class="rate-note">Skipped tests are not counted</div>
    </div>
    <div class="side">
      <div class="stats">
        <div class="card stat"><div class="label">Total</div><div class="value">${total}</div></div>
        <div class="card stat passed"><div class="label">Passed</div><div class="value">${passed}</div></div>
        <div class="card stat failed"><div class="label">Failed</div><div class="value">${failed}</div></div>
        <div class="card stat skipped"><div class="label">Skipped</div><div class="value">${skipped}</div></div>
      </div>
      <div class="card">
        <div class="bar">
          <span class="passed" style="flex: ${passed}"></span>
          <span class="failed" style="flex: ${failed}"></span>
          <span class="skipped" style="flex: ${skipped}"></span>
        </div>
        <div class="legend">
          <span class="passed">Passed ${passed}</span>
          <span class="failed">Failed ${failed}</span>
          <span class="skipped">Skipped ${skipped}</span>
        </div>
      </div>
    </div>
  </div>

  <section class="card">
    <h2>Test Results</h2>
    <div class="table-wrap">
      <table>
        <thead>
          <tr><th>#</th><th>Test</th><th>Status</th><th>Expected result</th><th>Time</th></tr>
        </thead>
        <tbody>
${rows}
        </tbody>
      </table>
    </div>
  </section>

  <section class="card">
    <h2>AI Test Analysis</h2>
    <div class="analysis">
${analysis}
    </div>
  </section>

  <footer>Generated by AI Software Testing Agent &middot; Playwright + Ollama</footer>
</div>
</body>
</html>
""")


def generate_report(results, ai_analysis, output_path):
    """Render the test results and AI analysis into a standalone HTML dashboard."""
    success_rate = results.get("success_rate", 0)

    if success_rate >= 80:
        rate_class = "good"
    elif success_rate >= 50:
        rate_class = "warn"
    else:
        rate_class = "bad"

    page = REPORT_TEMPLATE.substitute(
        website=html.escape(results.get("website", "")),
        generated_at=html.escape(results.get("generated_at", "").replace("T", " ")),
        duration=results.get("duration_seconds", 0),
        source="AI generated" if results.get("test_source") == "ai" else "Built-in fallback",
        total=results.get("total_tests", 0),
        passed=results.get("passed", 0),
        failed=results.get("failed", 0),
        skipped=results.get("skipped", 0),
        success_rate=f"{success_rate:.0f}" if success_rate == int(success_rate) else f"{success_rate:.1f}",
        success_angle=f"{success_rate * 3.6:.1f}",
        rate_class=rate_class,
        rows=_render_rows(results.get("test_details", [])),
        # The analysis comes from a model fed with website content, so escape it
        # before rendering the Markdown to keep any HTML in it from running.
        analysis=markdown.markdown(
            html.escape(ai_analysis or "No AI analysis available.", quote=False),
            extensions=["fenced_code", "tables"],
        ),
    )

    output_path = Path(output_path)
    output_path.write_text(page, encoding="utf-8")
    print(f"HTML Dashboard generated: {output_path}")
    return output_path


def _render_rows(test_details):
    if not test_details:
        return '<tr><td colspan="5" class="empty">No tests were run.</td></tr>'

    rows = []
    for index, test in enumerate(test_details, start=1):
        status = test.get("status")
        if status not in STATUS_LABELS:
            status = "skipped"

        details = html.escape(test.get("expected_result") or "—")
        if test.get("error"):
            details += f'<div class="error">{html.escape(test["error"])}</div>'

        rows.append(
            "<tr>"
            f'<td class="num">{index}</td>'
            f'<td><div class="test-name">{html.escape(test.get("name", ""))}</div>'
            f'<div class="test-type">{html.escape(test.get("test_type") or "unknown")}</div></td>'
            f'<td><span class="badge {status}">{STATUS_LABELS[status]}</span></td>'
            f"<td>{details}</td>"
            f'<td class="num">{test.get("duration_ms", 0)} ms</td>'
            "</tr>"
        )

    return "\n".join(rows)


if __name__ == "__main__":
    # Rebuild the dashboard from the files saved by the last run.
    results = json.loads((REPORTS_DIR / "test_results.json").read_text(encoding="utf-8"))

    analysis_path = REPORTS_DIR / "ai_analysis.md"
    if analysis_path.exists():
        ai_analysis = analysis_path.read_text(encoding="utf-8")
    else:
        ai_analysis = "No AI analysis available."

    generate_report(results, ai_analysis, REPORTS_DIR / "dashboard.html")
