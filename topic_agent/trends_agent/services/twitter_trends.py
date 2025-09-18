from typing import List, Dict
import requests


def fetch_twitter_trending() -> List[Dict]:
    """Fetch ALL trending from Twitter - return dict format"""
    try:
        # Twitter trends page (no API key needed)
        twitter_url = "https://trends24.in/united-states/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(twitter_url, headers=headers, timeout=15)
        if response.status_code == 200:
            content = response.text
            
            trending_terms = []
            lines = content.split('\n')
            for line in lines:
                # Extract any trending term (not just movie-related)
                if len(line) > 10 and len(line) < 100:
                    clean_line = line.strip()
                    if clean_line and clean_line not in [t.get('trend', '') for t in trending_terms] and not clean_line.startswith('http'):
                        trending_terms.append({
                            'trend': clean_line,
                            'breakdown': 'Twitter trending topic',
                            'link': f"https://twitter.com/search?q={clean_line.replace(' ', '%20')}",
                            'source': 'twitter'
                        })
            
            if trending_terms:
                print(f"✅ Twitter trends: {len(trending_terms)} total terms")
                return trending_terms
                
    except Exception as e:
        print(f"❌ Twitter failed: {e}")
    
    return []
