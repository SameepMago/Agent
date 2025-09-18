#!/usr/bin/env python3
"""
Test the new workflow with web search.
"""

from trends_agent.graph import build_graph


def test_new_workflow():
    """Test the new workflow with web search."""
    print("🧪 Testing New Workflow with Web Search")
    print("=" * 50)
    
    try:
        # Build the new graph
        print("🔧 Building new graph with web search...")
        app = build_graph()
        print("✅ New graph built successfully!")
        
        # Test with empty state
        print("\n🚀 Testing with empty state...")
        initial_state = {}
        
        print("\n📊 Initial state:", initial_state)
        
        # Execute the graph
        final_state = app.invoke(initial_state)
        
        print(f"\n✅ Graph execution completed!")
        print(f"📊 Final state keys: {list(final_state.keys())}")
        
        # Check results
        saved = final_state.get("saved_count", 0)
        search_results = final_state.get("search_results", [])
        all_trends = final_state.get("all_trends", [])
        
        print(f"\n🎯 Final Results:")
        print(f"   Trends collected: {len(all_trends)}")
        print(f"   Search results: {len(search_results)}")
        print(f"   Saved to DB: {saved} rows")
        
        if all_trends:
            print(f"\n🔍 Sample trends:")
            for trend in all_trends[:5]:
                print(f"  - {trend.get('trend', 'N/A')} (Source: {trend.get('source', 'N/A')})")
        
        if search_results:
            print(f"\n🌐 Sample search results:")
            for result in search_results[:3]:
                print(f"  - {result.get('title', 'N/A')[:50]}...")
                print(f"    Query: {result.get('search_query', 'N/A')}")
                print(f"    URL: {result.get('url', 'N/A')[:50]}...")
        
        return final_state
        
    except Exception as e:
        print(f"❌ Graph execution failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_new_workflow()
