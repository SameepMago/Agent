#!/usr/bin/env python3
"""
Quick script to check database contents
"""

from trends_agent.services.db import get_all_items

def main():
    items = get_all_items()
    print(f"Total items in database: {len(items)}")
    if items:
        print(f"\nAvailable columns: {list(items[0].keys())}")
        print("\nLast 10 items:")
        for i, item in enumerate(items[-10:]):
            print(f"{i+1}. {item.get('keyword', 'N/A')} - {item.get('movie_name', 'N/A')} - {item.get('specific_content', 'N/A')} - {item.get('reasoning', 'N/A')[:50]}...")

if __name__ == "__main__":
    main()
