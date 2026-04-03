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

    # Varied search terms to trigger different chakra resonances
    queries = ["tech innovation", "environmental crisis", "medical breakthrough", "space exploration", "global economy"]
    query = random.choice(queries)
    
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize=12&apiKey={NEWS_API_KEY}"
    
    try:
        print(f"Step 1: Fetching live headlines for query: {query}...")
        response = requests.get(url, timeout=10)
        data = response.json()
        articles = data.get("articles", [])
        return [a["title"] for a in articles if a.get("title")] or ["Neural network heartbeat stable"]
    except Exception as e:
        print(f"News Fetch Error: {e}")
        return ["Data stream local backup active"]

def analyze_sentiment(headlines):
    """Analyzes headlines and maps them to complex multi-chakra energy signatures."""
    if not GEMINI_API_KEY:
        return [{"text": "OFFLINE_MODE", "score": 0, "resonances": [0.5]*7, "global_state": "RAINBOW"}]

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Updated prompt to include the new global_state logic:
    # Gold for positive/growth, Red for negative/crisis, Rainbow for balanced/neutral
    prompt = f"""
    Analyze these headlines for the Lumen Visualizer. 
    Return a JSON array of objects. 
    Each object must have:
    - 'text': Shortened headline (max 40 chars).
    - 'score': Overall sentiment intensity (-10 to 10).
    - 'global_state': A string based on sentiment: 
        'GOLD' (Score > 3: Progress, prosperity, joy)
        'RED' (Score < -3: Crisis, conflict, danger)
        'RAINBOW' (Score between -3 and 3: Neutral, balanced, or complex)
    - 'resonances': An array of 7 floats (0 to 1.0). 
       Each index corresponds to a chakra (0:Root, 1:Sacral, 2:Solar, 3:Heart, 4:Throat, 5:ThirdEye, 6:Crown).
       Higher values mean that specific chakra 'flares' or glows with high-frequency white-hot energy.
    
    Headlines: {headlines}
    """
    
    models_to_try = ["gemini-2.5-flash-preview-09-2025", "gemini-2.0-flash", "gemini-1.5-flash"]
    
    for model_name in models_to_try:
        try:
            print(f"Step 2: Analysis attempt with {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            if response and response.text:
                return json.loads(response.text)
        except Exception as e:
            print(f"Model error: {e}")
            continue

    return [{"text": "SYSTEM_NEUTRAL", "score": 0, "resonances": [0.2]*7, "global_state": "RAINBOW"}]

def main():
    print("--- INITIATING COMPLEX ENERGY DATA UPDATE ---")
    headlines = fetch_filtered_news()
    results = analyze_sentiment(headlines)
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Update complete. Sent {len(results)} complex energy signatures to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
