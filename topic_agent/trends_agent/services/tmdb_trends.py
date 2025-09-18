from typing import List, Dict
import requests


def fetch_tmdb_trending() -> List[Dict]:
    """Fetch ALL trending entertainment content from TMDB - return dict format with trend, breakdown, link"""
    try:
        # TMDB API key - you can change this variable
        tmdb_api_key = "7fc8f0784594d9068ac175ff860bfe75"
        
        # Hit both movie and TV trending endpoints
        tmdb_movie_url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={tmdb_api_key}"
        tmdb_tv_url = f"https://api.themoviedb.org/3/trending/tv/week?api_key={tmdb_api_key}"
        
        headers = {
            'User-Agent': 'TrendsAgent/1.0',
            'Accept': 'application/json'
        }
        
        trending_terms = []
        
        # Fetch trending movies
        try:
            response = requests.get(tmdb_movie_url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                movies = data.get('results', [])
                
                for movie in movies:
                    title = movie.get('title', '')
                    if title and len(title) > 0:
                        trending_terms.append({
                            'trend': title,
                            'breakdown': f"Movie - {movie.get('overview', '')[:100]}...",
                            'link': f"https://www.themoviedb.org/movie/{movie.get('id', '')}",
                            'source': 'tmdb_movie',
                            'content_type': 'movie'
                        })
                print(f"✅ TMDB movies: {len(movies)} movies found")
        except Exception as e:
            print(f"❌ TMDB movies failed: {e}")
        
        # Fetch trending TV shows
        try:
            response = requests.get(tmdb_tv_url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                tv_shows = data.get('results', [])
                
                for show in tv_shows:
                    title = show.get('name', '')
                    if title and len(title) > 2:
                        trending_terms.append({
                            'trend': title,
                            'breakdown': f"TV Show - {show.get('overview', '')[:100]}...",
                            'link': f"https://www.themoviedb.org/tv/{show.get('id', '')}",
                            'source': 'tmdb_tv',
                            'content_type': 'tv'
                        })
                print(f"✅ TMDB TV shows: {len(tv_shows)} shows found")
        except Exception as e:
            print(f"❌ TMDB TV shows failed: {e}")
        
        if trending_terms:
            print(f"✅ TMDB entertainment trending: {len(trending_terms)} total items")
            return trending_terms
                
    except Exception as e:
        print(f"❌ TMDB failed: {e}")
    
    return []
