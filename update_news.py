import os
import json
import requests
from google import genai

# Configuration - These variables are pulled from your GitHub Repository Secrets
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OUTPUT_PATH = "data/news.json"

def fetch_filtered_news():
    """Fetches news based on curated topics, excluding crime and scams."""
    # Updated query to include your requested topics + high-impact categories for visual contrast
    topics = [
        "technology", "science", "space exploration", "art", 
        "markets", "economy", "global warming", "climate change", 
        "war", "geopolitics", "cybersecurity", "human rights"
    ]
    
    query_string = " OR ".join(f'"{topic}"' for topic in topics)
    # Fixed the quote error on the line below to ensure the script runs correctly
    exclude = "NOT (crime OR scam OR murder OR fraud OR theft OR 'lottery')"
    full_query = f"({query_string}) {exclude}"
    
    # We use 'everything' to get a broader range of global perspectives
    url = f"https://newsapi.org/v2/everything?q={full_query}&language=en&sortBy=relevancy&pageSize=20&apiKey={NEWS_API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        # Extract titles from the top 12 articles for more visual variety
        return [a["title"] for a in articles[:12] if a.get("title")]
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
    2. "score": A float from -15.0 (negative/tension) to 15.0 (positive/uplifting).
    3. "type": "HIGH_POS" if score > 10, "HIGH_NEG" if score < -10, else "NEUTRAL".
    
    Headlines: {headlines}
    
    Return ONLY a valid JSON array of objects. Do not include markdown formatting.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-09-2025",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
            }
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error during sentiment analysis: {e}")
        return []

def main():
    print("Initiating Enhanced Curated News Update...")
    
    # 1. Fetch filtered news based on specific topics
    headlines = fetch_filtered_news()
    if not headlines:
        print("No headlines found matching criteria. Aborting.")
        return
    
    # 2. Analyze with Gemini
    print(f"Analyzing {len(headlines)} curated headlines...")
    data = analyze_sentiment(headlines)
    
    if not data:
        print("Analysis failed. Aborting.")
        return
    
    # 3. Save to data/news.json
    print(f"Saving updated data to {OUTPUT_PATH}...")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    
    print("Update Successful. Topics: Markets, Climate, War, Tech, and Science.")

if __name__ == "__main__":
    main()
