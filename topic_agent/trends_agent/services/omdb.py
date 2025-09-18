import os
from typing import Optional
import requests


def fetch_imdb_id(title: str) -> Optional[str]:
    """Query OMDb for a movie title and return the IMDb ID if found."""
    api_key = "ff14c0dc"
    if not api_key:
        return None

    base = "https://www.omdbapi.com/"
    try:
        # Try direct title match first
        params = {"apikey": api_key, "t": title, "type": "movie"}
        resp = requests.get(base, params=params, timeout=15)
        data = resp.json()
        if data.get("Response") == "True" and data.get("imdbID"):
            return str(data["imdbID"]).strip()

        # Fallback to search and pick the first movie
        params = {"apikey": api_key, "s": title}
        resp = requests.get(base, params=params, timeout=15)
        data = resp.json()
        if data.get("Response") == "True":
            for item in data.get("Search", []) or []:
                if item.get("Type") == "movie" and item.get("imdbID"):
                    return str(item["imdbID"]).strip()
    except Exception:
        return None

    return None


