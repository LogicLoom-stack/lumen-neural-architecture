import os
import json
import random
from google import genai
from datetime import datetime

# 1. Setup API Keys (Gemini is still used for creative synthesis)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# 2. LOCAL DATASET (2026 News Pool)
# Categorized for dynamic art response
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
    """Simulates a news fetch by selecting a mix of perspectives from our local 2026 dataset."""
    # We pick a random 'mood' for the day
    mood = random.choice(["positive", "neutral", "negative", "mixed"])
    
    if mood == "mixed":
        # Mix of everything
        pool = NEWS_DATASET["positive"] + NEWS_DATASET["neutral"] + NEWS_DATASET["negative"]
        selected = random.sample(pool, 5)
    else:
        # Heavily weighted toward the chosen mood
        pool = NEWS_DATASET[mood]
        selected = random.sample(pool, min(len(pool), 5))
        # Add 1-2 neutral ones for balance
        selected += random.sample(NEWS_DATASET["neutral"], 2)
        
    print(f"Neural Scan: Current global mood detected as '{mood.upper()}'.")
    return selected

def analyze_sentiment(news_titles):
    """Uses Gemini 2.5 Flash to synthesize the final visual state and poetic summary."""
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = f"""
        Analyze these 2026 news events: {news_titles}
        Synthesize them into a single 'Global State' for a generative art piece.
        Return a JSON list with 1 object:
        {{
          "text": "3-5 WORD POETIC SUMMARY",
          "score": float (-10.0 to 10.0), 
          "global_state": "GOLD" (if pos), "RED" (if neg), "RAINBOW" (if mixed/neutral),
          "resonances": [7 floats 0-1 representing visual harmonics],
          "ml_metrics": {{"confidence": 0.98, "latency": 5, "entropy": 0.2, "drift_score": 0.01}}
        }}
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash-preview-09-2025',
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini Synthesis Failed: {e}")
        # Local Fallback logic if Gemini is down
        return [{
            "text": "LOCAL DATA OVERRIDE",
            "score": 0.0,
            "global_state": "RAINBOW",
            "resonances": [0.5]*7,
            "ml_metrics": {"confidence": 1.0, "latency": 0, "entropy": 0.5, "drift_score": 0.0}
        }]

def main():
    print(f"--- INITIATING LOCAL TELEMETRY SCAN (2026 DATASET) ---")
    
    titles = get_curated_news()
    processed_data = analyze_sentiment(titles)

    os.makedirs('data', exist_ok=True)
    with open('data/news.json', 'w') as f:
        json.dump(processed_data, f, indent=2)
    
    print(f"Scan complete. Visual state set to: {processed_data[0]['global_state']}")
    print(f"Poetic Summary: {processed_data[0]['text']}")

if __name__ == "__main__":
    main()
