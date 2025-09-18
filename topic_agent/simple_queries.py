import sqlite3

def count_total_trends():
    """Count total trends in database"""
    conn = sqlite3.connect('trends.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM trends')
    count = cursor.fetchone()[0]
    conn.close()
    return count

def count_with_imdb():
    """Count trends that have IMDb IDs"""
    conn = sqlite3.connect('trends.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM trends WHERE imdb_id IS NOT NULL')
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_latest_trends(limit=5):
    """Get latest trends"""
    conn = sqlite3.connect('trends.db')
    cursor = conn.cursor()
    cursor.execute('SELECT keyword, movie_name, imdb_id FROM trends ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def search_by_keyword(keyword):
    """Search trends by keyword"""
    conn = sqlite3.connect('trends.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trends WHERE keyword LIKE ?', (f'%{keyword}%',))
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    print("🔍 TRENDS DATABASE QUERIES")
    print("=" * 40)
    
    # Total count
    total = count_total_trends()
    with_imdb = count_with_imdb()
    print(f"📊 Total trends: {total}")
    print(f"🎬 With IMDb IDs: {with_imdb}")
    print(f"❌ Without IMDb IDs: {total - with_imdb}")
    
    print("\n📅 Latest 5 trends:")
    latest = get_latest_trends(5)
    for i, (keyword, movie, imdb) in enumerate(latest, 1):
        imdb_display = imdb if imdb else "❌"
        print(f"{i}. {keyword} → {movie} [{imdb_display}]")
    
    print("\n🔍 Search for 'Deadpool':")
    results = search_by_keyword('Deadpool')
    for row in results:
        print(f"   {row[1]} → {row[2]} [{row[3] or '❌'}]")
