from typing import List, Dict
import requests


def fetch_reddit_trending() -> List[Dict]:
    """Fetch ALL trending from Reddit /r/movies - return dict format"""
    try:
        reddit_url = "https://www.reddit.com/r/movies/hot.json?limit=50"
        headers = {'User-Agent': 'TrendsAgent/1.0'}
        
        response = requests.get(reddit_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            posts = data.get('data', {}).get('children', [])
            
            trending_terms = []
            for post in posts:
                title = post.get('data', {}).get('title', '')
                if title and len(title) > 5:
                    trending_terms.append({
                        'trend': title,
                        'breakdown': f"Reddit post - {post.get('data', {}).get('subreddit', 'movies')}",
                        'link': f"https://reddit.com{post.get('data', {}).get('permalink', '')}",
                        'source': 'reddit'
                    })
                        
            if trending_terms:
                print(f"✅ Reddit entertainment trending: {len(trending_terms)} total terms")
                return trending_terms
                
    except Exception as e:
        print(f"❌ Reddit failed: {e}")
    
    return []
