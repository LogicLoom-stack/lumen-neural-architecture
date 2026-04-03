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
    """Fetches a small, curated list of headlines with multiple safety fallbacks."""
    if not NEWS_API_KEY:
        print("CRITICAL: NEWS_API_KEY missing.")
        return []

    # Using 'everything' for broader results, limited to 5 for token efficiency
    topics = "technology OR space OR innovation"
    url = f"https://newsapi.org/v2/everything?q=({topics})&language=en&sortBy=relevancy&pageSize=5&apiKey={NEWS_API_KEY}"
    
    try:
        print("Step 1: Accessing News Stream...")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
        
        headlines = [a["title"] for a in articles[:5] if a.get("title") and len(a["title"]) > 5]
        
        if not headlines:
            print("Step 1b: No news found, using hardcoded system headlines.")
            return ["Neural network synchronization in progress", "Global data streams stabilized"]
            
        return headlines
    except Exception as e:
        print(f"News API Error: {e}")
        return ["Neural network synchronization in progress", "Global data streams stabilized"]

def analyze_sentiment(headlines):
    """
    Analyzes headlines using a multi-model fallback loop to prevent 404s 
    and a safety buffer to prevent 429s.
    """
    if not GEMINI_API_KEY:
        print("CRITICAL: GEMINI_API_KEY missing.")
        return []

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    Analyze these headlines for an art project. 
    Return a JSON array of objects only. No markdown formatting.
    Format: [{{"text": "string", "score": -15 to 15, "category": "TECH", "color_hex": "#00ffff", "geometry": "FLUID"}}]
    
    Headlines: {headlines}
    """
    
    # FORCED COOLDOWN: Essential for GitHub Actions Free Tier
    print("Step 2: Initiating 65-second Safety Minute (Prevents 429 Quota errors)...")
    time.sleep(65)
    
    # MULTI-MODEL FALLBACK LIST: Solves the 404 issue once and for all
    models_to_try = ["gemini-2.0-flash-lite", "gemini-1.5-flash", "models/gemini-1.5-flash"]
    
    for model_name in models_to_try:
        try:
            print(f"Step 3: Attempting analysis with model: {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1 
                )
            )
            
            if response and response.text:
                result = json.loads(response.text)
                print(f"SUCCESS: Analysis completed using {model_name}")
                return result if isinstance(result, list) else [result]
                
        except Exception as e:
            error_msg = str(e).upper()
            if "404" in error_msg:
                print(f"Model {model_name} not found, trying next option...")
                continue
            elif "429" in error_msg or "QUOTA" in error_msg:
                print("Rate limit hit during loop. Waiting 30s...")
                time.sleep(30)
            else:
                print(f"Unexpected error with {model_name}: {e}")
                
    # FINAL FALLBACK: If all models fail, return a simulated data point so the UI works
    print("ALL MODELS FAILED: Providing simulated art data.")
    return [{
        "text": "LUMEN CORE: NEURAL ARCHITECTURE ONLINE (RECOVERY MODE)",
        "score": 4.5,
        "category": "SYSTEM",
        "color_hex": "#00ffcc",
        "geometry": "FLUID"
    }]

def main():
    print("--- STARTING COMPREHENSIVE DATA UPDATE ---")
    
    headlines = fetch_filtered_news()
    data = analyze_sentiment(headlines)
    
    try:
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"FINAL STEP: Successfully written {len(data)} items to {OUTPUT_PATH}")
    except Exception as e:
        print(f"File System Error: {e}")

if __name__ == "__main__":
    main()
