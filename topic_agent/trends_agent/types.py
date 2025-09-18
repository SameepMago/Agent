from typing import TypedDict, List, Optional, Dict


class Item(TypedDict, total=False):
    keyword: str
    is_movie: bool
    movie_name: str
    imdb_id: str


class AgentState(TypedDict, total=False):
    # Raw data collection
    google_trends: List[Dict]
    tmdb_trends: List[Dict] 
    reddit_trends: List[Dict]
    twitter_trends: List[Dict]
    all_trends: List[Dict]
    
    # Query generation and testing
    manual_queries: Dict[str, List[str]]  # trend -> manual queries
    manual_query_results: Dict[str, List[Dict]]  # trend -> manual query search results
    manual_classifications: Dict[str, Dict]  # trend -> manual query classification
    
    # LLM query generation for non-entertainment
    llm_queries: Dict[str, List[str]]  # trend -> LLM queries
    llm_query_results: Dict[str, List[Dict]]  # trend -> LLM query search results
    llm_classifications: Dict[str, Dict]  # trend -> LLM query classification
    
    # Final results
    final_search_results: Dict[str, List[Dict]]  # trend -> final search results
    final_classifications: Dict[str, Dict]  # trend -> final classification
    omdb_results: Dict[str, Dict]  # trend -> OMDB data
    
    # Processed results
    classified_results: List[Dict]
    saved_count: int
    
    # Control flow
    trends_to_process: List[Dict]  # trends that need processing
    entertainment_trends: List[Dict]  # trends classified as entertainment
    non_entertainment_trends: List[Dict]  # trends that need LLM queries


