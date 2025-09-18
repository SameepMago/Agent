"""
Enhanced web search functionality with article scraping, smart queries and LLM fallback.
"""

import requests
from typing import List, Dict, Optional
import time
from datetime import datetime, timedelta
from trends_agent.services.llm import GeminiLLM
from bs4 import BeautifulSoup
from ddgs import DDGS


def extract_article_date(url: str) -> Optional[datetime]:
    """
    Extract publication date from an article URL.
    
    Args:
        url: Article URL to extract date from
        
    Returns:
        datetime object if date found, None otherwise
    """
    if not url or not url.startswith(('http://', 'https://')):
        return None
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try different date selectors
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="date"]',
            'meta[name="pubdate"]',
            'meta[name="publishdate"]',
            'time[datetime]',
            '.date',
            '.published',
            '.pubdate',
            '.publish-date'
        ]
        
        for selector in date_selectors:
            elements = soup.select(selector)
            for element in elements:
                date_str = None
                if element.name == 'meta':
                    date_str = element.get('content')
                elif element.name == 'time':
                    date_str = element.get('datetime')
                else:
                    date_str = element.get_text(strip=True)
                
                if date_str:
                    # Try to parse various date formats
                    date_formats = [
                        '%Y-%m-%dT%H:%M:%S%z',
                        '%Y-%m-%dT%H:%M:%S',
                        '%Y-%m-%d',
                        '%B %d, %Y',
                        '%b %d, %Y',
                        '%d %B %Y',
                        '%d %b %Y'
                    ]
                    
                    for fmt in date_formats:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
        
        return None
        
    except Exception as e:
        print(f"    ⚠️ Could not extract date from {url}: {e}")
        return None


def scrape_article_content(url: str, max_length: int = 2000) -> str:
    """
    Scrape article content from a URL to get rich context for trend analysis.
    
    Args:
        url: URL to scrape
        max_length: Maximum length of content to return
        
    Returns:
        Extracted article content as string
    """
    if not url or not url.startswith(('http://', 'https://')):
        return ""
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try to find main content areas
        content_selectors = [
            'article',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.content',
            'main',
            '.main-content',
            '[role="main"]',
            '.story-body',
            '.article-body'
        ]
        
        content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = ' '.join([elem.get_text(strip=True) for elem in elements])
                break
        
        # If no specific content area found, get all text
        if not content:
            content = soup.get_text(strip=True)
        
        # Clean up the content
        content = ' '.join(content.split())  # Remove extra whitespace
        
        # Truncate if too long
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        return content
        
    except Exception as e:
        print(f"❌ Failed to scrape article from {url}: {e}")
        return ""


def scrape_trend_articles(trend_data: Dict) -> Dict:
    """
    Scrape article content from trend links to enrich the trend data.
    Skips Google Trends links as they don't contain articles.
    
    Args:
        trend_data: Dictionary containing trend information with link
        
    Returns:
        Enhanced trend data with scraped article content
    """
    trend = trend_data.get("trend", "")
    link = trend_data.get("link", "")
    source = trend_data.get("source", "")
    
    # Skip scraping for Google Trends as their links don't contain articles
    if source == "google_trends" or "trends.google.com" in link:
        print(f"  ⏭️ Skipping article scraping for Google Trends link: {trend}")
        return {**trend_data, "article_content": ""}
    
    if not link:
        return {**trend_data, "article_content": ""}
    
    print(f"  📰 Scraping article for '{trend}' from {link[:50]}...")
    
    article_content = scrape_article_content(link)
    
    if article_content:
        print(f"  ✅ Scraped {len(article_content)} characters of content")
    else:
        print(f"  ⚠️ No content scraped from link")
    
    return {**trend_data, "article_content": article_content}


def search_duckduckgo(query: str, max_results: int = 5, max_age_days: int = 30) -> List[Dict]:
    """
    Search DuckDuckGo using the duckduckgo-search library for reliable results.
    Filters results to only include articles published within the last max_age_days.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        max_age_days: Maximum age of articles in days (default: 30 days)
        
    Returns:
        List of search results with title, url, snippet, and publication_date
    """
    try:
        # Add delay to avoid rate limiting
        time.sleep(0.5)
        
        # Skip search for very short or problematic queries
        if len(query.strip()) < 3 or query.lower() in ['html', 'doctype', 'meta', 'charset']:
            return []
        
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        # Use the duckduckgo-search library
        with DDGS() as ddgs:
            results = []
            for result in ddgs.text(query, max_results=max_results * 2):  # Get more results to filter
                url = result.get("href", "")
                if not url:
                    continue
                
                # Extract publication date
                pub_date = extract_article_date(url)
                
                # Filter by date - only include articles newer than cutoff
                if pub_date and pub_date >= cutoff_date:
                    results.append({
                        "title": result.get("title", ""),
                        "url": url,
                        "snippet": result.get("body", ""),
                        "source": "duckduckgo_library",
                        "publication_date": pub_date.isoformat(),
                        "days_old": (datetime.now() - pub_date).days
                    })
                elif pub_date is None:
                    # If we can't determine the date, include it (assume recent)
                    results.append({
                        "title": result.get("title", ""),
                        "url": url,
                        "snippet": result.get("body", ""),
                        "source": "duckduckgo_library",
                        "publication_date": "unknown",
                        "days_old": "unknown"
                    })
                
                # Stop when we have enough results
                if len(results) >= max_results:
                    break
            
            print(f"    📅 Found {len(results)} recent articles (within {max_age_days} days)")
            return results
        
    except Exception as e:
        print(f"❌ DuckDuckGo search failed for '{query}': {e}")
        return []




def generate_manual_search_queries(trend_data: Dict) -> List[str]:
    """
    Generate manual search queries specifically designed to find if a trend is entertainment content.
    
    Args:
        trend_data: Dictionary containing trend information
        
    Returns:
        List of search query strings designed to find entertainment content
    """
    trend = trend_data.get("trend", "")
    breakdown = trend_data.get("breakdown", "")
    source = trend_data.get("source", "")
    content_type = trend_data.get("content_type", "")
    
    queries = []
    
    # Entertainment-specific queries to determine if it's a show/movie
    if trend:
        # Direct entertainment queries
        queries.extend([
            f"{trend} movie",
            f"{trend} TV show",
            f"{trend} series",
            f"{trend} film",
            f"{trend} trailer",
            f"{trend} cast",
            f"{trend} director",
            f"{trend} IMDb",
            f"{trend} review",
            f"{trend} streaming",
            f"{trend} Netflix",
            f"{trend} Disney",
            f"{trend} HBO",
            f"{trend} Amazon Prime",
            f"{trend} release date",
            f"{trend} box office",
            f"{trend} rating",
            f"{trend} plot",
            f"{trend} genre",
            f"{trend} entertainment news"
        ])
    
    # Add breakdown-specific queries if available
    if breakdown and breakdown != trend:
        queries.extend([
            f"{trend} {breakdown} movie",
            f"{trend} {breakdown} show",
            f"{trend} {breakdown} entertainment"
        ])
    
    # Source-specific entertainment queries
    if source == "tmdb" and content_type:
        if content_type == "movie":
            queries.extend([
                f"{trend} movie review",
                f"{trend} film analysis",
                f"{trend} cinema"
            ])
        elif content_type == "tv":
            queries.extend([
                f"{trend} TV series",
                f"{trend} show episodes",
                f"{trend} television"
            ])
    
    # Remove duplicates and empty queries
    unique_queries = []
    seen = set()
    for query in queries:
        if query and query.strip() and query.strip().lower() not in seen:
            unique_queries.append(query.strip())
            seen.add(query.strip().lower())
    
    return unique_queries[:5]  # Limit to 5 queries per trend


def generate_llm_search_queries(trend_data: Dict) -> List[str]:
    """
    Use LLM to generate smart search queries using trend + breakdown + article content.
    
    Args:
        trend_data: Dictionary containing trend information with article content
        
    Returns:
        List of LLM-generated search query strings
    """
    trend = trend_data.get("trend", "")
    breakdown = trend_data.get("breakdown", "")
    source = trend_data.get("source", "")
    article_content = trend_data.get("article_content", "")
    
    if not trend:
        return []
    
    try:
        llm = GeminiLLM()
        
        # Build context from article content
        article_context = ""
        if article_content:
            article_context = f"""
Article Content (first 1000 chars):
{article_content[:1000]}
"""
        
        prompt = f"""
You are an expert at finding entertainment content (movies, TV shows, web series) on the web.

Given this trending topic: "{trend}"
Breakdown: "{breakdown}"
Source: "{source}"
{article_context}

Based on the trend name, breakdown, and article content, generate 5 specific search queries that would help determine:
1. If this trend is related to entertainment content (movies, TV shows, web series)
2. What specific movie/show/entertainment content this trend refers to
3. Find official information, reviews, cast, directors, studios, streaming platforms

Focus on queries that would return results from:
- IMDb, Wikipedia, official websites
- Entertainment news sites, reviews
- Streaming platforms (Netflix, Disney+, HBO, Amazon Prime, etc.)
- Movie/TV databases and information sites
- Cast, crew, and production information

Use the article content to understand the context and generate more targeted queries.

Return only the search queries, one per line, no explanations.
"""
        
        response = llm.model.generate_content(prompt)
        response_text = response.text if response else ""
        
        if response_text:
            # Parse the response to extract queries
            queries = []
            for line in response_text.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-'):
                    # Clean up the query
                    query = line.replace('"', '').replace("'", '').strip()
                    if query:
                        queries.append(query)
            
            return queries[:5]  # Limit to 5 queries
        
    except Exception as e:
        print(f"❌ LLM query generation failed for '{trend}': {e}")
    
    return []


def generate_search_queries(trend_data: Dict) -> List[str]:
    """
    Generate search queries with smart fallback logic:
    1. Try manual queries first
    2. Test manual query results for entertainment content
    3. If non-entertainment, generate LLM queries and try again
    4. If entertainment or LLM fails, use manual queries
    
    Args:
        trend_data: Dictionary containing trend information
        
    Returns:
        List of search query strings
    """
    trend = trend_data.get("trend", "")
    
    # First try manual queries
    manual_queries = generate_manual_search_queries(trend_data)
    
    if not manual_queries:
        print(f"⚠️ No manual queries generated for '{trend}', using LLM")
        return generate_llm_search_queries(trend_data)
    
    # Test manual queries by searching and classifying results
    print(f"🔍 Testing manual queries for '{trend}'...")
    test_results = []
    for query in manual_queries[:2]:  # Test first 2 manual queries
        try:
            results = search_duckduckgo(query, max_results=3)
            test_results.extend(results)
        except Exception as e:
            print(f"  ❌ Test search failed for '{query}': {e}")
            continue
    
    if not test_results:
        print(f"⚠️ Manual queries returned no results for '{trend}', using LLM")
        return generate_llm_search_queries(trend_data)
    
    # Classify the test results to see if they're entertainment-related
    print(f"🎯 Classifying test results for '{trend}'...")
    classification = classify_entertainment_content_with_llm(trend, test_results, trend_data)
    
    # If manual queries show entertainment content, use them
    if classification.get("is_entertainment", False):
        print(f"✅ Manual queries found entertainment content for '{trend}', using manual queries")
        return manual_queries
    
    # If manual queries show non-entertainment, try LLM queries
    print(f"🤖 Manual queries found non-entertainment content for '{trend}', trying LLM queries...")
    llm_queries = generate_llm_search_queries(trend_data)
    
    if not llm_queries:
        print(f"⚠️ LLM query generation failed for '{trend}', falling back to manual queries")
        return manual_queries
    
    # Test LLM queries as well
    print(f"🔍 Testing LLM queries for '{trend}'...")
    llm_test_results = []
    for query in llm_queries[:2]:  # Test first 2 LLM queries
        try:
            results = search_duckduckgo(query, max_results=3)
            llm_test_results.extend(results)
        except Exception as e:
            print(f"  ❌ LLM test search failed for '{query}': {e}")
            continue
    
    if llm_test_results:
        llm_classification = classify_entertainment_content_with_llm(trend, llm_test_results, trend_data)
        
        # If LLM queries show entertainment content, use them
        if llm_classification.get("is_entertainment", False):
            print(f"✅ LLM queries found entertainment content for '{trend}', using LLM queries")
            return llm_queries
        else:
            print(f"⚠️ LLM queries also found non-entertainment content for '{trend}', using manual queries")
            return manual_queries
    else:
        print(f"⚠️ LLM queries returned no results for '{trend}', using manual queries")
        return manual_queries


def classify_entertainment_content_with_llm(trend: str, search_results: List[Dict], trend_data: Dict = None) -> Dict:
    """
    Use LLM to analyze web search results and determine specific entertainment content.
    
    Args:
        trend: The trending topic name
        search_results: List of web search results for this trend
        trend_data: Additional trend context (breakdown, article content)
        
    Returns:
        Dictionary with detailed classification results including specific content names
    """
    if not search_results:
        return {
            "is_entertainment": False,
            "confidence": 0.0,
            "content_type": "unknown",
            "specific_content": "",
            "reasoning": "No search results to analyze"
        }
    
    try:
        llm = GeminiLLM()
        
        # Prepare search results text for LLM
        results_text = ""
        for i, result in enumerate(search_results[:5]):  # Use top 5 results
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            url = result.get("url", "")
            
            results_text += f"Result {i+1}:\n"
            results_text += f"Title: {title}\n"
            results_text += f"Snippet: {snippet}\n"
            results_text += f"URL: {url}\n\n"
        
        # Add trend context if available
        trend_context = ""
        if trend_data:
            breakdown = trend_data.get("breakdown", "")
            article_content = trend_data.get("article_content", "")
            
            if breakdown:
                trend_context += f"Trend Breakdown: {breakdown}\n"
            if article_content:
                trend_context += f"Article Context: {article_content[:500]}...\n"
        
        prompt = f"""
You are an expert entertainment content classifier. Analyze the following web search results for the trending topic "{trend}" and determine if it's related to ENTERTAINMENT CONTENT ONLY.

ENTERTAINMENT CONTENT DEFINITION:
- Movies (theatrical releases, streaming movies)
- TV shows (series, episodes, seasons)
- Web series (streaming originals, online series)
- Entertainment industry news (movie/TV production, casting, releases)
- Actors, directors, producers, entertainment personalities
- Entertainment awards, festivals, premieres

NOT ENTERTAINMENT CONTENT:
- Sports news, games, players, teams, championships, tournaments, Super Bowl, Olympics
- Politics, government, elections, political figures
- Technology, gadgets, apps, software, hardware (unless entertainment-related)
- General news, world events, current events
- Business, finance, economy, stock market, cryptocurrency, Bitcoin, investments
- Science, health, medical, education, research
- Food, travel, tourism, lifestyle (unless entertainment-related)
- Weather, natural disasters, accidents
- Crime, legal issues, court cases

Trend Context:
{trend_context}

Search Results:
{results_text}

Based on these search results, determine:
- Is this trend ITSELF about movies, TV shows, web series, or entertainment industry?
- The trend must be DIRECTLY about entertainment content, not just mention entertainment in passing
- If yes, identify the SPECIFIC movie/show name
- Determine the content type (movie, TV show, web series, actor, director, entertainment news)
- Provide confidence level
- Explain your reasoning

IMPORTANT: Do NOT classify as entertainment if the trend is about sports, finance, politics, etc., even if entertainment content is mentioned in the search results. The trend itself must be entertainment-focused.

EXAMPLES:
✅ ENTERTAINMENT:
- "Deadpool & Wolverine" → ENTERTAINMENT (movie)
- "Stranger Things Season 5" → ENTERTAINMENT (tv_show)  
- "Oppenheimer" → ENTERTAINMENT (movie)
- "Emmys 2025" → ENTERTAINMENT (entertainment awards)
- "Netflix" → ENTERTAINMENT (streaming platform)
- "Marvel" → ENTERTAINMENT (entertainment studio)
- "Tom Cruise" → ENTERTAINMENT (actor)

❌ NOT ENTERTAINMENT:
- "Super Bowl 2025" → NOT ENTERTAINMENT (sports event)
- "Bitcoin price" → NOT ENTERTAINMENT (finance/cryptocurrency)
- "NFL playoffs" → NOT ENTERTAINMENT (sports)
- "Stock market" → NOT ENTERTAINMENT (finance)
- "Election 2024" → NOT ENTERTAINMENT (politics)
- "iPhone 15" → NOT ENTERTAINMENT (technology)

ONLY classify as entertainment if it's clearly about movies, TV shows, web series, or entertainment industry.

Respond in this exact JSON format:
{{
    "is_entertainment": true/false,
    "confidence": 0.0-1.0,
    "content_type": "movie/tv_show/web_series/entertainment_news/actor/director/other",
    "specific_content": "Exact name of the movie/show/entertainment content if identified",
    "reasoning": "Detailed explanation of classification and specific content identification"
}}
"""
        
        response = llm.model.generate_content(prompt)
        response_text = response.text if response else ""
        
        if response_text:
            # Try to parse JSON response
            import json
            try:
                # Clean up the response to extract JSON
                response = response_text.strip()
                if response.startswith('```json'):
                    response = response[7:]
                if response.endswith('```'):
                    response = response[:-3]
                
                classification = json.loads(response)
                
                # Validate the response structure
                required_keys = ["is_entertainment", "confidence", "content_type", "specific_content", "reasoning"]
                if all(key in classification for key in required_keys):
                    return classification
                    
            except json.JSONDecodeError:
                print(f"❌ Failed to parse LLM JSON response for '{trend}'")
        
        # Fallback classification based on keywords
        return _fallback_classification(trend, search_results)
        
    except Exception as e:
        print(f"❌ LLM classification failed for '{trend}': {e}")
        return _fallback_classification(trend, search_results)


def _fallback_classification(trend: str, search_results: List[Dict]) -> Dict:
    """
    Fallback classification using keyword matching when LLM fails.
    Only classifies as entertainment if it's clearly movies, TV shows, or web series.
    """
    # Entertainment keywords (movies, TV shows, web series)
    entertainment_keywords = [
        "movie", "film", "cinema", "tv show", "series", "television", "streaming",
        "netflix", "disney", "hbo", "amazon prime", "hulu", "imdb", "trailer",
        "cast", "director", "actor", "actress", "studio", "entertainment",
        "box office", "rating", "review", "episode", "season", "premiere",
        "streaming", "web series", "documentary", "animation", "comedy", "drama",
        "thriller", "horror", "romance", "action", "sci-fi", "fantasy"
    ]
    
    # Non-entertainment keywords (sports, politics, etc.)
    non_entertainment_keywords = [
        "sport", "football", "basketball", "soccer", "baseball", "hockey", "tennis",
        "golf", "cricket", "rugby", "olympics", "championship", "tournament",
        "politics", "election", "government", "president", "minister", "parliament",
        "technology", "gadget", "app", "software", "hardware", "computer",
        "business", "finance", "economy", "stock", "market", "investment",
        "science", "health", "medical", "education", "school", "university",
        "food", "restaurant", "cooking", "recipe", "travel", "tourism", "vacation"
    ]
    
    # Check search results for entertainment keywords
    entertainment_score = 0
    non_entertainment_score = 0
    total_results = len(search_results)
    
    for result in search_results:
        title = result.get("title", "").lower()
        snippet = result.get("snippet", "").lower()
        url = result.get("url", "").lower()
        
        text_to_check = f"{title} {snippet} {url}"
        
        # Check for entertainment keywords
        for keyword in entertainment_keywords:
            if keyword in text_to_check:
                entertainment_score += 1
                break  # Count each result only once
        
        # Check for non-entertainment keywords
        for keyword in non_entertainment_keywords:
            if keyword in text_to_check:
                non_entertainment_score += 1
                break  # Count each result only once
    
    # Only classify as entertainment if entertainment score is higher than non-entertainment
    entertainment_confidence = entertainment_score / total_results if total_results > 0 else 0
    non_entertainment_confidence = non_entertainment_score / total_results if total_results > 0 else 0
    
    # More strict threshold - must have clear entertainment indicators and no strong non-entertainment indicators
    is_entertainment = (entertainment_confidence > 0.4 and 
                       entertainment_confidence > non_entertainment_confidence and
                       non_entertainment_confidence < 0.3)
    
    return {
        "is_entertainment": is_entertainment,
        "confidence": entertainment_confidence,
        "content_type": "movie" if is_entertainment else "other",
        "specific_content": trend if is_entertainment else "",
        "reasoning": f"Keyword-based classification (entertainment: {entertainment_score}, non-entertainment: {non_entertainment_score}, total: {total_results})"
    }


def search_and_classify_trends(trends: List[Dict], max_results_per_query: int = 5) -> List[Dict]:
    """
    Enhanced search and classification workflow:
    1. Scrape article content from trend links
    2. Generate smart search queries using trend + breakdown + article content
    3. Search web for each query
    4. Use LLM to classify and identify specific entertainment content
    5. Return classified results
    
    Args:
        trends: List of trend dictionaries
        max_results_per_query: Maximum results per search query
        
    Returns:
        List of classified trend results
    """
    classified_results = []
    
    for trend_data in trends:
        trend = trend_data.get("trend", "")
        if not trend:
            continue
            
        print(f"🔍 Processing trend: {trend}")
        
        # Step 1: Scrape article content from trend link
        enhanced_trend_data = scrape_trend_articles(trend_data)
        
        # Step 2: Generate search queries using enhanced data
        queries = generate_search_queries(enhanced_trend_data)
        print(f"  📝 Generated {len(queries)} search queries")
        
        # Step 3: Search web for this trend
        trend_search_results = []
        for query in queries:
            try:
                search_results = search_duckduckgo(query, max_results_per_query)
                
                # Add trend context to results
                for result in search_results:
                    result.update({
                        "trend": trend,
                        "trend_source": trend_data.get("source", ""),
                        "search_query": query,
                        "trend_breakdown": trend_data.get("breakdown", ""),
                        "trend_link": trend_data.get("link", "")
                    })
                
                trend_search_results.extend(search_results)
                
                # Small delay to be respectful
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  ❌ Search failed for query '{query}': {e}")
                continue
        
        print(f"  🌐 Found {len(trend_search_results)} web results")
        
        # Step 4: Classify using LLM with enhanced context
        if trend_search_results:
            classification = classify_entertainment_content_with_llm(trend, trend_search_results, enhanced_trend_data)
            print(f"  🤖 Classification: {classification['is_entertainment']} ({classification['content_type']}) - Confidence: {classification['confidence']:.2f}")
            if classification.get('specific_content'):
                print(f"  🎬 Specific Content: {classification['specific_content']}")
        else:
            classification = {
                "is_entertainment": False,
                "confidence": 0.0,
                "content_type": "unknown",
                "specific_content": "",
                "reasoning": "No search results found"
            }
        
        # Create classified result
        classified_result = {
            "trend": trend,
            "trend_source": trend_data.get("source", ""),
            "trend_breakdown": trend_data.get("breakdown", ""),
            "trend_link": trend_data.get("link", ""),
            "article_content": enhanced_trend_data.get("article_content", ""),
            "search_results": trend_search_results,
            "classification": classification,
            "total_queries": len(queries),
            "total_search_results": len(trend_search_results)
        }
        
        classified_results.append(classified_result)
    
    print(f"🎯 Processed {len(classified_results)} trends")
    return classified_results


def search_trends(trends: List[Dict], max_results_per_query: int = 3) -> List[Dict]:
    """
    Legacy function - now calls the enhanced search and classification workflow.
    """
    return search_and_classify_trends(trends, max_results_per_query)
