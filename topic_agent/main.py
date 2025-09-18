import os
from dotenv import load_dotenv

from trends_agent.graph import build_graph


def main() -> None:
    load_dotenv()
    
    print("🚀 Starting LangGraph Trends Agent...")
    print("=" * 50)
    
    app = build_graph()
    final_state = app.invoke({})

    # Display results
    saved = final_state.get("saved_count", 0)
    classified_results = final_state.get("classified_results", [])
    entertainment_trends = final_state.get("entertainment_trends", [])
    non_entertainment_trends = final_state.get("non_entertainment_trends", [])
    
    print(f"\n📊 RESULTS SUMMARY:")
    print(f"   🎬 Entertainment trends: {len(entertainment_trends)}")
    print(f"   🚫 Non-entertainment trends: {len(non_entertainment_trends)}")
    print(f"   🎯 Classified results: {len(classified_results)}")
    print(f"   💾 Saved to database: {saved}")
    
    if classified_results:
        print(f"\n🎯 CLASSIFIED ENTERTAINMENT CONTENT:")
        for i, result in enumerate(classified_results, 1):
            trend = result.get("trend", "N/A")
            classification = result.get("classification", {})
            content_type = classification.get("content_type", "unknown")
            specific_content = classification.get("specific_content", "N/A")
            confidence = classification.get("confidence", 0.0)
            print(f"   {i}. {trend} → {content_type} ({specific_content}) [Confidence: {confidence:.2f}]")
    
    print(f"\n✅ Agent completed successfully!")
    print(f"💾 Check trends.db for saved results")


if __name__ == "__main__":
    main()


