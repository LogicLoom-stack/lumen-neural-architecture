import os
import json
import requests
import time
import random
from google import genai
from google.genai import types

# Configuration
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OUTPUT_PATH = "data/news.json"

def fetch_filtered_news():
    """Fetches real-time headlines with error handling."""
    if not NEWS_API_KEY:
        return ["System initialized", "Awaiting data stream"]

    url = f"https://newsapi.org/v2/everything?q=(tech OR space)&language=en&sortBy=publishedAt&pageSize=5&apiKey={NEWS_API_KEY}"
    
    try:
        print("Step 1: Fetching live headlines...")
        response = requests.get(url, timeout=10)
        data = response.json()
        articles = data.get("articles", [])
        return [a["title"] for a in articles if a.get("title")] or ["Network stable"]
    except Exception as e:
        print(f"News Fetch Error: {e}")
        return ["Data stream interrupted"]

def analyze_sentiment(headlines):
    """Analyzes headlines using stable 2026 model IDs and aggressive retries."""
    if not GEMINI_API_KEY:
        return []

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"Analyze these headlines. Return JSON array: [{{'text': '...', 'score': -10to10, 'category': 'TECH', 'color_hex': '#hex'}}] \n\n Headlines: {headlines}"
    
    # STABLE 2026 MODELS (Updated to avoid 404s)
    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    
    for model_name in models_to_try:
        # We try each model up to 3 times with increasing waits
        for attempt in range(3):
            try:
                print(f"Step 2: Analysis attempt with {model_name} (Try {attempt+1})...")
                
                # Add a 'Safety Jitter' - Free tier hates simultaneous requests
                time.sleep(random.uniform(5, 15)) 
                
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                
                if response and response.text:
                    print(f"SUCCESS: {model_name} responded.")
                    return json.loads(response.text)
                    
            except Exception as e:
                err = str(e)
                if "429" in err or "QUOTA" in err:
                    wait_time = (attempt + 1) * 30 # Wait 30s, then 60s
                    print(f"Quota hit (429). Cooling down for {wait_time}s...")
                    time.sleep(wait_time)
                elif "404" in err:
                    print(f"Model {model_name} is deprecated. Trying next model...")
                    break # Skip to next model in list
                else:
                    print(f"Unexpected error: {e}")
                    break

    print("CRITICAL: All models busy. Using Simulation Backup.")
    return [{"text": "NEURAL FEED: STABILIZED", "score": 5, "category": "SYSTEM", "color_hex": "#00ffcc"}]

def main():
    print("--- INITIATING RECOVERY UPDATE ---")
    headlines = fetch_filtered_news()
    results = analyze_sentiment(headlines)
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Update complete. Written to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
