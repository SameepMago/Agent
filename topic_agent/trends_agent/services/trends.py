from typing import List, Dict

# Import from separate modules
from .google_trends import fetch_google_trends_csv
from .tmdb_trends import fetch_tmdb_trending
from .reddit_trends import fetch_reddit_trending
from .twitter_trends import fetch_twitter_trending
from .fallback_trends import fetch_fallback_trends


# Legacy function names for backward compatibility
def _fetch_from_google_trends_csv() -> List[Dict]:
    """Legacy function name - use fetch_google_trends_csv() instead"""
    return fetch_google_trends_csv()


def _fetch_from_tmdb_trending() -> List[Dict]:
    """Legacy function name - use fetch_tmdb_trending() instead"""
    return fetch_tmdb_trending()


def _fetch_from_reddit() -> List[Dict]:
    """Legacy function name - use fetch_reddit_trends() instead"""
    return fetch_reddit_trending()


def _fetch_from_twitter_trends() -> List[Dict]:
    """Legacy function name - use fetch_twitter_trending() instead"""
    return fetch_twitter_trending()


def _fallback_keywords() -> List[str]:
    """Legacy function - use fetch_fallback_trends() instead"""
    from .fallback_trends import get_fallback_keywords
    return get_fallback_keywords()


def fetch_trending_keywords() -> List[Dict]:
    """Fetch ALL trending keywords from all sources; let LLM filter for entertainment-related ones.
    
    Returns ALL trending terms with breakdowns for LLM to analyze for movies, TV shows, web series, etc.
    """
    # Try Google Trends CSV first (most comprehensive)
    print("🔍 Fetching ALL Google Trends CSV with Selenium...")
    csv_results = fetch_google_trends_csv()
    if csv_results:
        print(f"📊 Found {len(csv_results)} total trending terms with breakdowns - LLM will filter for entertainment-related ones")
        return csv_results

    # Try alternative APIs before falling back to static list
    print("🔄 Trying multiple trending sources...")
    alt_results = _fetch_from_alternative_apis()
    if alt_results:
        return alt_results

    print("⚠️  Using fallback keywords")
    # Final fallback
    return fetch_fallback_trends()


def _fetch_from_alternative_apis() -> List[Dict]:
    """Try all alternative trending sources - return dict format for consistency"""
    print("🔄 Trying multiple trending sources...")
    
    # Try all sources in order of preference
    sources = [
        ("TMDB", fetch_tmdb_trending),
        ("Reddit", fetch_reddit_trending),
        ("Twitter", fetch_twitter_trending),
    ]
    
    all_results = []
    
    for source_name, source_func in sources:
        try:
            print(f"\n🔍 Trying {source_name}...")
            results = source_func()
            if results:
                all_results.extend(results)
                print(f"✅ {source_name} added {len(results)} terms")
            else:
                print(f"❌ {source_name} returned no results")
        except Exception as e:
            print(f"❌ {source_name} error: {e}")
            continue
    
    # Remove duplicates but don't limit results
    unique_results = []
    seen = set()
    for result in all_results:
        trend_key = result.get('trend', '')
        if trend_key not in seen and len(trend_key) > 3:
            unique_results.append(result)
            seen.add(trend_key)
    
    if unique_results:
        print(f"\n🎯 Total unique trending terms: {len(unique_results)}")
        return unique_results
    
    return []


