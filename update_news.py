import os
import json
import requests
from google import genai
from datetime import datetime
import random

# 1. Setup API Keys
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def get_news():
    """Fetches news with multiple fallback queries to ensure data is found."""
    # We try 'everything' with popular keywords instead of just 'top-headlines'
    # as it is more reliable for free-tier API keys.
    search_queries = ['technology', 'science', 'space', 'environment', 'world news']
    random.shuffle(search_queries)
    
    for query in search_queries:
        print(f"Attempting to fetch news for: {query}...")
        url = f'https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize=10&apiKey={NEWS_API_KEY}'
        
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            if data.get('status') == 'ok' and data.get('articles'):
                titles = [a['title'] for a in data['articles'] if a.get('title') and len(a['title']) > 10]
                if titles:
                    print(f"Success! Found {len(titles)} articles.")
                    return titles[:8] # Return top 8
            else:
                print(f"Query '{query}' returned no results or error: {data.get('message')}")
        except Exception as e:
            print(f"Request error for '{query}': {e}")
            
    return []

def analyze_sentiment(news_titles):
    """Uses Gemini 2.5 Flash to process news into visual metadata."""
    if not news_titles:
        print("No titles provided to Gemini.")
        return None

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    You are the neural core of a light installation. 
    Analyze these headlines: {news_titles}
    
    Return a JSON list of objects. Each object MUST have:
    1. "text": A 3-5 word poetic summary in ALL CAPS.
    2. "score": A float from -10.0 to 10.0.
    3. "global_state": "GOLD" (if positive/growth), "RED" (if crisis/danger), or "RAINBOW" (neutral).
    4. "resonances": A list of 7 floats (0.0 to 1.0) for 7 nodes.
    5. "ml_metrics": {{"confidence": float, "latency": int, "entropy": float, "drift_score": float}}
    
    Ensure the JSON is valid and contains no extra text.
    """

    try:
        print("Contacting Gemini for sentiment analysis...")
        response = client.models.generate_content(
            model='gemini-2.5-flash-preview-09-2025',
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini Analysis Failed: {e}")
        return None

def main():
    print(f"--- STARTING NEURAL UPDATE: {datetime.now()} ---")
    
    if not NEWS_API_KEY or not GEMINI_API_KEY:
        print("CRITICAL ERROR: API Keys missing from environment secrets.")
    
    titles = get_news()
    processed_data = analyze_sentiment(titles)

    if not processed_data:
        print("CRITICAL: Both News and Gemini failed. Deploying emergency fallback.")
        processed_data = [{
            "text": "DATA_STREAM_INTERRUPTED", 
            "score": 0.0, 
            "global_state": "RAINBOW",
            "resonances": [0.2]*7,
            "ml_metrics": {"confidence": 0.5, "latency": 5, "entropy": 1.5, "drift_score": 0.9}
        }]

    os.makedirs('data', exist_ok=True)
    with open('data/news.json', 'w') as f:
        json.dump(processed_data, f, indent=2)
    
    print(f"--- UPDATE COMPLETE: Written to data/news.json ---")

if __name__ == "__main__":
    main()
