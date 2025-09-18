## trends agent

An agent built with LangGraph and Gemini API that ingests trending keywords, filters for movie-related trends, resolves a movie title, looks up the IMDb ID via OMDb, and stores results in SQLite.

### Setup

1. Create virtual environment (Windows PowerShell):
```
py -3 -m venv .venv
./.venv/Scripts/Activate.ps1
```

2. Install dependencies:
```
python -m pip install -U pip
pip install -r requirements.txt
```

3. Configure environment:
```
copy .env.example .env
# edit .env and set GEMINI_API_KEY and OMDB_API_KEY
```

### Run
```
python main.py
```

SQLite database file `trends.db` will be created in the project root.


