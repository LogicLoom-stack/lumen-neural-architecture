import os
import json
import random
import time
from google import genai
from datetime import datetime

# 1. Setup API Keys
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# 2. LOCAL DATASET (2026 News Pool)
NEWS_DATASET = {
    "positive": [
        "Artemis II completes lunar flyby, marking humanity's return to deep space.",
        "First personalized CRISPR treatment successfully cures rare genetic disorder in child.",
        "Quantum-assisted carbon capture reaching 95% efficiency in European pilots.",
        "Global High Seas Treaty officially ratified, protecting 30% of world oceans.",
        "AI-powered 'World Models' predict agricultural yields with 99% accuracy, ending localized famine.",
        "Solid-state battery breakthrough doubles EV range while halving charge time.",
        "Universal nasal spray vaccine for COVID and Flu enters mass production."
    ],
    "neutral": [
        "NASA Nancy Grace Roman Telescope fully assembled and awaiting fall launch.",
        "Global growth projected at steady 3.3% for 2026 amid divergent tech forces.",
        "Companies shift AI focus from 'hype' to measurable ROI and infrastructure.",
        "UN Desertification COP 17 opens in Mongolia to discuss grassland restoration.",
        "New 'folding' hardware forms dominate the 2026 mobile market.",
        "BepiColombo mission enters Mercury orbit after seven-year journey.",
        "Central banks move toward neutral interest rates as inflation stabilizes."
    ],
    "negative": [
        "WMO warns planet's climate is more out of balance than at any time in history.",
        "Major 1.5°C climate overshoot predicted for the 2025-2029 window.",
        "Geoeconomic confrontation cited as top risk for 2026 global stability.",
        "Underpriced climate risks threaten to burst $15 trillion global asset bubble.",
        "Ultra-processed food links to surge in cardiovascular cases among youth.",
        "State-based armed conflicts increase pressure on multilateral trade systems.",
        "E-waste levels hit all-time high as hardware replacement cycles accelerate."
    ]
}

def get_curated_news():
    mood = random.choice(["positive", "neutral", "negative", "mixed"])
    if mood == "mixed":
        pool = NEWS_DATASET["positive"] + NEWS_DATASET["neutral"] + NEWS_DATASET["negative"]
        selected = random.sample(pool, 5)
    else:
        pool = NEWS_DATASET[mood]
        selected = random.sample(pool, min(len(pool), 5))
        selected += random.sample(NEWS_DATASET["neutral"], 2)
    return mood, selected

def analyze_sentiment(mood, news_titles):
    """Uses Gemini 2.5 Flash with exponential backoff and local fallback."""
    if not GEMINI_API_KEY:
        return local_fallback(mood, news_titles)

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
    Analyze these 2026 news events: {news_titles}
    Synthesize them into a single 'Global State' for a generative art piece.
    Return a JSON list with 1 object:
    {{
      "text": "3-5 WORD POETIC SUMMARY",
      "score": float (-10.0 to 10.0), 
      "global_state": "GOLD" | "RED" | "RAINBOW",
      "resonances": [7 floats 0-1],
      "ml_metrics": {{"confidence": 0.98, "latency": 5, "entropy": 0.2, "drift_score": 0.01}}
    }}
    """

    # Exponential Backoff Implementation
    for i in range(5):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash-preview-09-2025',
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            return json.loads(response.text)
        except Exception as e:
            wait_time = (2 ** i)
            print(f"Gemini attempt {i+1} failed. Retrying in {wait_time}s...")
            time.sleep(wait_time)

    print("Gemini unreachable after 5 attempts. Using local synthesis.")
    return local_fallback(mood, news_titles)

def local_fallback(mood, titles):
    """Calculates art parameters locally if AI is unavailable."""
    score_map = {"positive": 7.5, "negative": -7.5, "neutral": 0.0, "mixed": 1.2}
    state_map = {"positive": "GOLD", "negative": "RED", "neutral": "RAINBOW", "mixed": "RAINBOW"}
    
    return [{
        "text": f"LOCAL_{mood.upper()}_SYNTHESIS",
        "score": score_map.get(mood, 0.0),
        "global_state": state_map.get(mood, "RAINBOW"),
        "resonances": [random.uniform(0.1, 0.9) for _ in range(7)],
        "ml_metrics": {"confidence": 1.0, "latency": 0, "entropy": 0.1, "drift_score": 0.0}
    }]

def main():
    print(f"--- INITIATING NEURAL SCAN: {datetime.now()} ---")
    mood, titles = get_curated_news()
    processed_data = analyze_sentiment(mood, titles)

    os.makedirs('data', exist_ok=True)
    with open('data/news.json', 'w') as f:
        json.dump(processed_data, f, indent=2)
    
    print(f"Scan complete. Visual state: {processed_data[0]['global_state']}")

if __name__ == "__main__":
    main()
