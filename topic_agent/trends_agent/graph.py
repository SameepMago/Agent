from typing import Dict, Annotated
from langgraph.graph import StateGraph, END

from .types import AgentState
from .services.google_trends import fetch_google_trends_csv
from .services.tmdb_trends import fetch_tmdb_trending
from .services.reddit_trends import fetch_reddit_trending
from .services.twitter_trends import fetch_twitter_trending
from .services.web_search import (
    generate_manual_search_queries, 
    search_duckduckgo, 
    classify_entertainment_content_with_llm,
    generate_llm_search_queries,
    scrape_trend_articles
)
from .services.db import TrendsDB


db = TrendsDB()


def fetch_google_trends(state: AgentState) -> AgentState:
    """Fetch from Google Trends CSV using Selenium"""
    print("🔍 Fetching Google Trends CSV...")
    try:
        csv_results = fetch_google_trends_csv()
        if csv_results:
            print(f"✅ Google Trends: {len(csv_results)} items found")
            # Return the complete state with new data
            return {"google_trends": csv_results, **state}
        else:
            print("❌ Google Trends: No results")
            return {"google_trends": [], **state}
    except Exception as e:
        print(f"❌ Google Trends failed: {e}")
        return {"google_trends": [], **state}


def fetch_tmdb_trends(state: AgentState) -> AgentState:
    """Fetch from TMDB (movies and TV shows) - skips LLM"""
    print("🔍 Fetching TMDB trending...")
    try:
        tmdb_results = fetch_tmdb_trending()
        if tmdb_results:
            print(f"✅ TMDB: {len(tmdb_results)} items found")
            # Return the complete state with new data
            return {"tmdb_trends": tmdb_results, **state}
        else:
            print("❌ TMDB: No results")
            return {"tmdb_trends": [], **state}
    except Exception as e:
        print(f"❌ TMDB failed: {e}")
        return {"tmdb_trends": [], **state}


def fetch_reddit_trends(state: AgentState) -> AgentState:
    """Fetch from Reddit /r/movies"""
    print("🔍 Fetching Reddit trends...")
    try:
        reddit_results = fetch_reddit_trending()
        if reddit_results:
            print(f"✅ Reddit: {len(reddit_results)} items found")
            # Return the complete state with new data
            return {"reddit_trends": reddit_results, **state}
        else:
            print("❌ Reddit: No results")
            return {"reddit_trends": [], **state}
    except Exception as e:
        print(f"❌ Reddit failed: {e}")
        return {"reddit_trends": [], **state}


def fetch_twitter_trends(state: AgentState) -> AgentState:
    """Fetch from Twitter trends"""
    print("🔍 Fetching Twitter trends...")
    try:
        twitter_results = fetch_twitter_trending()
        if twitter_results:
            print(f"✅ Twitter: {len(twitter_results)} items found")
            # Return the complete state with new data
            return {"twitter_trends": twitter_results, **state}
        else:
            print("❌ Twitter: No results")
            return {"twitter_trends": [], **state}
    except Exception as e:
        print(f"❌ Twitter failed: {e}")
        return {"twitter_trends": [], **state}


def combine_all_trends(state: AgentState) -> AgentState:
    """Combine all raw trends from all sources"""
    print("🔄 Combining all trends from all sources...")
    
    all_trends = []
    
    # Add Google Trends
    google_trends = state.get("google_trends", [])
    for item in google_trends:
        all_trends.append({
            "trend": item.get("trend", ""),
            "breakdown": item.get("breakdown", ""),
            "link": item.get("link", ""),
            "source": "google_trends"
        })
    
    # Add TMDB trends
    tmdb_trends = state.get("tmdb_trends", [])
    for item in tmdb_trends:
        all_trends.append({
            "trend": item.get("trend", ""),
            "breakdown": item.get("breakdown", ""),
            "link": item.get("link", ""),
            "source": item.get("source", "tmdb"),
            "content_type": item.get("content_type", "")
        })
    
    # Add Reddit trends
    reddit_trends = state.get("reddit_trends", [])
    for item in reddit_trends:
        all_trends.append({
            "trend": item.get("trend", ""),
            "breakdown": item.get("breakdown", ""),
            "link": item.get("link", ""),
            "source": "reddit"
        })
    
    # Add Twitter trends
    twitter_trends = state.get("twitter_trends", [])
    for item in twitter_trends:
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
    
    print(f"🎯 Combined trends: {len(unique_trends)} unique trends from all sources")
    return {"all_trends": unique_trends, "trends_to_process": unique_trends}


def generate_manual_queries(state: AgentState) -> AgentState:
    """Generate manual search queries for all trends"""
    trends_to_process = state.get("trends_to_process", [])
    if not trends_to_process:
        print("🔍 No trends to generate queries for")
        return {"manual_queries": {}}
    
    print(f"🔍 Generating manual queries for {len(trends_to_process)} trends...")
    
    manual_queries = {}
    for trend_data in trends_to_process:
        trend = trend_data.get("trend", "")
        if trend:
            try:
                queries = generate_manual_search_queries(trend_data)
                manual_queries[trend] = queries
                print(f"  ✅ Generated {len(queries)} manual queries for '{trend}'")
            except Exception as e:
                print(f"  ❌ Failed to generate manual queries for '{trend}': {e}")
                manual_queries[trend] = []
    
    print(f"✅ Generated manual queries for {len(manual_queries)} trends")
    return {"manual_queries": manual_queries, "trends_to_process": trends_to_process}


def test_manual_queries(state: AgentState) -> AgentState:
    """Test manual queries by searching and getting results"""
    manual_queries = state.get("manual_queries", {})
    trends_to_process = state.get("trends_to_process", [])
    
    print(f"🔍 DEBUG: manual_queries={len(manual_queries)}, trends_to_process={len(trends_to_process)}")
    
    if not manual_queries:
        print("🔍 No manual queries to test")
        return {"manual_query_results": {}}
    
    print(f"🔍 Testing manual queries for {len(manual_queries)} trends...")
    
    manual_query_results = {}
    for trend_data in trends_to_process:
        trend = trend_data.get("trend", "")
        queries = manual_queries.get(trend, [])
        
        if not queries:
            continue
            
        print(f"  🔍 Testing queries for '{trend}'...")
        test_results = []
        
        # Test first 2 queries
        for query in queries[:2]:
            try:
                results = search_duckduckgo(query, max_results=3, max_age_days=30)
                test_results.extend(results)
            except Exception as e:
                print(f"    ❌ Test search failed for '{query}': {e}")
                continue
        
        manual_query_results[trend] = test_results
        print(f"    ✅ Got {len(test_results)} test results for '{trend}'")
    
    print(f"✅ Tested manual queries for {len(manual_query_results)} trends")
    return {"manual_query_results": manual_query_results, "trends_to_process": trends_to_process}


def classify_manual_entertainment(state: AgentState) -> AgentState:
    """Classify manual query results to determine if entertainment"""
    manual_query_results = state.get("manual_query_results", {})
    trends_to_process = state.get("trends_to_process", [])
    
    if not manual_query_results:
        print("🎯 No manual query results to classify")
        return {"manual_classifications": {}, "entertainment_trends": [], "non_entertainment_trends": []}
    
    print(f"🎯 Classifying manual query results for {len(manual_query_results)} trends...")
    
    manual_classifications = {}
    entertainment_trends = []
    non_entertainment_trends = []
    
    for trend_data in trends_to_process:
        trend = trend_data.get("trend", "")
        test_results = manual_query_results.get(trend, [])
        
        if not test_results:
            print(f"  ⚠️ No test results for '{trend}', marking as non-entertainment")
            non_entertainment_trends.append(trend_data)
            continue
        
        print(f"  🎯 Classifying results for '{trend}'...")
        try:
            classification = classify_entertainment_content_with_llm(trend, test_results, trend_data)
            manual_classifications[trend] = classification
            
            if classification.get("is_entertainment", False):
                print(f"    ✅ '{trend}' classified as ENTERTAINMENT")
                entertainment_trends.append(trend_data)
            else:
                print(f"    ❌ '{trend}' classified as NON-ENTERTAINMENT")
                non_entertainment_trends.append(trend_data)
                
        except Exception as e:
            print(f"    ❌ Classification failed for '{trend}': {e}")
            non_entertainment_trends.append(trend_data)
    
    print(f"✅ Classification complete:")
    print(f"   🎬 Entertainment trends: {len(entertainment_trends)}")
    print(f"   🚫 Non-entertainment trends: {len(non_entertainment_trends)}")
    
    return {
        "manual_classifications": manual_classifications,
        "entertainment_trends": entertainment_trends,
        "non_entertainment_trends": non_entertainment_trends
    }


def generate_llm_queries(state: AgentState) -> AgentState:
    """Generate LLM queries for non-entertainment trends"""
    non_entertainment_trends = state.get("non_entertainment_trends", [])
    
    if not non_entertainment_trends:
        print("🤖 No non-entertainment trends for LLM query generation")
        return {"llm_queries": {}}
    
    print(f"🤖 Generating LLM queries for {len(non_entertainment_trends)} non-entertainment trends...")
    
    llm_queries = {}
    for trend_data in non_entertainment_trends:
        trend = trend_data.get("trend", "")
        if trend:
            try:
                queries = generate_llm_search_queries(trend_data)
                llm_queries[trend] = queries
                print(f"  ✅ Generated {len(queries)} LLM queries for '{trend}'")
            except Exception as e:
                print(f"  ❌ Failed to generate LLM queries for '{trend}': {e}")
                llm_queries[trend] = []
    
    print(f"✅ Generated LLM queries for {len(llm_queries)} trends")
    return {"llm_queries": llm_queries}


def test_llm_queries(state: AgentState) -> AgentState:
    """Test LLM queries by searching and getting results"""
    llm_queries = state.get("llm_queries", {})
    non_entertainment_trends = state.get("non_entertainment_trends", [])
    
    if not llm_queries:
        print("🔍 No LLM queries to test")
        return {"llm_query_results": {}}
    
    print(f"🔍 Testing LLM queries for {len(llm_queries)} trends...")
    
    llm_query_results = {}
    for trend_data in non_entertainment_trends:
        trend = trend_data.get("trend", "")
        queries = llm_queries.get(trend, [])
        
        if not queries:
            continue
            
        print(f"  🔍 Testing LLM queries for '{trend}'...")
        test_results = []
        
        # Test first 2 queries
        for query in queries[:2]:
            try:
                results = search_duckduckgo(query, max_results=3, max_age_days=30)
                test_results.extend(results)
            except Exception as e:
                print(f"    ❌ LLM test search failed for '{query}': {e}")
                continue
        
        llm_query_results[trend] = test_results
        print(f"    ✅ Got {len(test_results)} LLM test results for '{trend}'")
    
    print(f"✅ Tested LLM queries for {len(llm_query_results)} trends")
    return {"llm_query_results": llm_query_results}


def classify_llm_entertainment(state: AgentState) -> AgentState:
    """Classify LLM query results to determine if entertainment"""
    llm_query_results = state.get("llm_query_results", {})
    non_entertainment_trends = state.get("non_entertainment_trends", [])
    
    if not llm_query_results:
        print("🎯 No LLM query results to classify")
        return {"llm_classifications": {}}
    
    print(f"🎯 Classifying LLM query results for {len(llm_query_results)} trends...")
    
    llm_classifications = {}
    final_entertainment_trends = []
    final_non_entertainment_trends = []
    
    for trend_data in non_entertainment_trends:
        trend = trend_data.get("trend", "")
        test_results = llm_query_results.get(trend, [])
        
        if not test_results:
            print(f"  ⚠️ No LLM test results for '{trend}', keeping as non-entertainment")
            final_non_entertainment_trends.append(trend_data)
            continue
        
        print(f"  🎯 Classifying LLM results for '{trend}'...")
        try:
            classification = classify_entertainment_content_with_llm(trend, test_results, trend_data)
            llm_classifications[trend] = classification
            
            if classification.get("is_entertainment", False):
                print(f"    ✅ '{trend}' re-classified as ENTERTAINMENT with LLM queries")
                final_entertainment_trends.append(trend_data)
            else:
                print(f"    ❌ '{trend}' still classified as NON-ENTERTAINMENT with LLM queries")
                final_non_entertainment_trends.append(trend_data)
                
        except Exception as e:
            print(f"    ❌ LLM classification failed for '{trend}': {e}")
            final_non_entertainment_trends.append(trend_data)
    
    # Combine with original entertainment trends
    original_entertainment = state.get("entertainment_trends", [])
    all_entertainment = original_entertainment + final_entertainment_trends
    
    print(f"✅ LLM classification complete:")
    print(f"   🎬 Total entertainment trends: {len(all_entertainment)}")
    print(f"   🚫 Final non-entertainment trends: {len(final_non_entertainment_trends)}")
    
    return {
        "llm_classifications": llm_classifications,
        "entertainment_trends": all_entertainment,
        "non_entertainment_trends": final_non_entertainment_trends
    }


def execute_final_searches(state: AgentState) -> AgentState:
    """Execute final web searches for all entertainment trends"""
    entertainment_trends = state.get("entertainment_trends", [])
    manual_queries = state.get("manual_queries", {})
    llm_queries = state.get("llm_queries", {})
    
    if not entertainment_trends:
        print("🔍 No entertainment trends to search")
        return {"final_search_results": {}}
    
    print(f"🔍 Executing final searches for {len(entertainment_trends)} entertainment trends...")
    
    final_search_results = {}
    for trend_data in entertainment_trends:
        trend = trend_data.get("trend", "")
        if not trend:
            continue
        
        print(f"  🔍 Final search for '{trend}'...")
        
        # Determine which queries to use
        queries = manual_queries.get(trend, [])
        if not queries:
            queries = llm_queries.get(trend, [])
        
        if not queries:
            print(f"    ⚠️ No queries available for '{trend}'")
            continue
        
        # Execute searches with all queries
        search_results = []
        for query in queries:
            try:
                results = search_duckduckgo(query, max_results=5, max_age_days=30)
                for result in results:
                    result["search_query"] = query
                search_results.extend(results)
            except Exception as e:
                print(f"    ❌ Search failed for '{query}': {e}")
                continue
        
        final_search_results[trend] = search_results
        print(f"    ✅ Got {len(search_results)} final results for '{trend}'")
    
    print(f"✅ Final searches completed for {len(final_search_results)} trends")
    return {"final_search_results": final_search_results}


def classify_final_entertainment(state: AgentState) -> AgentState:
    """Final classification of entertainment trends with full search results"""
    entertainment_trends = state.get("entertainment_trends", [])
    final_search_results = state.get("final_search_results", {})
    
    if not entertainment_trends:
        print("🎯 No entertainment trends to classify")
        return {"final_classifications": {}, "classified_results": []}
    
    print(f"🎯 Final classification for {len(entertainment_trends)} entertainment trends...")
    
    final_classifications = {}
    classified_results = []
    
    for trend_data in entertainment_trends:
        trend = trend_data.get("trend", "")
        search_results = final_search_results.get(trend, [])
        
        if not search_results:
            print(f"  ⚠️ No search results for '{trend}', skipping")
            continue
        
        print(f"  🎯 Final classification for '{trend}'...")
        try:
            classification = classify_entertainment_content_with_llm(trend, search_results, trend_data)
            final_classifications[trend] = classification
            
            # Create classified result
            classified_result = {
                "trend": trend,
                "trend_source": trend_data.get("source", ""),
                "search_results": search_results,
                "classification": classification,
                "article_content": ""  # Could add article scraping here if needed
            }
            classified_results.append(classified_result)
            
            print(f"    ✅ Final classification for '{trend}': {classification.get('content_type', 'unknown')}")
            
        except Exception as e:
            print(f"    ❌ Final classification failed for '{trend}': {e}")
            continue
    
    print(f"✅ Final classification complete for {len(classified_results)} trends")
    return {"final_classifications": final_classifications, "classified_results": classified_results}


def resolve_omdb_ids(state: AgentState) -> AgentState:
    """Resolve IMDb IDs for identified entertainment content"""
    classified_results = state.get("classified_results", [])
    
    if not classified_results:
        print("🎬 No classified results for OMDB resolution")
        return {"omdb_results": {}}
    
    print(f"🎬 Resolving IMDb IDs for {len(classified_results)} classified results...")
    
    omdb_results = {}
    for result in classified_results:
        trend = result.get("trend", "")
        classification = result.get("classification", {})
        specific_content = classification.get("specific_content", "")
        
        if not specific_content:
            print(f"  ⚠️ No specific content identified for '{trend}', skipping OMDB")
            continue
        
        print(f"  🎬 Resolving IMDb ID for '{specific_content}'...")
        try:
            # Import OMDB service
            from trends_agent.services.omdb import get_imdb_id
            
            imdb_data = get_imdb_id(specific_content)
            if imdb_data:
                omdb_results[trend] = imdb_data
                print(f"    ✅ Found IMDb ID: {imdb_data.get('imdb_id', 'N/A')}")
            else:
                print(f"    ❌ No IMDb ID found for '{specific_content}'")
                
        except Exception as e:
            print(f"    ❌ OMDB resolution failed for '{specific_content}': {e}")
            continue
    
    print(f"✅ OMDB resolution complete for {len(omdb_results)} trends")
    return {"omdb_results": omdb_results}


def save_to_db(state: AgentState) -> AgentState:
    """Save all classified results to database"""
    classified_results = state.get("classified_results", []) or []
    omdb_results = state.get("omdb_results", {})
    
    if not classified_results:
        print("💾 No classified results to save")
        return {"saved_count": 0, "classified_results": []}
    
    print("💾 Saving classified results to database...")
    try:
        # Convert classified results to items format for database
        items = []
        for result in classified_results:
            trend = result.get("trend", "")
            classification = result.get("classification", {})
            search_results = result.get("search_results", [])
            omdb_data = omdb_results.get(trend, {})
            
            # Only save if it's classified as entertainment content
            if classification.get("is_entertainment", False):
                # Create one item per search result
                for search_result in search_results:
                    items.append({
                        "keyword": trend,
                        "movie_name": search_result.get("title", ""),
                        "imdb_id": omdb_data.get("imdb_id", ""),
                        "source": result.get("trend_source", ""),
                        "link": search_result.get("url", ""),
                        "search_query": search_result.get("search_query", ""),
                        "snippet": search_result.get("snippet", ""),
                        "content_type": classification.get("content_type", ""),
                        "confidence": classification.get("confidence", 0.0),
                        "reasoning": classification.get("reasoning", ""),
                        "specific_content": classification.get("specific_content", ""),
                        "article_content": result.get("article_content", "")
                    })
        
        saved = db.save_items(items)
        print(f"💾 Saved to database: {saved} entertainment search results")
        return {"saved_count": saved, "classified_results": classified_results}
    except Exception as e:
        print(f"❌ Database save failed: {e}")
        return {"saved_count": 0, "classified_results": classified_results}


def build_graph() -> StateGraph:
    """Build the new LangGraph workflow with smart query generation and conditional routing"""
    print("🔧 Building new LangGraph with smart query flow...")
    
    graph = StateGraph(AgentState)
    
    # Data collection nodes - fetch from all sources
    graph.add_node("fetch_google_trends", fetch_google_trends)
    graph.add_node("fetch_tmdb_trends", fetch_tmdb_trends)
    graph.add_node("fetch_reddit_trends", fetch_reddit_trends)
    graph.add_node("fetch_twitter_trends", fetch_twitter_trends)
    
    # Data processing
    graph.add_node("combine_all_trends", combine_all_trends)
    
    # Manual query generation and testing
    graph.add_node("generate_manual_queries", generate_manual_queries)
    graph.add_node("test_manual_queries", test_manual_queries)
    graph.add_node("classify_manual_entertainment", classify_manual_entertainment)
    
    # LLM query generation for non-entertainment trends
    graph.add_node("generate_llm_queries", generate_llm_queries)
    graph.add_node("test_llm_queries", test_llm_queries)
    graph.add_node("classify_llm_entertainment", classify_llm_entertainment)
    
    # Final search and classification
    graph.add_node("execute_final_searches", execute_final_searches)
    graph.add_node("classify_final_entertainment", classify_final_entertainment)
    
    # OMDB resolution and storage
    graph.add_node("resolve_omdb_ids", resolve_omdb_ids)
    graph.add_node("save_to_db", save_to_db)
    
    # Set entry point
    graph.set_entry_point("fetch_google_trends")
    
    # Sequential execution flow
    # 1. Data collection (sequential to avoid rate limits)
    graph.add_edge("fetch_google_trends", "fetch_tmdb_trends")
    graph.add_edge("fetch_tmdb_trends", "fetch_reddit_trends")
    graph.add_edge("fetch_reddit_trends", "fetch_twitter_trends")
    
    # 2. Combine all trends
    graph.add_edge("fetch_twitter_trends", "combine_all_trends")
    
    # 3. Manual query generation and testing
    graph.add_edge("combine_all_trends", "generate_manual_queries")
    graph.add_edge("generate_manual_queries", "test_manual_queries")
    graph.add_edge("test_manual_queries", "classify_manual_entertainment")
    
    # 4. Conditional routing: if non-entertainment trends exist, generate LLM queries
    def should_generate_llm_queries(state: AgentState) -> str:
        non_entertainment = state.get("non_entertainment_trends", [])
        if non_entertainment:
            return "generate_llm_queries"
        else:
            return "execute_final_searches"
    
    graph.add_conditional_edges(
        "classify_manual_entertainment",
        should_generate_llm_queries,
        {
            "generate_llm_queries": "generate_llm_queries",
            "execute_final_searches": "execute_final_searches"
        }
    )
    
    # 5. LLM query flow (if needed)
    graph.add_edge("generate_llm_queries", "test_llm_queries")
    graph.add_edge("test_llm_queries", "classify_llm_entertainment")
    graph.add_edge("classify_llm_entertainment", "execute_final_searches")
    
    # 6. Final search and classification
    graph.add_edge("execute_final_searches", "classify_final_entertainment")
    
    # 7. OMDB resolution and storage
    graph.add_edge("classify_final_entertainment", "resolve_omdb_ids")
    graph.add_edge("resolve_omdb_ids", "save_to_db")
    graph.add_edge("save_to_db", END)
    
    print("✅ New LangGraph with smart query flow built successfully!")
    return graph.compile()
