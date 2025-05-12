# generate_cpp_methods.py
from langchain_ollama import OllamaLLM
import csv
import json
import re
import time

model = OllamaLLM(model="llama3.2")

prompt = """
Generate 3 unique C++ methods. Each must:
- Include full valid implementation.
- Include /** ... */ style documentation.

Return them as a JSON array like this:
[
  {
    "method_name": "string",
    "documentation": "escaped string, with \\n for newlines and escaped quotes",
    "code": "escaped string, with \\n for newlines and escaped quotes"
  }
]

Return ONLY the JSON array. No explanations or markdown.
"""

def extract_valid_methods(response):
    try:
        match = re.search(r'\[\s*{.*?}\s*]', response, re.DOTALL)
        if not match:
            raise ValueError("No valid method blocks found")
        methods_raw = match.group(0)
        methods_raw = methods_raw.replace('\r', '').replace('\n', '\\n')
        methods_raw = re.sub(r'\\+', r'\\', methods_raw)  # double-escape backslashes
        return json.loads(methods_raw)
    except Exception as e:
        print("❌ Failed to extract method blocks:", e)
        print("📤 Response was:\n", response[:1000])
        return None

success_count = 0
max_success = 10
attempt = 1

print(f"🚀 Starting method generation loop...")

while success_count < max_success:
    print(f"\n⚙️ Attempt {attempt}...")

    response = model.invoke(prompt).strip()

    methods = extract_valid_methods(response)

    if not methods:
        print(f"❌ Failed on attempt {attempt}")
    else:
        with open("cpp_method_docs.csv", "a", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            if success_count == 0 and attempt == 1:
                writer.writerow(["MethodName", "Documentation", "Code"])
            for item in methods:
                writer.writerow([
                    item["method_name"],
                    item["documentation"],
                    item["code"]
                ])
        print(f"✅ Added {len(methods)} methods (total success: {success_count + 1})")
        success_count += 1

    attempt += 1
    time.sleep(1)  # optional pause to avoid flooding

print("🎉 Done generating 30 C++ methods.")
