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

    # Broadening search to ensure we always have data for the chakras to process
    url = f"https://newsapi.org/v2/everything?q=(tech OR science OR breakthrough)&language=en&sortBy=publishedAt&pageSize=10&apiKey={NEWS_API_KEY}"
    
    try:
        print("Step 1: Fetching live headlines...")
        response = requests.get(url, timeout=10)
        data = response.json()
        articles = data.get("articles", [])
        return [a["title"] for a in articles if a.get("title")] or ["Neural network heartbeat stable"]
    except Exception as e:
        print(f"News Fetch Error: {e}")
        return ["Data stream local backup active"]

def analyze_sentiment(headlines):
    """Analyzes headlines and maps them to energy signatures."""
    if not GEMINI_API_KEY:
        return [{"text": "OFFLINE_MODE", "score": 0, "color_shift": 0}]

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Prompting Gemini to provide a score (-10 to 10) and a color_shift (0 to 1) 
    # where 0 is 'cool/calm' and 1 is 'intense/vibrant'
    prompt = f"""
    Analyze these headlines for the Lumen Visualizer. 
    Return a JSON array of objects. 
    Each object must have:
    - 'text': Shortened headline (max 40 chars).
    - 'score': Sentiment intensity (-10 to 10).
    - 'color_shift': A float from 0 to 1 representing 'energy turbulence' (0 = stable, 1 = chaotic).
    
    Headlines: {headlines}
    """
    
    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    
    for model_name in models_to_try:
        for attempt in range(3):
            try:
                print(f"Step 2: Analysis attempt with {model_name}...")
                time.sleep(2) # Minimal jitter
                
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                
                if response and response.text:
                    return json.loads(response.text)
                    
            except Exception as e:
                print(f"Model error: {e}")
                time.sleep(5)

    return [{"text": "SYSTEM_NEUTRAL", "score": 0, "color_shift": 0.5}]

def main():
    print("--- INITIATING ENERGY DATA UPDATE ---")
    headlines = fetch_filtered_news()
    results = analyze_sentiment(headlines)
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Update complete. Sent {len(results)} energy signatures to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
