import os
import json
import requests
import time
import random
from google import genai
from google.genai import types

# Configuration
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OUTPUT_PATH = "data/news.json"

# High-vibrancy fallback stream to prevent "System Neutral" during API downtime
FALLBACK_NEWS = [
    "Quantum entanglement achieved at room temperature",
    "Global reforestation efforts reach record milestone",
    "Deep space signals confirm geometric origin",
    "New fusion reactor maintains stability for 48 hours",
    "Global economic index shifts toward decentralized growth",
    "Breakthrough in neural-link biocompatibility reported",
    "First successful carbon-negative city infrastructure launched",
    "Rare planetary alignment triggers geomagnetic shifts"
]

def fetch_filtered_news():
    """Fetches real-time headlines with an automatic fallback to a synthetic stream."""
    if not NEWS_API_KEY:
        print("No API Key: Loading synthetic stream...")
        return random.sample(FALLBACK_NEWS, 5)

    queries = ["tech innovation", "environmental crisis", "medical breakthrough", "space exploration", "global economy"]
    query = random.choice(queries)
    
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize=12&apiKey={NEWS_API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        articles = data.get("articles", [])
        titles = [a["title"] for a in articles if a.get("title")]
        
        if not titles:
            print("API returned empty: Loading synthetic stream...")
            return random.sample(FALLBACK_NEWS, 5)
            
        return titles
    except Exception as e:
        print(f"Fetch failed: {e}. Loading synthetic stream...")
        return random.sample(FALLBACK_NEWS, 5)

def analyze_sentiment(headlines):
    """Analyzes headlines and maps them to complex multi-chakra energy signatures with ML telemetry."""
    if not GEMINI_API_KEY:
        return [{"text": "OFFLINE_MODE", "score": 0, "resonances": [0.5]*7, "global_state": "RAINBOW", "ml_metrics": {"confidence": 0.5, "latency": 0, "entropy": 1.0, "drift_score": 0.5, "tokens": 0}}]

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    Analyze these headlines for the Lumen Visualizer. 
    Return a JSON array of objects. 
    Each object must have:
    - 'text': Shortened headline (max 40 chars).
    - 'score': Overall sentiment intensity (-10 to 10).
    - 'global_state': 'GOLD' (Positive/Progress), 'RED' (Crisis/Conflict), or 'RAINBOW' (Neutral/Balanced) based on score.
    - 'resonances': Array of 7 floats (0 to 1.0) for chakra flares.
    - 'ml_metrics': An object containing futuristic ML monitoring data:
        - 'confidence': (0.0 to 1.0) Model's certainty in this classification.
        - 'latency': (integer, 10-500) Simulated inference time in ms.
        - 'entropy': (0.0 to 2.0) Prediction uncertainty.
        - 'drift_score': (0.0 to 1.0) How far this data is from the training baseline.
        - 'tokens': (integer, 5-25) Number of linguistic units processed.
    
    Headlines: {headlines}
    """
    
    models_to_try = ["gemini-2.5-flash-preview-09-2025", "gemini-2.0-flash"]
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            if response and response.text:
                return json.loads(response.text)
        except Exception:
            continue

    # Final fallback if LLM is unreachable
    return [{
        "text": "SYNTHETIC_SIGNAL_STABLE", 
        "score": 0, 
        "resonances": [0.3]*7, 
        "global_state": "RAINBOW", 
        "ml_metrics": {"confidence": 0.99, "latency": 15, "entropy": 0.05, "drift_score": 0.01, "tokens": 12}
    }]

def main():
    headlines = fetch_filtered_news()
    results = analyze_sentiment(headlines)
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
