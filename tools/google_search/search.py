import os
import requests
import json
import time
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

CACHE = {}
CACHE_TTL = 86400

def search_web(query: str, num_results: int = 5) -> Dict:
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    cache_key = f"{query}:{num_results}"
    if cache_key in CACHE:
        cached_data, cached_time = CACHE[cache_key]
        if time.time() - cached_time < CACHE_TTL:
            return cached_data
    
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {"key": api_key, "cx": engine_id, "q": query, "num": num_results}
        response = requests.get(url, params=params, timeout=10, verify=True)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("items", []):
            results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", "")
            })
        
        result = {"query": query, "results": results, "count": len(results)}
        CACHE[cache_key] = (result, time.time())
        return result
    except Exception as e:
        return {"error": str(e), "results": []}

def format_search_results(search_data: Dict) -> str:
    if search_data.get("error"):
        return f"Search failed: {search_data['error']}"
    
    results = search_data.get("results", [])
    
    output = f"Search: {search_data.get('query', '')}\n\n"
    for i, result in enumerate(results, 1):
        output += f"{i}. {result['title']}\n{result['snippet']}\n{result['link']}\n\n"
    return output
