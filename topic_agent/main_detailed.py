import os
from dotenv import load_dotenv

from trends_agent.graph import build_graph
from trends_agent.services.trends import fetch_trending_keywords
from trends_agent.services.llm import GeminiLLM
from trends_agent.services.omdb import fetch_imdb_id
from trends_agent.services.db import TrendsDB

def show_step_results():
    """Show detailed results of each step"""
    print("🔍 STEP-BY-STEP EXECUTION RESULTS")
    print("=" * 60)
    
    # Step 1: Fetch Trends
    print("\n📊 STEP 1: fetch_trends")
    print("-" * 30)
    keywords = fetch_trending_keywords(15)
    print(f"✅ Retrieved {len(keywords)} trending keywords:")
    for i, kw in enumerate(keywords[:10], 1):  # Show first 10
        print(f"   {i:2d}. {kw}")
    if len(keywords) > 10:
        print(f"   ... and {len(keywords) - 10} more")
    
    # Step 2: Filter Movies
    print("\n🎬 STEP 2: filter_movies")
    print("-" * 30)
    llm = GeminiLLM()
    movie_results = llm.classify_keywords(keywords[:10])  # Process first 10
    movie_keywords = [r for r in movie_results if r.get("is_movie")]
    print(f"✅ Identified {len(movie_keywords)} movie-related keywords:")
    for i, result in enumerate(movie_keywords, 1):
        print(f"   {i:2d}. {result['keyword']} → {result.get('movie_name', 'N/A')}")
    
    # Step 3: Resolve Movie Titles
    print("\n🎯 STEP 3: resolve_movie")
    print("-" * 30)
    resolved_movies = []
    for result in movie_keywords:
        movie_name = result.get("movie_name")
        if not movie_name:
            movie_name = llm.resolve_movie(result.get("keyword", ""))
        if movie_name:
            resolved_movies.append({
                "keyword": result.get("keyword"),
                "movie_name": movie_name
            })
    
    print(f"✅ Resolved {len(resolved_movies)} movie titles:")
    for i, movie in enumerate(resolved_movies, 1):
        print(f"   {i:2d}. {movie['keyword']} → {movie['movie_name']}")
    
    # Step 4: Fetch IMDb IDs
    print("\n🔗 STEP 4: fetch_imdb")
    print("-" * 30)
    enriched_movies = []
    for movie in resolved_movies:
        imdb_id = fetch_imdb_id(movie.get("movie_name", ""))
        enriched_movies.append({
            **movie,
            "imdb_id": imdb_id
        })
    
    print(f"✅ Enriched {len(enriched_movies)} movies with IMDb IDs:")
    for i, movie in enumerate(enriched_movies, 1):
        imdb_display = movie.get("imdb_id") or "❌ Not found"
        print(f"   {i:2d}. {movie['keyword']} → {movie['movie_name']} [{imdb_display}]")
    
    # Step 5: Save to Database
    print("\n💾 STEP 5: save_to_db")
    print("-" * 30)
    db = TrendsDB()
    saved_count = db.save_items(enriched_movies)
    print(f"✅ Saved {saved_count} movies to database")
    
    return enriched_movies

def main() -> None:
    load_dotenv()
    
    print("🚀 TRENDS AGENT - DETAILED EXECUTION")
    print("=" * 60)
    
    # Run step by step
    final_items = show_step_results()
    
    print("\n" + "=" * 60)
    print("🎯 FINAL RESULTS SUMMARY")
    print("=" * 60)
    
    print(f"📊 Total items processed: {len(final_items)}")
    with_imdb = len([item for item in final_items if item.get("imdb_id")])
    without_imdb = len(final_items) - with_imdb
    
    print(f"✅ With IMDb IDs: {with_imdb}")
    print(f"❌ Without IMDb IDs: {without_imdb}")
    
    print(f"\n💾 Database updated: trends.db")
    print("🔍 Use 'python simple_queries.py' to view results")

if __name__ == "__main__":
    main()
