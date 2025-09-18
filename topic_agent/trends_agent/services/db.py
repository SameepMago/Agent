from __future__ import annotations

from typing import List, Dict
from sqlalchemy import create_engine, text


CREATE_TABLE_SQL = (
    """
    CREATE TABLE IF NOT EXISTS trends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT,
        movie_name TEXT,
        imdb_id TEXT,
        source TEXT,
        link TEXT,
        search_query TEXT,
        snippet TEXT,
        content_type TEXT,
        confidence REAL,
        reasoning TEXT,
        specific_content TEXT,
        article_content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
)


class TrendsDB:
    def __init__(self, uri: str = "sqlite:///trends.db") -> None:
        self.engine = create_engine(uri, future=True)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self.engine.begin() as conn:
            conn.execute(text(CREATE_TABLE_SQL))

    def save_items(self, items: List[Dict]) -> int:
        if not items:
            return 0
        inserted = 0
        with self.engine.begin() as conn:
            for item in items:
                conn.execute(
                    text(
                        """INSERT INTO trends (
                            keyword, movie_name, imdb_id, source, link, 
                            search_query, snippet, content_type, confidence, reasoning,
                            specific_content, article_content
                        ) VALUES (
                            :keyword, :movie_name, :imdb_id, :source, :link,
                            :search_query, :snippet, :content_type, :confidence, :reasoning,
                            :specific_content, :article_content
                        )"""
                    ),
                    {
                        "keyword": item.get("keyword"),
                        "movie_name": item.get("movie_name"),
                        "imdb_id": item.get("imdb_id"),
                        "source": item.get("source"),
                        "link": item.get("link"),
                        "search_query": item.get("search_query"),
                        "snippet": item.get("snippet"),
                        "content_type": item.get("content_type"),
                        "confidence": item.get("confidence"),
                        "reasoning": item.get("reasoning"),
                        "specific_content": item.get("specific_content"),
                        "article_content": item.get("article_content"),
                    },
                )
                inserted += 1
        return inserted

    def get_all_items(self) -> List[Dict]:
        """Retrieve all items from the database"""
        with self.engine.begin() as conn:
            result = conn.execute(text("SELECT * FROM trends ORDER BY timestamp DESC"))
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]


# Convenience functions
def save_items(items: List[Dict]) -> int:
    """Save items to database"""
    db = TrendsDB()
    return db.save_items(items)

def get_all_items() -> List[Dict]:
    """Get all items from database"""
    db = TrendsDB()
    return db.get_all_items()


