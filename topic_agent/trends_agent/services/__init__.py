"""Trends Agent Services Package

This package contains all the services for fetching trending data from various sources,
processing it with LLM, and storing it in the database.
"""

# Core functions
from .trends import fetch_trending_keywords
from .llm import GeminiLLM
from .omdb import fetch_imdb_id
from .db import TrendsDB

# Individual source functions
from .google_trends import fetch_google_trends_csv
from .tmdb_trends import fetch_tmdb_trending
from .reddit_trends import fetch_reddit_trending
from .twitter_trends import fetch_twitter_trending
from .fallback_trends import fetch_fallback_trends, get_fallback_keywords
from .web_search import search_trends, search_duckduckgo, generate_search_queries, search_and_classify_trends

__all__ = [
    # Core functions
    'fetch_trending_keywords',
    'GeminiLLM',
    'fetch_imdb_id',
    'TrendsDB',
    
    # Individual source functions
    'fetch_google_trends_csv',
    'fetch_tmdb_trending',
    'fetch_reddit_trending',
    'fetch_twitter_trending',
    'fetch_fallback_trends',
    'get_fallback_keywords',
    
    # Web search functions
    'search_trends',
    'search_duckduckgo',
    'generate_search_queries',
    'search_and_classify_trends',
]


