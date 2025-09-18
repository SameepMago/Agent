import sqlite3
from datetime import datetime

def query_trends():
    """Query and display all trends from the database"""
    conn = sqlite3.connect('trends.db')
    cursor = conn.cursor()
    
    # Get all records
    cursor.execute('SELECT * FROM trends ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    
    print(f"📊 Found {len(rows)} records in trends database\n")
    
    for row in rows:
        id_num, keyword, movie_name, imdb_id, timestamp = row
        imdb_display = imdb_id if imdb_id else "❌ Not found"
        print(f"ID: {id_num:2d} | {timestamp}")
        print(f"   Keyword: {keyword}")
        print(f"   Movie:   {movie_name}")
        print(f"   IMDb:    {imdb_display}")
        print("-" * 50)
    
    conn.close()

def query_recent_trends(limit=5):
    """Query recent trends with IMDb IDs"""
    conn = sqlite3.connect('trends.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT keyword, movie_name, imdb_id, timestamp 
        FROM trends 
        WHERE imdb_id IS NOT NULL 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    
    print(f"🎬 Recent {len(rows)} trends with IMDb IDs:\n")
    
    for row in rows:
        keyword, movie_name, imdb_id, timestamp = row
        print(f"📅 {timestamp}")
        print(f"   🎯 {keyword} → 🎬 {movie_name}")
        print(f"   🔗 IMDb: {imdb_id}")
        print("-" * 40)
    
    conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("           TRENDS DATABASE QUERY TOOL")
    print("=" * 60)
    
    print("\n1️⃣ All Records:")
    query_trends()
    
    print("\n" + "=" * 60)
    print("\n2️⃣ Recent Trends with IMDb IDs:")
    query_recent_trends()
