#!/usr/bin/env python3
"""
Test script to verify the updated entertainment classification system
"""

import os
from trends_agent.services.web_search import search_and_classify_trends

def main():
    # Test trends with different types of content
    test_trends = [
        {
            "trend": "Deadpool & Wolverine",
            "breakdown": "Marvel movie trailer",
            "source": "google_trends",
            "link": "https://trends.google.com/trends/explore?q=Deadpool%20%26%20Wolverine"
        },
        {
            "trend": "Super Bowl 2025",
            "breakdown": "NFL championship game",
            "source": "google_trends", 
            "link": "https://trends.google.com/trends/explore?q=Super%20Bowl%202025"
        },
        {
            "trend": "Stranger Things Season 5",
            "breakdown": "Netflix series",
            "source": "google_trends",
            "link": "https://trends.google.com/trends/explore?q=Stranger%20Things%20Season%205"
        },
        {
            "trend": "Bitcoin price",
            "breakdown": "Cryptocurrency market",
            "source": "google_trends",
            "link": "https://trends.google.com/trends/explore?q=Bitcoin%20price"
        },
        {
            "trend": "Oppenheimer",
            "breakdown": "Christopher Nolan movie",
            "source": "google_trends",
            "link": "https://trends.google.com/trends/explore?q=Oppenheimer"
        }
    ]
    
    print("🧪 TESTING ENTERTAINMENT CLASSIFICATION SYSTEM")
    print("=" * 60)
    
    # Test the classification
    results = search_and_classify_trends(test_trends, max_results_per_query=3)
    
    print(f"\n📊 CLASSIFICATION RESULTS")
    print("=" * 60)
    
    for i, result in enumerate(results):
        trend = result.get("trend", "")
        classification = result.get("classification", {})
        is_entertainment = classification.get("is_entertainment", False)
        content_type = classification.get("content_type", "unknown")
        specific_content = classification.get("specific_content", "")
        confidence = classification.get("confidence", 0.0)
        reasoning = classification.get("reasoning", "")
        
        status = "✅ ENTERTAINMENT" if is_entertainment else "❌ NOT ENTERTAINMENT"
        
        print(f"\n{i+1}. {trend}")
        print(f"   Status: {status}")
        print(f"   Type: {content_type}")
        print(f"   Specific: {specific_content}")
        print(f"   Confidence: {confidence:.2f}")
        print(f"   Reasoning: {reasoning[:100]}...")

if __name__ == "__main__":
    main()
