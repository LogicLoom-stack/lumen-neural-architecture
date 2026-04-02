import os
import json
import requests
from datetime import datetime, timedelta
from google import genai

# Configuration
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OUTPUT_PATH = "data/news.json"

def fetch_filtered_news():
    """Fetches news from the last 48 hours to ensure relevance and speed."""
    
    # Calculate date range (Last 48 hours)
    # This prevents the API from searching the entire historical database
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    
    topics = [
        "technology", "science", "space", "art", 
        "markets", "economy", "climate change", 
        "geopolitics", "innovation"
    ]
    query_string = " OR ".join(f'"{topic}"' for topic in topics)
    exclude = "NOT (crime OR scam OR murder OR fraud OR theft)"
    
    queries = [
        f"({query_string}) {exclude}", 
        "business OR technology", 
        "innovation"
    ]

    for q in queries:
        # Added 'from' and 'to' parameters to restrict the search to recent news
        url = (
            f"https://newsapi.org/v2/everything?q={q}"
            f"&from={yesterday}&to={today}"
            f"&language=en&sortBy=relevancy&pageSize=15&apiKey={NEWS_API_KEY}"
        )
        
        try:
            print(f"Attempting query for period {yesterday} to {today}: {q[:30]}...")
            response = requests.get(url, timeout=10) 
            response.raise_for_status()
            articles = response.json().get("articles", [])
            
            # Filter out very short titles or broken data
            titles = [a["title"] for a in articles[:10] if a.get("title") and len(a["title"]) > 15]
            
            if titles:
                print(f"Success! Found {len(titles)} recent headlines.")
                return titles
        except Exception as e:
            print(f"Query attempt failed: {e}")
            continue
            
    return []

def analyze_sentiment(headlines):
    """Uses Gemini to assign scores and visual metadata."""
    if not headlines:
        return []
        
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    Analyze these recent headlines for a generative art installation. 
    For each, return a JSON object with:
    1. "text": The headline string.
    2. "score": Float from -15.0 to 15.0.
    3. "category": One of [MARKETS, CLIMATE, WAR, TECH, SPACE, HUMAN_RIGHTS, ART, GENERAL].
    4. "color_hex": A high-tech neon hex code reflecting the topic.
    5. "geometry": "SHARP" for negative/tense news, "FLUID" for positive/breakthroughs.
    
    Headlines: {headlines}
    
    Return ONLY a valid JSON array.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-09-2025",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error during Gemini analysis: {e}")
        return []

def main():
    print("Initiating Temporal-Aware News Update...")
    
    headlines = fetch_filtered_news()
    if not headlines:
        print("CRITICAL: No recent headlines found. Writing empty array.")
        data = []
    else:
        print(f"Analyzing {len(headlines)} headlines with Gemini...")
        data = analyze_sentiment(headlines)
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Update Finished. news.json contains {len(data)} items.")

if __name__ == "__main__":
    main()
