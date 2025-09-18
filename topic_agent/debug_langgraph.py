#!/usr/bin/env python3
"""
Debug script to check the LangGraph state flow.
"""

import os
import sys

# Try to load environment variables if dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trends_agent.graph import build_graph


def debug_langgraph_state():
    """Debug the LangGraph state flow"""
    print("🔍 Debugging LangGraph State Flow")
    print("=" * 50)
    
    try:
        # Build the graph
        print("🔧 Building LangGraph...")
        graph = build_graph()
        print("✅ Graph built successfully!")
        
        # Initialize state with mock data
        initial_state = {
            "google_trends": [
                {"trend": "Deadpool & Wolverine", "breakdown": "Movie", "link": "https://trends.google.com/trends/explore?q=Deadpool+%26+Wolverine"},
                {"trend": "Stranger Things Season 5", "breakdown": "TV Show", "link": "https://trends.google.com/trends/explore?q=Stranger+Things+Season+5"},
            ],
            "tmdb_trends": [
                {"trend": "Oppenheimer", "breakdown": "Movie", "link": "https://www.themoviedb.org/movie/872585-oppenheimer", "source": "tmdb", "content_type": "movie"},
            ],
            "reddit_trends": [],
            "twitter_trends": [],
            "all_trends": [],
            "trends_to_process": [],
            "manual_queries": {},
            "manual_query_results": {},
            "manual_classifications": {},
            "llm_queries": {},
            "llm_query_results": {},
            "llm_classifications": {},
            "entertainment_trends": [],
            "non_entertainment_trends": [],
            "final_search_results": {},
            "final_classifications": {},
            "classified_results": [],
            "omdb_results": {},
            "saved_count": 0
        }
        
        print("\n🎯 Running LangGraph workflow step by step...")
        print("-" * 30)
        
        # Run the graph step by step
        result = graph.invoke(initial_state)
        
        print("\n✅ LangGraph workflow completed!")
        print("=" * 50)
        
        # Debug state after each step
        print("\n🔍 DEBUGGING STATE:")
        print(f"   📊 all_trends: {len(result.get('all_trends', []))}")
        print(f"   🔄 trends_to_process: {len(result.get('trends_to_process', []))}")
        print(f"   🔍 manual_queries: {len(result.get('manual_queries', {}))}")
        print(f"   🎬 entertainment_trends: {len(result.get('entertainment_trends', []))}")
        print(f"   🚫 non_entertainment_trends: {len(result.get('non_entertainment_trends', []))}")
        
        # Show trends_to_process content
        trends_to_process = result.get('trends_to_process', [])
        if trends_to_process:
            print(f"\n📋 TRENDS TO PROCESS ({len(trends_to_process)}):")
            for i, trend in enumerate(trends_to_process, 1):
                print(f"   {i}. {trend.get('trend', 'N/A')} (Source: {trend.get('source', 'N/A')})")
        else:
            print("\n❌ No trends to process found!")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🔍 LangGraph State Debug")
    print("=" * 50)
    
    # Check for required environment variables
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("⚠️ GEMINI_API_KEY not found in environment variables")
        print("   Using placeholder key for testing...")
        os.environ["GEMINI_API_KEY"] = "test_key_placeholder"
    
    # Run the debug
    success = debug_langgraph_state()
    
    if success:
        print("\n🎉 Debug completed!")
    else:
        print("\n💥 Debug failed!")
        sys.exit(1)
