#!/usr/bin/env python3
"""
Test script for the new LangGraph workflow with smart query generation and conditional routing.
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


def test_new_langgraph():
    """Test the new LangGraph workflow"""
    print("🚀 Testing New LangGraph Workflow")
    print("=" * 50)
    
    try:
        # Build the graph
        print("🔧 Building LangGraph...")
        graph = build_graph()
        print("✅ Graph built successfully!")
        
        # Initialize state
        initial_state = {
            "google_trends": [],
            "tmdb_trends": [],
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
        
        print("\n🎯 Running LangGraph workflow...")
        print("-" * 30)
        
        # Run the graph
        result = graph.invoke(initial_state)
        
        print("\n✅ LangGraph workflow completed!")
        print("=" * 50)
        
        # Display results summary
        print("\n📊 RESULTS SUMMARY:")
        print(f"   🎬 Entertainment trends: {len(result.get('entertainment_trends', []))}")
        print(f"   🚫 Non-entertainment trends: {len(result.get('non_entertainment_trends', []))}")
        print(f"   🔍 Manual queries generated: {len(result.get('manual_queries', {}))}")
        print(f"   🤖 LLM queries generated: {len(result.get('llm_queries', {}))}")
        print(f"   🌐 Final search results: {len(result.get('final_search_results', {}))}")
        print(f"   🎯 Classified results: {len(result.get('classified_results', []))}")
        print(f"   🎬 OMDB results: {len(result.get('omdb_results', {}))}")
        print(f"   💾 Saved to database: {result.get('saved_count', 0)}")
        
        # Display entertainment trends
        entertainment_trends = result.get('entertainment_trends', [])
        if entertainment_trends:
            print(f"\n🎬 ENTERTAINMENT TRENDS FOUND ({len(entertainment_trends)}):")
            for i, trend in enumerate(entertainment_trends, 1):
                print(f"   {i}. {trend.get('trend', 'N/A')} (Source: {trend.get('source', 'N/A')})")
        
        # Display non-entertainment trends
        non_entertainment_trends = result.get('non_entertainment_trends', [])
        if non_entertainment_trends:
            print(f"\n🚫 NON-ENTERTAINMENT TRENDS ({len(non_entertainment_trends)}):")
            for i, trend in enumerate(non_entertainment_trends, 1):
                print(f"   {i}. {trend.get('trend', 'N/A')} (Source: {trend.get('source', 'N/A')})")
        
        # Display classified results
        classified_results = result.get('classified_results', [])
        if classified_results:
            print(f"\n🎯 CLASSIFIED RESULTS ({len(classified_results)}):")
            for i, result_item in enumerate(classified_results, 1):
                trend = result_item.get('trend', 'N/A')
                classification = result_item.get('classification', {})
                content_type = classification.get('content_type', 'unknown')
                specific_content = classification.get('specific_content', 'N/A')
                confidence = classification.get('confidence', 0.0)
                print(f"   {i}. {trend} → {content_type} ({specific_content}) [Confidence: {confidence:.2f}]")
        
        return True
        
    except Exception as e:
        print(f"❌ LangGraph test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🎬 New LangGraph Workflow Test")
    print("=" * 50)
    
    # Check for required environment variables
    gemini_key = 'AIzaSyCMY2U71_A-gAkIJi85CZu94-SXeOxTl4U'
    if not gemini_key:
        print("⚠️ GEMINI_API_KEY not found in environment variables")
        print("   Using placeholder key for testing...")
        os.environ["GEMINI_API_KEY"] = "test_key_placeholder"
    
    # Run the test
    success = test_new_langgraph()
    
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!")
        sys.exit(1)
