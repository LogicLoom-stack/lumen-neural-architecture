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
    """Fetches a very small, highly-curated list of headlines to save API quota."""
    # Restricted query for quality over quantity
    topics = "technology OR space OR innovation"
    exclude = "NOT (crime OR scam OR murder OR fraud)"
    
    # Strictly 5 articles to keep token counts very low
    url = f"https://newsapi.org/v2/everything?q=({topics}) {exclude}&language=en&sortBy=relevancy&pageSize=5&apiKey={NEWS_API_KEY}"
    
    try:
        print("Accessing Curated News Stream (Limited Volume)...")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        
        # Fallback to a single top headline if the main search is empty
        if not articles:
            print("No targeted news found. Falling back to single top tech headline...")
            fallback_url = f"https://newsapi.org/v2/top-headlines?category=technology&language=en&pageSize=1&apiKey={NEWS_API_KEY}"
            response = requests.get(fallback_url, timeout=15)
            articles = response.json().get("articles", [])

        return [a["title"] for a in articles[:5] if a.get("title") and len(a["title"]) > 10]
    except Exception as e:
        print(f"News API Error: {e}")
        return []

def analyze_sentiment(headlines):
    """Analyzes headlines with a strict 'Safety Minute' for Free Tier reliability."""
    if not headlines:
        return []
        
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Ultra-compact prompt for free tier reliability
    prompt = f"""
    Analyze these headlines for an art project. 
    Return a JSON array of objects:
    [{{"text": "headline", "score": -15 to 15, "category": "TECH", "color_hex": "#00ffff", "geometry": "FLUID"}}]
    
    Headlines: {headlines}
    """
    
    # FREE TIER STRATEGY:
    # Most free tiers allow 1-2 requests per minute. 
    # By waiting 65 seconds upfront, we guarantee we start in a clean window.
    print("Initiating 65-second 'Safety Minute' to clear Free Tier quota...")
    time.sleep(65)
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Updated model name to 'gemini-1.5-flash-latest' to resolve 404 NOT_FOUND errors
            response = client.models.generate_content(
                model="gemini-1.5-flash-latest",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1 
                )
            )
            return json.loads(response.text)
            
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e).upper():
                # On Free Tier, a 429 means you must wait for the next minute.
                wait_time = 70 
                print(f"Rate limit still active. Waiting {wait_time}s for next quota window... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                print(f"Gemini Error: {e}")
                break
                
    return []

def main():
    print("--- STARTING MINIMALIST NEURAL UPDATE (FREE TIER MODE) ---")
    
    headlines = fetch_filtered_news()
    if not headlines:
        print("FAILED: No headlines retrieved.")
        data = []
    else:
        print(f"Processing {len(headlines)} headlines...")
        data = analyze_sentiment(headlines)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    
    if data:
        print(f"SUCCESS: {len(data)} items saved to {OUTPUT_PATH}")
    else:
        print("ERROR: Data was not processed. Please wait 2-3 minutes before running the action again manually.")

if __name__ == "__main__":
    main()
