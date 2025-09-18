#!/usr/bin/env python3
"""
Test the new workflow without Google Trends (to avoid hanging).
"""

from trends_agent.services.tmdb_trends import fetch_tmdb_trending
from trends_agent.services.reddit_trends import fetch_reddit_trending
from trends_agent.services.twitter_trends import fetch_twitter_trending
from trends_agent.services.web_search import search_trends


def test_workflow_no_google():
    """Test the new workflow without Google Trends."""
    print("🧪 Testing New Workflow (No Google Trends)")
    print("=" * 50)
    
    try:
        # Fetch from sources that work
        print("🔍 Fetching from TMDB...")
        tmdb_results = fetch_tmdb_trending()
        print(f"✅ TMDB: {len(tmdb_results)} items")
        
        print("\n🔍 Fetching from Reddit...")
        reddit_results = fetch_reddit_trending()
        print(f"✅ Reddit: {len(reddit_results)} items")
        
        print("\n🔍 Fetching from Twitter...")
        twitter_results = fetch_twitter_trending()
        print(f"✅ Twitter: {len(twitter_results)} items")
        
        # Combine all trends
        all_trends = []
        
        # Add TMDB trends
        for item in tmdb_results:
            all_trends.append({
                "trend": item.get("trend", ""),
                "breakdown": item.get("breakdown", ""),
                "link": item.get("link", ""),
                "source": item.get("source", "tmdb"),
                "content_type": item.get("content_type", "")
            })
        
        # Add Reddit trends
        for item in reddit_results:
            all_trends.append({
                "trend": item.get("trend", ""),
                "breakdown": item.get("breakdown", ""),
                "link": item.get("link", ""),
                "source": "reddit"
            })
        
        # Add Twitter trends
        for item in twitter_results:
            all_trends.append({
                "trend": item.get("trend", ""),
                "breakdown": item.get("breakdown", ""),
                "link": item.get("link", ""),
                "source": "twitter"
            })
        
        # Remove duplicates
        unique_trends = []
        seen = set()
        for trend in all_trends:
            key = trend.get("trend", "")
            if key and key not in seen:
                unique_trends.append(trend)
                seen.add(key)
        
        print(f"\n🎯 Combined trends: {len(unique_trends)} unique trends")
        
        # Show sample trends
        if unique_trends:
            print(f"\n🔍 Sample trends:")
            for trend in unique_trends[:10]:
                print(f"  - {trend.get('trend', 'N/A')} (Source: {trend.get('source', 'N/A')})")
        
        # Test search agent with a subset of trends
        print(f"\n🔍 Testing search agent with first 5 trends...")
        test_trends = unique_trends[:5]
        
        search_results = search_trends(test_trends, max_results_per_query=2)
        
        print(f"\n🌐 Search results: {len(search_results)} total results")
        
        if search_results:
            print(f"\n🔍 Sample search results:")
            for result in search_results[:5]:
                print(f"  - {result.get('title', 'N/A')[:60]}...")
                print(f"    Query: {result.get('search_query', 'N/A')}")
                print(f"    Trend: {result.get('trend', 'N/A')}")
                print(f"    URL: {result.get('url', 'N/A')[:50]}...")
                print()
        
        return {
            "trends": unique_trends,
            "search_results": search_results
        }
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_workflow_no_google()
