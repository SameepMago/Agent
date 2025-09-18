#!/usr/bin/env python3
"""
Simple Trend Resolution Test

This script tests the core trend resolution workflow without web search issues.
"""

import os
import sys
from typing import List, Dict
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trends_agent.services import (
    fetch_google_trends_csv,
    fetch_tmdb_trending, 
    fetch_reddit_trending,
    fetch_twitter_trending,
    fetch_fallback_trends
)
from trends_agent.services.llm import GeminiLLM

def test_trend_collection():
    """Test trend collection from all sources."""
    print("🚀 Testing trend collection from all sources...")
    
    all_trends = []
    
    # Test each source individually
    sources = [
        ("Google Trends", fetch_google_trends_csv),
        ("TMDB", fetch_tmdb_trending),
        ("Reddit", fetch_reddit_trending),
        ("Twitter", fetch_twitter_trending),
    ]
    
    for source_name, fetch_func in sources:
        print(f"\n📊 Testing {source_name}...")
        try:
            trends = fetch_func()
            if trends:
                print(f"✅ {source_name}: {len(trends)} trends")
                # Add source info
                for trend in trends:
                    trend['source'] = source_name.lower().replace(' ', '_')
                all_trends.extend(trends)
            else:
                print(f"⚠️ {source_name}: No trends returned")
        except Exception as e:
            print(f"❌ {source_name}: {e}")
    
    print(f"\n🎯 Total trends collected: {len(all_trends)}")
    return all_trends

def test_llm_classification(trends: List[Dict]):
    """Test LLM classification on a sample of trends."""
    print("\n🤖 Testing LLM classification...")
    
    # Initialize LLM
    llm = GeminiLLM()
    
    # Test with first 10 trends
    sample_trends = trends[:10]
    print(f"📝 Testing classification on {len(sample_trends)} sample trends...")
    
    for i, trend in enumerate(sample_trends, 1):
        trend_name = trend.get('trend', 'Unknown')
        print(f"\n{i}. Testing: '{trend_name}'")
        
        try:
            # Test the classification
            result = llm.classify_keywords([{'trend': trend_name}])
            if result and len(result) > 0:
                classification = result[0]
                is_movie = classification.get('is_movie', False)
                movie_name = classification.get('movie_name', '')
                print(f"   Result: {'🎬 Entertainment' if is_movie else '📰 Non-entertainment'}")
                if movie_name:
                    print(f"   Content: {movie_name}")
            else:
                print(f"   Result: No classification returned")
        except Exception as e:
            print(f"   Error: {e}")

def test_manual_classification():
    """Test manual classification with known entertainment terms."""
    print("\n🎬 Testing manual classification with known entertainment terms...")
    
    test_terms = [
        "Wednesday Addams",
        "The Conjuring",
        "Netflix",
        "Marvel",
        "Disney",
        "football game",
        "weather report",
        "stock market",
        "cooking recipe"
    ]
    
    llm = GeminiLLM()
    
    for term in test_terms:
        print(f"\nTesting: '{term}'")
        try:
            result = llm.classify_keywords([{'trend': term}])
            if result and len(result) > 0:
                classification = result[0]
                is_movie = classification.get('is_movie', False)
                movie_name = classification.get('movie_name', '')
                print(f"   Result: {'🎬 Entertainment' if is_movie else '📰 Non-entertainment'}")
                if movie_name:
                    print(f"   Content: {movie_name}")
        except Exception as e:
            print(f"   Error: {e}")

def main():
    """Main test function."""
    print("🧪 SIMPLE TREND RESOLUTION TEST")
    print("="*50)
    
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    gemini_key = 'AIzaSyCMY2U71_A-gAkIJi85CZu94-SXeOxTl4U'
    if not gemini_key:
        print("❌ Error: GEMINI_API_KEY not found")
        return
    
    print(f"✅ Gemini API key loaded")
    
    try:
        # Test 1: Trend Collection
        trends = test_trend_collection()
        
        if not trends:
            print("❌ No trends collected!")
            return
        
        # Test 2: LLM Classification on sample
        test_llm_classification(trends)
        
        # Test 3: Manual classification
        test_manual_classification()
        
        print(f"\n✅ All tests completed!")
        print(f"📊 Summary: {len(trends)} trends collected and tested")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

