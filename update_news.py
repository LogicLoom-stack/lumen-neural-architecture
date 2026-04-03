import os
import json
import requests
import time
from google import genai
from google.genai import types

# Configuration
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OUTPUT_PATH = "data/news.json"

def fetch_filtered_news():
    """Fetches a very small, highly-curated list of headlines with error safety."""
    if not NEWS_API_KEY:
        print("Missing NEWS_API_KEY environment variable.")
        return []

    topics = "technology OR space OR innovation"
    url = f"https://newsapi.org/v2/everything?q=({topics})&language=en&sortBy=relevancy&pageSize=5&apiKey={NEWS_API_KEY}"
    
    try:
        print("Accessing News Stream...")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        articles = data.get("articles", [])
        if not isinstance(articles, list):
            return []
            
        return [a["title"] for a in articles[:5] if a.get("title") and len(a["title"]) > 5]
    except Exception as e:
        print(f"News API Error: {e}")
        return []

def analyze_sentiment(headlines):
    """Analyzes headlines with strict model naming, safety buffer, and JSON parsing safety."""
    if not headlines:
        return []
        
    if not GEMINI_API_KEY:
        print("Missing GEMINI_API_KEY environment variable.")
        return []

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    Analyze these headlines for an art project. 
    Return a JSON array of objects only. No markdown.
    Format: [{{"text": "headline", "score": -15 to 15, "category": "TECH", "color_hex": "#00ffff", "geometry": "FLUID"}}]
    
    Headlines: {headlines}
    """
    
    # Pre-emptive cooldown for Free Tier
    print("Initiating 65-second Safety Minute to protect API quota...")
    time.sleep(65)
    
    try:
        # FIX: Added 'models/' prefix which is often required by the SDK to avoid 404 errors
        response = client.models.generate_content(
            model="models/gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1 
            )
        )
        
        if not response or not response.text:
            raise ValueError("Empty response from Gemini API")
            
        result = json.loads(response.text)
        
        if not isinstance(result, list):
            return [result] if isinstance(result, dict) else []
            
        return result

    except Exception as e:
        print(f"Gemini Error: {e}")
        # FALLBACK: Prevents blank files
        return [{
            "text": "NEURAL FEED STABILIZED: VISUALIZING SEED ARCHITECTURE.",
            "score": 2.5,
            "category": "SYSTEM",
            "color_hex": "#00ffcc",
            "geometry": "FLUID"
        }]

def main():
    print("--- STARTING NEURAL DATA UPDATE ---")
    
    headlines = fetch_filtered_news()
    
    if not headlines:
        headlines = [
            "Neural network synchronization in progress", 
            "Global data streams stabilized",
            "Autonomous architecture visualizing current trends"
        ]

    data = analyze_sentiment(headlines)
    
    try:
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"SUCCESS: Successfully written {len(data)} items to {OUTPUT_PATH}")
    except Exception as e:
        print(f"File System Error: {e}")

if __name__ == "__main__":
    main()
