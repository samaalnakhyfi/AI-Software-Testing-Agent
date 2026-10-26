import json
import ollama 

def analyze_results(file_path):
   with open(file_path, "r") as file:
       results = json.load(file)

   total = results["total_tests"]
   passed = results["passed"]
   failed = results["failed"]

   success_rate = (passed / total) * 100 if total > 0 else 0

   print("==== TEST ANALYSIS ====")
   print(f"Total Tests: {total}")
   print(f"Passed: {passed}")
   print(f"Failed: {failed}")
   print(f"Success Rate: {success_rate:.2f}%")

   test_details = results.get("test_details", [])

   prompt = f"""
    You are an expert software testing engineer.

    Analyze the following test results:
    {json.dumps(test_details, indent=2)}

    Explain:
    1. Overall testing status.
    2. Any failed tests and possible causes.
    3. Recommended improvements.

    Do not invent failures.
    """
   response = ollama.chat(
       model="qwen2.5-coder:7b",
       messages=[
           {
               "role": "user",
               "content": prompt
           }
       ]
   )

   print("\n=== AI TEST ANALYSIS ===")
   print(response["message"]["content"])
   with open("reports/ai_analysis.txt", "w", encoding="utf-8") as file:
    file.write(response["message"]["content"])