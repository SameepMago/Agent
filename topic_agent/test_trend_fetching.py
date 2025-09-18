#!/usr/bin/env python3
"""
Test Trend Fetching Script

This script tests the trend fetching functionality without requiring API keys.
It focuses on the first part of the workflow: collecting trends from all sources.

Usage:
    python test_trend_fetching.py
"""

import os
import sys
from typing import List, Dict

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trends_agent.services import (
    fetch_google_trends_csv,
    fetch_tmdb_trending, 
    fetch_reddit_trending,
    fetch_twitter_trending,
    fetch_fallback_trends
)

def test_trend_sources() -> List[Dict]:
    """
    Test fetching trends from all available sources.
    
    Returns:
        List of all trend dictionaries from all sources
    """
    print("🚀 Testing trend collection from all sources...")
    
    all_trends = []
    
    # 1. Google Trends CSV
    print("\n📊 Testing Google Trends CSV...")
    try:
        google_trends = fetch_google_trends_csv()
        for trend in google_trends:
            trend['source'] = 'google_trends'
            trend['content_type'] = 'trend'
        all_trends.extend(google_trends)
        print(f"✅ Google Trends: {len(google_trends)} trends")
        
        # Show sample trends
        if google_trends:
            print("   Sample trends:")
            for i, trend in enumerate(google_trends[:3]):
                print(f"     {i+1}. {trend.get('trend', 'Unknown')}")
                if trend.get('breakdown'):
                    print(f"        Breakdown: {trend.get('breakdown')}")
                    
    except Exception as e:
        print(f"❌ Google Trends failed: {e}")
    
    # 2. TMDB Trending
    print("\n🎬 Testing TMDB trending...")
    try:
        tmdb_trends = fetch_tmdb_trending()
        all_trends.extend(tmdb_trends)
        print(f"✅ TMDB: {len(tmdb_trends)} trends")
        
        # Show sample trends
        if tmdb_trends:
            print("   Sample trends:")
            for i, trend in enumerate(tmdb_trends[:3]):
                print(f"     {i+1}. {trend.get('trend', 'Unknown')} ({trend.get('content_type', 'unknown')})")
                    
    except Exception as e:
        print(f"❌ TMDB failed: {e}")
    
    # 3. Reddit Trending
    print("\n🔴 Testing Reddit trending...")
    try:
        reddit_trends = fetch_reddit_trending()
        all_trends.extend(reddit_trends)
        print(f"✅ Reddit: {len(reddit_trends)} trends")
        
        # Show sample trends
        if reddit_trends:
            print("   Sample trends:")
            for i, trend in enumerate(reddit_trends[:3]):
                print(f"     {i+1}. {trend.get('trend', 'Unknown')}")
                    
    except Exception as e:
        print(f"❌ Reddit failed: {e}")
    
    # 4. Twitter Trending
    print("\n🐦 Testing Twitter trending...")
    try:
        twitter_trends = fetch_twitter_trending()
        all_trends.extend(twitter_trends)
        print(f"✅ Twitter: {len(twitter_trends)} trends")
        
        # Show sample trends
        if twitter_trends:
            print("   Sample trends:")
            for i, trend in enumerate(twitter_trends[:3]):
                print(f"     {i+1}. {trend.get('trend', 'Unknown')}")
                    
    except Exception as e:
        print(f"❌ Twitter failed: {e}")
    
    # 5. Fallback Trends (only if no other sources worked)
    if not all_trends:
        print("\n🆘 No trends found, testing fallback...")
        try:
            fallback_trends = fetch_fallback_trends()
            all_trends.extend(fallback_trends)
            print(f"✅ Fallback: {len(fallback_trends)} trends")
        except Exception as e:
            print(f"❌ Fallback failed: {e}")
    
    print(f"\n🎯 Total trends collected: {len(all_trends)}")
    return all_trends

def display_trends_summary(trends: List[Dict]):
    """Display a detailed summary of collected trends by source."""
    print("\n" + "="*60)
    print("📊 TRENDS COLLECTION SUMMARY")
    print("="*60)
    
    if not trends:
        print("❌ No trends collected!")
        return
    
    # Group by source
    by_source = {}
    for trend in trends:
        source = trend.get('source', 'unknown')
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(trend)
    
    for source, source_trends in by_source.items():
        print(f"\n📈 {source.upper()}: {len(source_trends)} trends")
        for i, trend in enumerate(source_trends[:5]):  # Show first 5
            trend_name = trend.get('trend', 'Unknown')
            breakdown = trend.get('breakdown', '')
            link = trend.get('link', '')
            content_type = trend.get('content_type', '')
            
            print(f"  {i+1}. {trend_name}")
            if breakdown:
                print(f"     Breakdown: {breakdown}")
            if link:
                print(f"     Link: {link[:60]}...")
            if content_type:
                print(f"     Type: {content_type}")
                
        if len(source_trends) > 5:
            print(f"  ... and {len(source_trends) - 5} more")

def main():
    """Main execution function."""
    print("🚀 TREND FETCHING TEST")
    print("="*60)
    
    try:
        # Test trend fetching
        all_trends = test_trend_sources()
        
        if not all_trends:
            print("❌ No trends collected from any source!")
            return
        
        # Display detailed summary
        display_trends_summary(all_trends)
        
        print(f"\n✅ Trend fetching test completed successfully!")
        print(f"📊 Summary:")
        print(f"   - Total trends collected: {len(all_trends)}")
        
        # Show breakdown by source
        sources = {}
        for trend in all_trends:
            source = trend.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print(f"   - Sources: {dict(sources)}")
        
        print(f"\n💡 Next steps:")
        print(f"   1. Set up GEMINI_API_KEY in environment variables")
        print(f"   2. Run 'python resolve_trends.py' to test full resolution workflow")
        
    except Exception as e:
        print(f"❌ Error in trend fetching test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
