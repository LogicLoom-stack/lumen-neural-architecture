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
    """Fetches news using a high-probability search strategy."""
    # We broaden the search queries to be high-volume terms
    search_queries = [
        'artificial intelligence', 
        'global climate', 
        'breakthrough', 
        'future tech', 
        'astronomy',
        'quantum computing'
    ]
    random.shuffle(search_queries)
    
    for query in search_queries:
        print(f"Deep searching for: {query}...")
        
        # We switch to 'relevancy' instead of 'publishedAt' as free tiers
        # often throttle the newest results but allow relevant ones.
        url = (
            f'https://newsapi.org/v2/everything?'
            f'q={query}&'
            f'language=en&'
            f'sortBy=relevancy&'
            f'pageSize=15&'
            f'apiKey={NEWS_API_KEY}'
        )
        
        try:
            response = requests.get(url, timeout=15)
            data = response.json()
            
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                # Filter out 'Removed' or empty titles
                titles = [
                    a['title'] for a in articles 
                    if a.get('title') and "[Removed]" not in a['title'] and len(a['title']) > 15
                ]
                
                if titles:
                    print(f"Neural linkage established! Found {len(titles)} high-relevance articles.")
                    return titles[:10]
            else:
                # Log the specific API message (e.g. 'rateLimited', 'parameterInvalid')
                print(f"API rejection for '{query}': {data.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"Network error during search for '{query}': {e}")
            
    return []

def analyze_sentiment(news_titles):
    """Uses Gemini 2.5 Flash to process news into visual metadata."""
    if not news_titles:
        print("Neural core idle: No titles received.")
        return None

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    You are the neural core of a light installation. 
    Headlines: {news_titles}
    
    Synthesize this information. Return a JSON list of 1 object:
    1. "text": A 3-5 word poetic summary in ALL CAPS.
    2. "score": A float from -10.0 to 10.0 (Global Sentiment).
    3. "global_state": "GOLD" (if optimistic), "RED" (if chaotic), or "RAINBOW" (balanced).
    4. "resonances": A list of 7 floats (0.0 to 1.0) for visual nodes.
    5. "ml_metrics": {{"confidence": float, "latency": int, "entropy": float, "drift_score": float}}
    """

    try:
        print("Transmitting to Gemini for neural synthesis...")
        response = client.models.generate_content(
            model='gemini-2.5-flash-preview-09-2025',
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini Synthesis Failed: {e}")
        return None

def main():
    print(f"--- INITIATING GLOBAL TELEMETRY SCAN: {datetime.now()} ---")
    
    if not NEWS_API_KEY or not GEMINI_API_KEY:
        print("ERROR: API credentials missing.")
        return

    titles = get_news()
    processed_data = analyze_sentiment(titles)

    if not processed_data:
        print("CRITICAL: Stream collapsed. Generating synthetic data.")
        processed_data = [{
            "text": "SYSTEM_IDLE_CHECK_LOGS", 
            "score": 0.0, 
            "global_state": "RAINBOW",
            "resonances": [0.1]*7,
            "ml_metrics": {"confidence": 0.0, "latency": 0, "entropy": 0.0, "drift_score": 1.0}
        }]

    os.makedirs('data', exist_ok=True)
    with open('data/news.json', 'w') as f:
        json.dump(processed_data, f, indent=2)
    
    print(f"--- SCAN COMPLETE: Data written to news.json ---")

if __name__ == "__main__":
    main()
