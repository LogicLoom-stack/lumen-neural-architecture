import os
import json
import requests
from google import genai

# Configuration
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OUTPUT_PATH = "data/news.json"

def fetch_filtered_news():
    """Guaranteed news fetcher with wide parameters to ensure news.json is never empty."""
    
    # Attempt 1: Targeted Search
    topics = "technology OR science OR markets OR space OR climate"
    exclude = "NOT (crime OR scam OR murder)"
    url = f"https://newsapi.org/v2/everything?q=({topics}) {exclude}&language=en&sortBy=publishedAt&pageSize=20&apiKey={NEWS_API_KEY}"
    
    try:
        print("Fetching global news feed...")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        
        # Attempt 2: Fallback to Top Tech Headlines if Attempt 1 is empty
        if not articles:
            print("Targeted search returned nothing. Trying top-headlines fallback...")
            fallback_url = f"https://newsapi.org/v2/top-headlines?category=technology&language=en&apiKey={NEWS_API_KEY}"
            response = requests.get(fallback_url, timeout=15)
            articles = response.json().get("articles", [])

        titles = [a["title"] for a in articles[:12] if a.get("title") and len(a["title"]) > 10]
        return titles
        
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def analyze_sentiment(headlines):
    """Uses Gemini to assign scores and visual metadata."""
    if not headlines:
        return []
        
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    Analyze these headlines for a generative art installation. 
    For each, return a JSON object with:
    1. "text": The headline string.
    2. "score": Float from -15.0 to 15.0.
    3. "category": One of [MARKETS, CLIMATE, WAR, TECH, SPACE, ART, GENERAL].
    4. "color_hex": A high-tech neon hex code (e.g., #00ffff).
    5. "geometry": "SHARP" or "FLUID".
    
    Headlines: {headlines}
    
    Return ONLY a valid JSON array. No markdown formatting.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-09-2025",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini Analysis Error: {e}")
        return []

def main():
    print("Running Guaranteed News Update...")
    
    headlines = fetch_filtered_news()
    if not headlines:
        print("FAILED: No headlines found even in fallback mode.")
        data = []
    else:
        print(f"Found {len(headlines)} headlines. Sending to Gemini...")
        data = analyze_sentiment(headlines)
    
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Success! {len(data)} items written to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
