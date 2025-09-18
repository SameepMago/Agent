import os
import json
import re
from typing import List, Dict, Optional


def _looks_like_entertainment_content(text: str) -> bool:
    text = text.strip()
    if not text:
        return False
    lowered = text.lower()
    if any(tok in lowered for tok in ["trailer", "movie", "film", "box office", "tv show", "series", "episode", "season", "netflix", "streaming"]):
        return True
    # Simple heuristic: multi-word Title Case
    words = text.split()
    if len(words) >= 2 and all(w and w[0].isupper() for w in words if w.isalpha() or w[0].isalpha()):
        return True
    # Year pattern
    if re.search(r"\b(19|20)\d{2}\b", text):
        return True
    return False


class GeminiLLM:
    def __init__(self) -> None:
        self.api_key = "AIzaSyCMY2U71_A-gAkIJi85CZu94-SXeOxTl4U"
        self.model = None
        if self.api_key:
            try:
                import google.generativeai as genai  # type: ignore

                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-2.0-flash")
            except Exception:
                self.model = None

    def _extract_json(self, text: str) -> str:
        text = text.strip()
        # Try direct parse first
        try:
            json.loads(text)
            return text
        except Exception:
            pass
        # Extract first JSON array/object
        match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
        if match:
            return match.group(1)
        # Fallback to empty list
        return "[]"

    def classify_keywords(self, keywords: List[Dict]) -> List[Dict]:
        """Return per-keyword dicts with is_entertainment flag and optional content_name."""
        if self.model is not None and keywords:
            # Extract trend names for the prompt
            trend_names = [kw.get('trend', '') for kw in keywords if kw.get('trend')]
            
            prompt = (
                "You are an expert entertainment content classifier. Given a list of trending keywords with additional context, identify which are entertainment-related. "
                "Consider these categories as entertainment-related:\n"
                "- Movie titles (e.g., 'Deadpool & Wolverine', 'Inside Out 2')\n"
                "- TV show titles (e.g., 'Stranger Things', 'The Crown')\n"
                "- Web series titles (e.g., 'The Boys', 'Wednesday')\n"
                "- Actor/actress names (e.g., 'Tom Cruise', 'Margot Robbie')\n"
                "- Director names (e.g., 'Christopher Nolan', 'Greta Gerwig')\n"
                "- Entertainment characters (e.g., 'Barbie', 'Wolverine', 'Wednesday Addams')\n"
                "- Entertainment events (e.g., 'Oscars', 'Emmy Awards', 'Box Office')\n"
                "- Entertainment franchises (e.g., 'Marvel', 'Star Wars', 'Game of Thrones')\n"
                "- Entertainment news (e.g., 'Movie Release', 'TV Premiere', 'Streaming')\n"
                "- Streaming platforms (e.g., 'Netflix', 'Disney+', 'HBO Max')\n\n"
                "Return a JSON array where each element has: 'keyword' (string), 'is_entertainment_related' (boolean), and optional 'content_name' (string).\n"
                "For actor/director names, include their most recent or notable movie/TV show in 'content_name'.\n\n"
                f"Keywords: {json.dumps(trend_names)}\n\nReturn only valid JSON."
            )
            try:
                response = self.model.generate_content(prompt)
                text = response.text or "[]"
                data = json.loads(self._extract_json(text))
                items: List[Dict] = []
                if isinstance(data, list):
                    for entry in data:
                        if not isinstance(entry, dict):
                            continue
                        keyword = str(entry.get("keyword", "")).strip()
                        if not keyword:
                            continue
                        is_entertainment = bool(entry.get("is_entertainment_related") or entry.get("is_movie_related") or entry.get("is_movie"))
                        content_name = entry.get("content_name") or entry.get("movie_name") or entry.get("title")
                        rec: Dict = {"keyword": keyword, "is_movie": is_entertainment}  # Keep is_movie for compatibility
                        if content_name and isinstance(content_name, str):
                            rec["movie_name"] = content_name.strip()  # Keep movie_name for compatibility
                        items.append(rec)
                if items:
                    return items
            except Exception:
                pass

        # Heuristic fallback
        results: List[Dict] = []
        for kw in keywords:
            trend_name = kw.get('trend', '') if isinstance(kw, dict) else str(kw)
            is_entertainment = _looks_like_entertainment_content(trend_name)
            rec: Dict = {"keyword": trend_name, "is_movie": is_entertainment}  # Keep is_movie for compatibility
            if is_entertainment:
                rec["movie_name"] = trend_name  # Keep movie_name for compatibility
            results.append(rec)
        return results

    def resolve_movie(self, keyword: str) -> Optional[str]:
        """Map a keyword to a likely entertainment content title. Returns None if not applicable."""
        if self.model is not None:
            prompt = (
                "Given a trending keyword, if it refers to entertainment content (movie, TV show, web series) or a cast/actor/character associated with specific content, "
                "output only the exact content title as plain text. If not applicable, output 'null'.\n\n"
                f"Keyword: {json.dumps(keyword)}"
            )
            try:
                response = self.model.generate_content(prompt)
                raw = (response.text or "").strip()
                # Normalize common outputs
                cleaned = raw.strip().strip('"')
                if cleaned.lower() == "null" or cleaned.lower() == "none":
                    return None
                if cleaned:
                    return cleaned
            except Exception:
                pass

        # Heuristic fallback
        return keyword if _looks_like_entertainment_content(keyword) else None


