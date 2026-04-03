import os
import json
import random
import time
from google import genai
from datetime import datetime

# 1. Setup API Keys (Optional if you want manual-only control)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# 2. ENHANCED LOCAL DATASET (Manual Sentiment Mapping)
# You can now manually define the score (-10 to 10) and state for each headline.
NEWS_DATASET = {
    "positive": [
        {"title": "Artemis II completes lunar flyby, marking humanity's return to deep space.", "score": 9.0, "state": "GOLD"},
        {"title": "First personalized CRISPR treatment successfully cures rare genetic disorder.", "score": 8.5, "state": "GOLD"},
        {"title": "Quantum-assisted carbon capture reaching 95% efficiency in European pilots.", "score": 7.0, "state": "GOLD"},
        {"title": "Global High Seas Treaty officially ratified, protecting 30% of world oceans.", "score": 7.5, "state": "GOLD"}
    ],
    "neutral": [
        {"title": "NASA Nancy Grace Roman Telescope fully assembled and awaiting fall launch.", "score": 0.5, "state": "RAINBOW"},
        {"title": "Global growth projected at steady 3.3% for 2026.", "score": 0.0, "state": "RAINBOW"},
        {"title": "Companies shift AI focus from 'hype' to measurable ROI.", "score": -0.5, "state": "RAINBOW"},
        {"title": "New 'folding' hardware forms dominate the 2026 mobile market.", "score": 0.2, "state": "RAINBOW"}
    ],
    "negative": [
        {"title": "WMO warns planet's climate is more out of balance than ever.", "score": -9.0, "state": "RED"},
        {"title": "Major 1.5°C climate overshoot predicted for the 2025-2029 window.", "score": -8.5, "state": "RED"},
        {"title": "Geoeconomic confrontation cited as top risk for 2026 stability.", "score": -7.0, "state": "RED"},
        {"title": "Ultra-processed food links to surge in cardiovascular cases among youth.", "score": -6.5, "state": "RED"}
    ]
}

def get_curated_news():
    mood = random.choice(["positive", "neutral", "negative", "mixed"])
    if mood == "mixed":
        pool = NEWS_DATASET["positive"] + NEWS_DATASET["neutral"] + NEWS_DATASET["negative"]
    else:
        pool = NEWS_DATASET[mood]
    
    selected = random.sample(pool, min(len(pool), 5))
    return mood, selected

def analyze_sentiment(mood, selected_items):
    """
    If API Key exists, use Gemini for poetic synthesis.
    Otherwise, use the manual scores defined in the dataset.
    """
    titles = [item["title"] for item in selected_items]
    
    if not GEMINI_API_KEY:
        print("No API Key found. Using manual dataset values.")
        return local_manual_synthesis(mood, selected_items)

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
    Analyze these 2026 news events: {titles}
    Synthesize them into a single 'Global State' for a generative art piece.
    Return a JSON list with 1 object:
    {{
      "text": "3-5 WORD POETIC SUMMARY",
      "articles": ["Headline 1", "Headline 2", ...],
      "score": float (-10.0 to 10.0), 
      "global_state": "GOLD" | "RED" | "RAINBOW",
      "resonances": [7 floats 0-1],
      "ml_metrics": {{"confidence": 0.98, "latency": 5, "entropy": 0.2, "drift_score": 0.01}}
    }}
    """

    for i in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash-preview-09-2025',
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            return json.loads(response.text)
        except Exception as e:
            time.sleep(2 ** i)

    return local_manual_synthesis(mood, selected_items)

def local_manual_synthesis(mood, items):
    """Calculates state by averaging the manual scores in the dataset."""
    avg_score = sum(item["score"] for item in items) / len(items)
    titles = [item["title"] for item in items]
    
    # Determine state based on average
    if avg_score > 3.0:
        state = "GOLD"
    elif avg_score < -3.0:
        state = "RED"
    else:
        state = "RAINBOW"
    
    return [{
        "text": f"MANUAL {mood.upper()} ALIGNMENT",
        "articles": titles,
        "score": round(avg_score, 2),
        "global_state": state,
        "resonances": [random.uniform(0.1, 0.9) for _ in range(7)],
        "ml_metrics": {"confidence": 1.0, "latency": 0, "entropy": 0.0, "drift_score": 0.0}
    }]

def main():
    print(f"--- INITIATING SYSTEM SCAN: {datetime.now()} ---")
    mood, selected_items = get_curated_news()
    processed_data = analyze_sentiment(mood, selected_items)

    os.makedirs('data', exist_ok=True)
    with open('data/news.json', 'w') as f:
        json.dump(processed_data, f, indent=2)
    
    print(f"Update complete. Mode: {'AI-Synthesized' if GEMINI_API_KEY else 'Manual-Override'}")
    print(f"Visual State: {processed_data[0]['global_state']} (Score: {processed_data[0]['score']})")

if __name__ == "__main__":
    main()
