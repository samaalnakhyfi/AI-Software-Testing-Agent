# AI Software Testing Agent

An AI-assisted website testing agent built with Python, Playwright, and a local Ollama model.

The agent inspects a website, asks the model to write test cases based on what actually exists on the page, runs them in a real browser, asks the model to analyze the results, and produces an HTML dashboard.

## Features

- Website inspection with Playwright (title, headings, links, buttons)
- AI-generated test cases grounded in the real page content
- Automatic fallback to built-in test cases when the AI is unavailable
- Test execution with clear failure messages and per-test timing
- AI analysis of the results with recommendations
- HTML dashboard with success rate, per-test results, and light/dark mode
- JSON output for use in other tools, and a non-zero exit code when tests fail (CI friendly)

## Supported test types

| Test type        | What it checks                                                  |
|------------------|-----------------------------------------------------------------|
| `page_title`     | The page has a title (and contains `expected_title` if given)    |
| `page_load`      | The page responds with a successful HTTP status                  |
| `https_security` | The page is served over HTTPS                                    |
| `link_presence`  | A link named `link_text` exists (or any link, if not given)      |

## Technologies

- Python 3.10+
- Playwright
- Ollama with Qwen2.5-Coder 7B
- Markdown, HTML and CSS
- pytest

## Project Structure

```text
AI-Software-testing-Agent/
├── agent/
│   ├── config.py            # settings (URL, model, reports folder)
│   ├── ai_client.py         # talks to the local Ollama model
│   ├── test_generator.py    # inspects the site and generates test cases
│   ├── test_executor.py     # runs each test case on the page
│   ├── result_analyzer.py   # summary numbers and AI analysis
│   └── report_generator.py  # HTML dashboard
├── tests/                   # pytest tests for the agent itself
├── reports/                 # generated output (not committed)
├── main.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## How to Run

1. Install the dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   playwright install chromium
   ```

2. Install [Ollama](https://ollama.com), then download the model and start the server:

   ```bash
   ollama pull qwen2.5-coder:7b
   ollama serve
   ```

3. Run the agent:

   ```bash
   python main.py                              # tests https://example.com
   python main.py --url https://your-site.com  # test another website
   python main.py --headed --pause             # watch the browser
   ```

4. Open `reports/dashboard.html` in your browser.

If Ollama is not running, the agent still runs the built-in test cases and notes in the report that the AI analysis is unavailable.

## Configuration

These environment variables override the defaults in `agent/config.py`:

| Variable       | Default               |
|----------------|-----------------------|
| `TEST_WEBSITE` | `https://example.com` |
| `OLLAMA_MODEL` | `qwen2.5-coder:7b`    |
| `REPORTS_DIR`  | `reports`             |

## Output

| File                         | Content                          |
|------------------------------|----------------------------------|
| `reports/test_cases.json`    | The test cases that were run     |
| `reports/test_results.json`  | Summary and per-test results     |
| `reports/ai_analysis.md`     | The AI analysis                  |
| `reports/dashboard.html`     | The HTML dashboard               |

To rebuild the dashboard from the last run without testing again:

```bash
python -m agent.report_generator
```

## Running the Tests

```bash
pytest                   # all tests
pytest -m "not network"  # skip tests that need internet access
```
