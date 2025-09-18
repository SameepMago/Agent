#!/usr/bin/env python3
"""
Test the core LangGraph workflow logic without data fetching.
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

from trends_agent.types import AgentState
from trends_agent.graph import (
    combine_all_trends,
    generate_manual_queries,
    test_manual_queries,
    classify_manual_entertainment
)


def test_core_workflow():
    """Test the core workflow functions directly"""
    print("🔍 Testing Core LangGraph Workflow Functions")
    print("=" * 50)
    
    try:
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
        
        print("🎯 Step 1: Combining all trends...")
        state1 = combine_all_trends(initial_state)
        print(f"   ✅ Combined trends: {len(state1.get('all_trends', []))}")
        print(f"   ✅ Trends to process: {len(state1.get('trends_to_process', []))}")
        
        print("\n🎯 Step 2: Generating manual queries...")
        state2 = generate_manual_queries(state1)
        print(f"   ✅ Manual queries: {len(state2.get('manual_queries', {}))}")
        
        print("\n🎯 Step 3: Testing manual queries...")
        state3 = test_manual_queries(state2)
        print(f"   ✅ Manual query results: {len(state3.get('manual_query_results', {}))}")
        
        print("\n🎯 Step 4: Classifying manual entertainment...")
        state4 = classify_manual_entertainment(state3)
        print(f"   ✅ Entertainment trends: {len(state4.get('entertainment_trends', []))}")
        print(f"   ✅ Non-entertainment trends: {len(state4.get('non_entertainment_trends', []))}")
        
        print("\n✅ Core workflow test completed!")
        print("=" * 50)
        
        # Show detailed results
        trends_to_process = state1.get('trends_to_process', [])
        if trends_to_process:
            print(f"\n📋 TRENDS TO PROCESS ({len(trends_to_process)}):")
            for i, trend in enumerate(trends_to_process, 1):
                print(f"   {i}. {trend.get('trend', 'N/A')} (Source: {trend.get('source', 'N/A')})")
        
        manual_queries = state2.get('manual_queries', {})
        if manual_queries:
            print(f"\n🔍 MANUAL QUERIES ({len(manual_queries)}):")
            for trend, queries in manual_queries.items():
                print(f"   {trend}: {queries}")
        
        entertainment_trends = state4.get('entertainment_trends', [])
        if entertainment_trends:
            print(f"\n🎬 ENTERTAINMENT TRENDS ({len(entertainment_trends)}):")
            for i, trend in enumerate(entertainment_trends, 1):
                print(f"   {i}. {trend.get('trend', 'N/A')} (Source: {trend.get('source', 'N/A')})")
        
        non_entertainment_trends = state4.get('non_entertainment_trends', [])
        if non_entertainment_trends:
            print(f"\n🚫 NON-ENTERTAINMENT TRENDS ({len(non_entertainment_trends)}):")
            for i, trend in enumerate(non_entertainment_trends, 1):
                print(f"   {i}. {trend.get('trend', 'N/A')} (Source: {trend.get('source', 'N/A')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Core workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🔍 Core LangGraph Workflow Test")
    print("=" * 50)
    
    # Check for required environment variables
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("⚠️ GEMINI_API_KEY not found in environment variables")
        print("   Using placeholder key for testing...")
        os.environ["GEMINI_API_KEY"] = "test_key_placeholder"
    
    # Run the test
    success = test_core_workflow()
    
    if success:
        print("\n🎉 Core workflow test completed successfully!")
    else:
        print("\n💥 Core workflow test failed!")
        sys.exit(1)
