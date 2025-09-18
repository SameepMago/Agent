#!/usr/bin/env python3
"""
Trend Resolution Script

This script:
1. Fetches trending data from all sources
2. Passes the trends to web search for entertainment content classification
3. Shows detailed results of the resolution process

Usage:
    python resolve_trends.py
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
    fetch_fallback_trends,
    search_and_classify_trends
)

def fetch_all_trends() -> List[Dict]:
    """
    Fetch trends from all available sources and combine them.
    Limited to small samples for faster testing.
    
    Returns:
        List of trend dictionaries from all sources (limited sample)
    """
    print("🚀 Starting trend collection from all sources (limited sample)...")
    
    all_trends = []
    
    # 1. Google Trends CSV (limit to first 10)
    print("\n📊 Fetching Google Trends CSV (sample of 10)...")
    try:
        google_trends = fetch_google_trends_csv()
        # Take only first 10 trends
        google_trends = google_trends[:10]
        for trend in google_trends:
            trend['source'] = 'google_trends'
            trend['content_type'] = 'trend'
        all_trends.extend(google_trends)
        print(f"✅ Google Trends: {len(google_trends)} trends")
    except Exception as e:
        print(f"❌ Google Trends failed: {e}")
    
    # 2. TMDB Trending (limit to first 5)
    print("\n🎬 Fetching TMDB trending (sample of 5)...")
    try:
        tmdb_trends = fetch_tmdb_trending()
        # Take only first 5 trends
        tmdb_trends = tmdb_trends[:5]
        all_trends.extend(tmdb_trends)
        print(f"✅ TMDB: {len(tmdb_trends)} trends")
    except Exception as e:
        print(f"❌ TMDB failed: {e}")
    
    # 3. Reddit Trending (limit to first 5)
    print("\n🔴 Fetching Reddit trending (sample of 5)...")
    try:
        reddit_trends = fetch_reddit_trending()
        # Take only first 5 trends
        reddit_trends = reddit_trends[:5]
        all_trends.extend(reddit_trends)
        print(f"✅ Reddit: {len(reddit_trends)} trends")
    except Exception as e:
        print(f"❌ Reddit failed: {e}")
    
    # 4. Twitter Trending (limit to first 5)
    print("\n🐦 Fetching Twitter trending (sample of 5)...")
    try:
        twitter_trends = fetch_twitter_trending()
        # Take only first 5 trends
        twitter_trends = twitter_trends[:5]
        all_trends.extend(twitter_trends)
        print(f"✅ Twitter: {len(twitter_trends)} trends")
    except Exception as e:
        print(f"❌ Twitter failed: {e}")
    
    # 5. Fallback Trends (only if no other sources worked)
    if not all_trends:
        print("\n🆘 No trends found, using fallback...")
        try:
            fallback_trends = fetch_fallback_trends()
            all_trends.extend(fallback_trends)
            print(f"✅ Fallback: {len(fallback_trends)} trends")
        except Exception as e:
            print(f"❌ Fallback failed: {e}")
    
    print(f"\n🎯 Total trends collected: {len(all_trends)} (limited sample)")
    return all_trends

def display_trends_summary(trends: List[Dict]):
    """Display a summary of collected trends by source."""
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
        for i, trend in enumerate(source_trends[:3]):  # Show first 3
            trend_name = trend.get('trend', 'Unknown')
            breakdown = trend.get('breakdown', '')
            print(f"  {i+1}. {trend_name}")
            if breakdown:
                print(f"     Breakdown: {breakdown}")
        if len(source_trends) > 3:
            print(f"  ... and {len(source_trends) - 3} more")

def resolve_entertainment_trends(trends: List[Dict]) -> List[Dict]:
    """
    Pass trends to web search and classification workflow.
    
    Args:
        trends: List of trend dictionaries
        
    Returns:
        List of classified trend results
    """
    print("\n" + "="*60)
    print("🔍 ENTERTAINMENT CONTENT RESOLUTION")
    print("="*60)
    
    if not trends:
        print("❌ No trends to resolve!")
        return []
    
    print(f"🎯 Processing {len(trends)} trends for entertainment content classification...")
    
    # Use the enhanced web search and classification workflow (reduced results per query)
    classified_results = search_and_classify_trends(trends, max_results_per_query=2)
    
    return classified_results

def display_resolution_results(results: List[Dict]):
    """Display detailed results of the entertainment content resolution."""
    print("\n" + "="*60)
    print("🎬 ENTERTAINMENT CONTENT RESOLUTION RESULTS")
    print("="*60)
    
    if not results:
        print("❌ No resolution results!")
        return
    
    # Count entertainment vs non-entertainment
    entertainment_count = 0
    non_entertainment_count = 0
    
    print(f"\n📊 Processing Summary:")
    print(f"Total trends processed: {len(results)}")
    
    for result in results:
        classification = result.get('classification', {})
        is_entertainment = classification.get('is_entertainment', False)
        
        if is_entertainment:
            entertainment_count += 1
        else:
            non_entertainment_count += 1
    
    print(f"🎬 Entertainment content: {entertainment_count}")
    print(f"📰 Non-entertainment content: {non_entertainment_count}")
    
    # Show entertainment content details
    if entertainment_count > 0:
        print(f"\n🎬 ENTERTAINMENT CONTENT FOUND:")
        print("-" * 40)
        
        for result in results:
            classification = result.get('classification', {})
            if classification.get('is_entertainment', False):
                trend = result.get('trend', 'Unknown')
                content_type = classification.get('content_type', 'unknown')
                specific_content = classification.get('specific_content', '')
                confidence = classification.get('confidence', 0.0)
                reasoning = classification.get('reasoning', '')
                
                print(f"\n🎯 Trend: {trend}")
                print(f"   Type: {content_type}")
                print(f"   Specific Content: {specific_content}")
                print(f"   Confidence: {confidence:.2f}")
                print(f"   Reasoning: {reasoning[:100]}...")
                
                # Show search results summary
                search_results = result.get('search_results', [])
                print(f"   Search Results: {len(search_results)} found")
                
                # Show queries used
                queries_used = result.get('total_queries', 0)
                print(f"   Queries Generated: {queries_used}")
    
    # Show some non-entertainment examples
    if non_entertainment_count > 0:
        print(f"\n📰 NON-ENTERTAINMENT CONTENT (first 5):")
        print("-" * 40)
        
        count = 0
        for result in results:
            classification = result.get('classification', {})
            if not classification.get('is_entertainment', False) and count < 5:
                trend = result.get('trend', 'Unknown')
                content_type = classification.get('content_type', 'unknown')
                confidence = classification.get('confidence', 0.0)
                
                print(f"{count+1}. {trend} ({content_type}, confidence: {confidence:.2f})")
                count += 1

def main():
    """Main execution function."""
    print("🚀 TREND RESOLUTION WORKFLOW")
    print("="*60)
    
    # Load environment variables
    load_dotenv()
    
    # Check for required API keys
    gemini_key = 'AIzaSyCMY2U71_A-gAkIJi85CZu94-SXeOxTl4U'
    if not gemini_key:
        print("❌ Error: GEMINI_API_KEY not found in environment variables")
        print("Please add your Gemini API key to .env file")
        return
    
    print(f"✅ Gemini API key loaded")
    
    try:
        # Step 1: Fetch all trends
        all_trends = fetch_all_trends()
        
        if not all_trends:
            print("❌ No trends collected from any source!")
            return
        
        # Step 2: Display trends summary
        display_trends_summary(all_trends)
        
        # Step 3: Resolve entertainment content
        classified_results = resolve_entertainment_trends(all_trends)
        
        # Step 4: Display resolution results
        display_resolution_results(classified_results)
        
        print(f"\n✅ Trend resolution workflow completed successfully!")
        print(f"📊 Final Summary:")
        print(f"   - Trends collected: {len(all_trends)}")
        print(f"   - Trends processed: {len(classified_results)}")
        print(f"   - Entertainment content found: {sum(1 for r in classified_results if r.get('classification', {}).get('is_entertainment', False))}")
        
    except Exception as e:
        print(f"❌ Error in trend resolution workflow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
