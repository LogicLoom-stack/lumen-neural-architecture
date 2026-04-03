import os
import json
import random
import time
from google import genai
from datetime import datetime

# 1. Setup API Keys
# Ensure GEMINI_API_KEY is set in your environment or GitHub Secrets
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# 2. ENHANCED LOCAL DATASET (Used for curation or fallback)
NEWS_DATASET = {
    "positive": [
        {"title": "Artemis II completes lunar flyby, marking humanity's return to deep space.", "score": 9.2},
        {"title": "First personalized CRISPR treatment successfully cures rare genetic disorder.", "score": 8.8},
        {"title": "Quantum-assisted carbon capture reaching 95% efficiency in European pilots.", "score": 7.5},
        {"title": "Global High Seas Treaty officially ratified, protecting 30% of world oceans.", "score": 8.0}
    ],
    "neutral": [
        {"title": "NASA Nancy Grace Roman Telescope fully assembled and awaiting fall launch.", "score": 1.2},
        {"title": "Global growth projected at steady 3.3% for 2026.", "score": 0.0},
        {"title": "Companies shift AI focus from 'hype' to measurable ROI.", "score": -0.5},
        {"title": "New 'folding' hardware forms dominate the 2026 mobile market.", "score": 0.8}
    ],
    "negative": [
        {"title": "WMO warns planet's climate is more out of balance than ever.", "score": -9.5},
        {"title": "Major 1.5°C climate overshoot predicted for the 2025-2029 window.", "score": -8.8},
        {"title": "Geoeconomic confrontation cited as top risk for 2026 stability.", "score": -7.5},
        {"title": "Ultra-processed food links to surge in cardiovascular cases among youth.", "score": -6.0}
    ]
}

def get_curated_news():
    """Selects a mix of headlines to be analyzed."""
    mood = random.choice(["positive", "neutral", "negative", "mixed"])
    if mood == "mixed":
        pool = NEWS_DATASET["positive"] + NEWS_DATASET["neutral"] + NEWS_DATASET["negative"]
    else:
        pool = NEWS_DATASET[mood]
    return random.sample(pool, min(len(pool), 6))

def analyze_sentiment(selected_items):
    """Uses Gemini to assign granular scores and states to each individual headline."""
    titles = [item["title"] for item in selected_items]
    
    # Pre-formatted fallback data to prevent "INITIALIZING_STREAM" hangs
    fallback_data = {
        "global_summary": "SYNTHETIC EQUILIBRIUM",
        "articles": [
            {
                "title": i["title"], 
                "score": i["score"], 
                "state": "GOLD" if i["score"] > 3 else "RED" if i["score"] < -3 else "RAINBOW"
            } for i in selected_items
        ],
        "ml_metrics": {"confidence": 0.95, "latency": 10, "entropy": 0.12, "drift_score": 0.01}
    }

    if not GEMINI_API_KEY:
        print("No API Key found. Using manual dataset values.")
        return fallback_data

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # The prompt explicitly asks for per-headline analysis to drive the chakra colors
    prompt = f"""
    Analyze these 2026 news events: {titles}
    
    For EACH headline, perform a deep sentiment analysis:
    1. Assign an individual sentiment score from -10.0 (extreme negative) to 10.0 (extreme positive).
    2. Determine the visual 'state': 'GOLD' (score > 3), 'RED' (score < -3), or 'RAINBOW' (neutral/mixed).
    
    Also provide a 3-word global summary and ML performance metrics.
    
    Return the response as a valid JSON object:
    {{
      "global_summary": "3 WORD SUMMARY",
      "articles": [
        {{"title": "Headline string", "score": float, "state": "GOLD/RED/RAINBOW"}},
        ...
      ],
      "ml_metrics": {{
        "confidence": float (0-1),
        "latency": int (ms),
        "entropy": float,
        "drift_score": float
      }}
    }}
    """

    # Retry logic with exponential backoff
    for i in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash-preview-09-2025',
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Retry {i+1} due to error: {e}")
            time.sleep(2 ** i)

    # Return structured fallback instead of empty list to keep the UI active
    return fallback_data

def main():
    print(f"--- INITIATING NEURAL SCAN: {datetime.now()} ---")
    
    # 1. Gather headlines
    selected_items = get_curated_news()
    
    # 2. Analyze via Gemini
    processed_data = analyze_sentiment(selected_items)

    # 3. Guard against empty/malformed data
    if "ml_metrics" not in processed_data:
        processed_data["ml_metrics"] = {"confidence": 0.99, "latency": 5, "entropy": 0.05, "drift_score": 0.00}
    
    # 4. Save to the path expected by index.html
    os.makedirs('data', exist_ok=True)
    with open('data/news.json', 'w') as f:
        json.dump(processed_data, f, indent=2)
    
    print(f"Update complete. {len(processed_data.get('articles', []))} headlines synchronized.")
    print(f"Global Sentiment Flux initialized: {processed_data.get('global_summary')}")

if __name__ == "__main__":
    main()
