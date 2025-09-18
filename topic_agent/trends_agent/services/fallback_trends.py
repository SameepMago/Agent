from typing import List, Dict


def get_fallback_keywords() -> List[str]:
    """Get fallback entertainment keywords when all sources fail"""
    return [
        "Deadpool & Wolverine",
        "Inside Out 2",
        "Dune Part Two",
        "Oppenheimer",
        "Bad Boys: Ride or Die",
        "The Marvels",
        "Barbie",
        "Furiosa",
        "Challengers",
        "The Fall Guy",
        "Stranger Things",
        "Wednesday",
        "The Crown",
        "Game of Thrones",
        "Breaking Bad",
        "Trailer",
        "Box office",
        "Top cast",
        "Oscars",
        "Emmy Awards",
        "Netflix",
        "Streaming",
    ]


def fetch_fallback_trends() -> List[Dict]:
    """Fetch fallback entertainment keywords when all sources fail"""
    fallback_keywords = get_fallback_keywords()
    return [{'trend': term, 'breakdown': 'Fallback entertainment keyword', 'link': '', 'source': 'fallback'} for term in fallback_keywords]
