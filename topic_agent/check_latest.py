import sqlite3

def check_latest_entries():
    conn = sqlite3.connect('trends.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT keyword, movie_name, imdb_id, timestamp 
        FROM trends 
        ORDER BY timestamp DESC 
        LIMIT 10
    ''')
    
    rows = cursor.fetchall()
    print(f"📊 Latest {len(rows)} database entries:")
    print("=" * 60)
    
    for i, (keyword, movie, imdb, timestamp) in enumerate(rows, 1):
        keyword_short = keyword[:50] + "..." if len(keyword) > 50 else keyword
        imdb_display = imdb if imdb else "❌"
        print(f"{i:2d}. {keyword_short}")
        print(f"    → {movie} [{imdb_display}]")
        print(f"    📅 {timestamp}")
        print("-" * 40)
    
    conn.close()

if __name__ == "__main__":
    check_latest_entries()
