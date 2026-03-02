import requests
import json
import re
import os
from datetime import datetime

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
OUTPUT_FILE = "index.html"

def build_prompt():
    today = datetime.utcnow().strftime("%B %d, %Y")
    return "You are SIGNAL, a bilingual (English & Mandarin Chinese) senior international news analyst. Today is " + today + ". Find the MOST SIGNIFICANT real international news stories from the past 7 days. Return ONLY a raw valid JSON object. No markdown, no backticks, no explanation. Start with { and end with }. Use this exact format: { \"politics\": [ { \"rank\": 1, \"headline_en\": \"English headline\", \"headline_zh\": \"中文标题\", \"region\": \"REGION\", \"body_en\": \"3-4 sentences.\", \"body_zh\": \"3-4句。\", \"significance_en\": \"1-2 sentences.\", \"significance_zh\": \"1-2句。\", \"links\": [ {\"type\": \"source\", \"label\": \"Outlet - Title\", \"url\": \"https://url.com\"} ] } ], \"business\": [], \"technology\": [], \"conflict\": [] }. RULES: Each section must have 6 to 8 stories. All URLs must be real. Chinese must be fluent Simplified Chinese. No Chinese curly quotes in JSON."

def fetch_briefing():
    print("Calling Gemini API...")
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + GEMINI_API_KEY
    payload = {
        "contents": [{"parts": [{"text": build_prompt()}]}],
        "tools": [{"google_search": {}}]
    }
    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    full_text = data["candidates"][0]["content"]["parts"][-1]["text"]
    clean = full_text.replace("```json", "").replace("```", "").strip()
    match = re.search(r'\{[\s\S]*\}', clean)
    if not match:
        raise ValueError("No JSON found in response")
    result = json.loads(match.group(0))
    print("Success!")
    return result

def inject_into_html(stories):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        html = f.read()
    start_marker = "function getSampleBriefing(){"
    end_marker = "\nsetDates();"
    start = html.index(start_marker)
    end = html.index(end_marker)
    json_str = json.dumps(stories, ensure_ascii=False, indent=2)
    new_fn = "function getSampleBriefing(){\n  return " + json_str + ";\n}"
    new_html = html[:start] + new_fn + html[end:]
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    new_html = re.sub(r'<!-- LAST UPDATED:.*?-->', '<!-- LAST UPDATED: ' + now + ' -->', new_html)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(new_html)
    print("index.html updated at " + now)

if __name__ == "__main__":
    try:
        stories = fetch_briefing()
        inject_into_html(stories)
    except Exception as e:
        print("ERROR: " + str(e))
        raise
