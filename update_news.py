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
    """Fetches a small, curated list of headlines with fallback logic."""
    if not NEWS_API_KEY:
        print("CRITICAL: NEWS_API_KEY missing.")
        return []

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
            return ["Neural network synchronization in progress", "Global data streams stabilized"]
            
        return headlines
    except Exception as e:
        print(f"News API Error: {e}")
        return ["Neural network synchronization in progress", "Global data streams stabilized"]

def analyze_sentiment(headlines):
    """
    Analyzes headlines using a more robust model selection and 
    longer wait times to bypass free-tier busy signals.
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
    print("Step 2: Initiating 70-second Safety Minute...")
    time.sleep(70)
    
    # Priority list optimized for Free Tier stability
    models_to_try = ["gemini-1.5-flash-latest", "gemini-1.5-flash", "gemini-2.0-flash-lite"]
    
    for model_name in models_to_try:
        max_retries = 2
        for attempt in range(max_retries):
            try:
                print(f"Step 3: Attempting analysis with {model_name} (Attempt {attempt+1})...")
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
                    print(f"Model {model_name} not recognized. Skipping.")
                    break # Move to next model name
                elif "429" in error_msg or "QUOTA" in error_msg or "EXHAUSTED" in error_msg:
                    wait = 45 # Significant wait to clear the per-minute quota
                    print(f"API Busy (429). Waiting {wait}s for quota reset...")
                    time.sleep(wait)
                else:
                    print(f"Model error: {e}")
                    break 
                
    # FINAL FALLBACK: Ensures data is always updated even if AI is offline
    print("ALL AI MODELS BUSY: Using high-fidelity simulation data.")
    return [{
        "text": "LUMEN NEURAL CORE: FEED STABILIZED. ARCHITECTURE ADAPTING TO TRENDS.",
        "score": 6.5,
        "category": "SYSTEM",
        "color_hex": "#00ffcc",
        "geometry": "FLUID"
    }]

def main():
    print("--- STARTING FINAL ROBUST UPDATE ---")
    
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
