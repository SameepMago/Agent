#!/usr/bin/env python3
"""
LLM-Only Test Script

This script tests the LLM classification without web search to avoid DuckDuckGo issues.
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
    fetch_twitter_trending
)
from trends_agent.services.llm import GeminiLLM

def test_llm_classification_only():
    """Test LLM classification on trends without web search."""
    print("🤖 Testing LLM Classification (No Web Search)")
    print("="*50)
    
    # Initialize LLM
    llm = GeminiLLM()
    
    # Test with known entertainment terms
    test_terms = [
        "Wednesday Addams",
        "The Conjuring",
        "Netflix",
        "Marvel",
        "Disney",
        "Stranger Things",
        "Game of Thrones",
        "football game",
        "weather report", 
        "stock market",
        "cooking recipe",
        "election results"
    ]
    
    print(f"📝 Testing {len(test_terms)} sample terms...")
    
    entertainment_found = 0
    non_entertainment_found = 0
    
    for i, term in enumerate(test_terms, 1):
        print(f"\n{i:2d}. Testing: '{term}'")
        
        try:
            result = llm.classify_keywords([{'trend': term}])
            if result and len(result) > 0:
                classification = result[0]
                is_entertainment = classification.get('is_movie', False)
                movie_name = classification.get('movie_name', '')
                
                if is_entertainment:
                    entertainment_found += 1
                    print(f"    ✅ Entertainment: {movie_name if movie_name else 'General Entertainment'}")
                else:
                    non_entertainment_found += 1
                    print(f"    ❌ Non-entertainment")
            else:
                print(f"    ⚠️ No classification returned")
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    print(f"\n📊 Results Summary:")
    print(f"   Entertainment: {entertainment_found}")
    print(f"   Non-entertainment: {non_entertainment_found}")
    print(f"   Total tested: {len(test_terms)}")

def test_real_trends_sample():
    """Test LLM on a small sample of real trends."""
    print("\n🎯 Testing Real Trends Sample")
    print("="*50)
    
    # Get a small sample of trends
    print("📊 Fetching sample trends...")
    
    all_trends = []
    
    # Try to get a few trends from each source
    try:
        google_trends = fetch_google_trends_csv()
        if google_trends:
            all_trends.extend(google_trends[:5])  # First 5
            print(f"✅ Google Trends: {len(google_trends[:5])} trends")
    except Exception as e:
        print(f"❌ Google Trends: {e}")
    
    try:
        tmdb_trends = fetch_tmdb_trending()
        if tmdb_trends:
            all_trends.extend(tmdb_trends[:3])  # First 3
            print(f"✅ TMDB: {len(tmdb_trends[:3])} trends")
    except Exception as e:
        print(f"❌ TMDB: {e}")
    
    try:
        reddit_trends = fetch_reddit_trending()
        if reddit_trends:
            all_trends.extend(reddit_trends[:3])  # First 3
            print(f"✅ Reddit: {len(reddit_trends[:3])} trends")
    except Exception as e:
        print(f"❌ Reddit: {e}")
    
    if not all_trends:
        print("❌ No trends collected!")
        return
    
    print(f"\n🎯 Testing {len(all_trends)} real trends...")
    
    # Initialize LLM
    llm = GeminiLLM()
    
    entertainment_found = 0
    non_entertainment_found = 0
    
    for i, trend_data in enumerate(all_trends, 1):
        trend_name = trend_data.get('trend', 'Unknown')
        source = trend_data.get('source', 'unknown')
        
        print(f"\n{i:2d}. [{source}] '{trend_name}'")
        
        try:
            result = llm.classify_keywords([{'trend': trend_name}])
            if result and len(result) > 0:
                classification = result[0]
                is_entertainment = classification.get('is_movie', False)
                movie_name = classification.get('movie_name', '')
                
                if is_entertainment:
                    entertainment_found += 1
                    print(f"    ✅ Entertainment: {movie_name if movie_name else 'General Entertainment'}")
                else:
                    non_entertainment_found += 1
                    print(f"    ❌ Non-entertainment")
            else:
                print(f"    ⚠️ No classification returned")
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    print(f"\n📊 Real Trends Results:")
    print(f"   Entertainment: {entertainment_found}")
    print(f"   Non-entertainment: {non_entertainment_found}")
    print(f"   Total tested: {len(all_trends)}")

def main():
    """Main test function."""
    print("🧪 LLM-ONLY CLASSIFICATION TEST")
    print("="*60)
    
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    gemini_key = 'AIzaSyCMY2U71_A-gAkIJi85CZu94-SXeOxTl4U'
    if not gemini_key:
        print("❌ Error: GEMINI_API_KEY not found")
        return
    
    print(f"✅ Gemini API key loaded")
    
    try:
        # Test 1: Known terms
        test_llm_classification_only()
        
        # Test 2: Real trends sample
        test_real_trends_sample()
        
        print(f"\n✅ All LLM tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

