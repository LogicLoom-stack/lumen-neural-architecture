import os
import json
import requests
from google import genai

# Configuration - These variables are pulled from your GitHub Repository Secrets
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OUTPUT_PATH = "data/news.json"

def fetch_top_headlines():
    """Fetches the latest global headlines using NewsAPI."""
    # Ensure you have a NewsAPI key from newsapi.org
    url = f"https://newsapi.org/v2/top-headlines?language=en&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        # Extract titles from the first 10 articles
        return [a["title"] for a in articles[:10] if a.get("title")]
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def analyze_sentiment(headlines):
    """Uses Gemini to assign sentiment scores to each headline."""
    if not headlines:
        return []
        
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    Analyze the sentiment of these headlines for a data-art installation. 
    For each headline, return a JSON object with:
    1. "text": The headline string.
    2. "score": A float from -15.0 (extremely negative/crisis) to 15.0 (extremely positive/breakthrough).
    3. "type": "HIGH_POS" if score > 10, "HIGH_NEG" if score < -10, else "NEUTRAL".
    
    Headlines: {headlines}
    
    Return ONLY a valid JSON array of objects. Do not include markdown formatting or explanations.
    """
    
    try:
        # Using the specific preview model supported in this environment
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-09-2025",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
            }
        )
        # Parse the JSON string from the response
        return json.loads(response.text)
    except Exception as e:
        print(f"Error during sentiment analysis: {e}")
        return []

def main():
    print("Initiating News Sentiment Update...")
    
    # 1. Fetch news
    headlines = fetch_top_headlines()
    if not headlines:
        print("No headlines found. Aborting.")
        return
    
    # 2. Analyze with Gemini
    print(f"Analyzing {len(headlines)} headlines...")
    data = analyze_sentiment(headlines)
    
    if not data:
        print("Analysis failed. Aborting.")
        return
    
    # 3. Save to data/news.json
    print(f"Saving updated data to {OUTPUT_PATH}...")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    
    print("Update Successful.")

if __name__ == "__main__":
    main()
