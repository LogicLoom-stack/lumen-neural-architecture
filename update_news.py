import os
import json
import requests
from google import genai

# Configuration
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OUTPUT_PATH = "data/news.json"

def fetch_filtered_news():
    """Fetches news with multiple fallback attempts to avoid empty results."""
    # Attempt 1: Your specific curated topics
    topics = [
        "technology", "science", "space", "art", 
        "markets", "economy", "climate change", 
        "geopolitics", "innovation"
    ]
    query_string = " OR ".join(f'"{topic}"' for topic in topics)
    exclude = "NOT (crime OR scam OR murder OR fraud OR theft)"
    
    # Try different endpoints/queries if the first one fails
    queries = [
        f"({query_string}) {exclude}", # Targeted search
        "world news OR business OR technology", # Broad fallback
        "latest breaking news" # Final fallback
    ]

    for q in queries:
        url = f"https://newsapi.org/v2/everything?q={q}&language=en&sortBy=relevancy&pageSize=20&apiKey={NEWS_API_KEY}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            articles = response.json().get("articles", [])
            titles = [a["title"] for a in articles[:12] if a.get("title") and len(a["title"]) > 10]
            if titles:
                print(f"Success! Found news using query: {q[:50]}...")
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
    Analyze these headlines for a generative art installation. 
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
    print("Initiating Robust Art-Driven News Update...")
    
    headlines = fetch_filtered_news()
    if not headlines:
        print("CRITICAL: All news fetch attempts returned empty. Writing empty array.")
        data = []
    else:
        print(f"Analyzing {len(headlines)} headlines...")
        data = analyze_sentiment(headlines)
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Update Finished. news.json contains {len(data)} items.")

if __name__ == "__main__":
    main()
