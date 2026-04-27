# System Diagram — RAG Music Recommender

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          INPUTS                                     │
│                                                                     │
│   User Preferences (UserProfile)                                    │
│   genre · mood · energy · danceability · valence · acousticness     │
│   + feature weights                                                 │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                    main.py  (Orchestrator)                        │
│   Loads song catalog · Iterates user profiles · Prints results   │
└──────────┬────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────┐
│           data/songs.csv  (Knowledge Base)                       │
│   100 songs · id, title, artist, genre, mood,                    │
│   energy, tempo_bpm, valence, danceability, acousticness         │
└──────────┬───────────────────────────────────────────────────────┘
           │  load_songs()
           ▼
┌──────────────────────────────────────────────────────────────────┐
│          RETRIEVER  —  recommender.py / score_song()             │
│                                                                  │
│   For every song in catalog:                                     │
│     • Categorical match: genre & mood  (exact → full weight)    │
│     • Numerical proximity: energy, danceability, valence,        │
│       acousticness, tempo  (1 − |target − actual|) × weight     │
│     • Sum → weighted score 0.0 – 1.0                            │
│   Sort descending → return top-k candidates + reason strings    │
└──────────┬───────────────────────────────────────────────────────┘
           │ top-k (song, score, [reasons])
           ▼
┌──────────────────────────────────────────────────────────────────┐
│         RAG GENERATOR  —  rag.py / RAGExplainer                  │
│                                                                  │
│   RETRIEVAL context already done ↑                               │
│   GENERATION: for each top-k song                               │
│     • Builds structured prompt: song features + user prefs       │
│       + match score + top 3 matching reasons                     │
│     • Calls OpenAI GPT-3.5-turbo (temperature 0.7, max 150 tok) │
│     • Returns conversational 2–3 sentence explanation            │
│                                                                  │
│   Fallback ──────────────────────────────────────────────────►  │
│   (API error)   technical "reason | reason" string              │
└──────────┬───────────────────────────────────────────────────────┘
           │ (song, score, ai_explanation)[]
           ▼
┌──────────────────────────────────────────────────────────────────┐
│                    OUTPUT  (printed to CLI)                       │
│                                                                  │
│   #1  Song Title — Artist                                        │
│        Score : 0.87 / 1.00                                       │
│        Genre : dance pop   Mood: confident                       │
│        Why   : "This track's driving beat and confident energy   │
│                perfectly match your high-energy playlist taste…" │
└──────────────────────────────────────────────────────────────────┘


                     ┌──────────────────────────────────────────┐
                     │            OBSERVABILITY                 │
                     │  logger_config.py → logs/*.log           │
                     │  DEBUG, INFO, WARNING, ERROR on every    │
                     │  load · score · API call · fallback      │
                     └──────────────────────────────────────────┘


         ┌────────────────────────────────────────────────────────┐
         │              HUMAN / TESTING LAYER                     │
         │                                                        │
         │  tests/test_recommender.py  (unit, pytest)            │
         │    • Song · UserProfile · Recommender OOP interface   │
         │    • Verifies ranked order & non-empty explanations   │
         │                                                        │
         │  test_rag_integration.py  (integration, manual)       │
         │    • load_songs → score_song → recommend_songs        │
         │    • recommend_songs_with_rag (use_ai=False, no key)  │
         │    • Human reviews output quality / AI tone in CLI    │
         └────────────────────────────────────────────────────────┘
```

## Data Flow Summary

| Stage | Component | Role |
|---|---|---|
| Input | `UserProfile` dict | Genre, mood, audio features + weights |
| Storage | `data/songs.csv` | 100-song knowledge base |
| Retrieval | `score_song()` in `src/recommender.py` | Weighted feature scoring → top-k candidates |
| Generation | `RAGExplainer` in `src/rag.py` | GPT-3.5-turbo produces conversational explanations |
| Fallback | `_fallback_explanation()` | Technical strings when API is unavailable |
| Orchestration | `src/main.py` | Runs 3 user profiles end-to-end |
| Observability | `src/logger_config.py` | Structured logs to `logs/` |
| Unit testing | `tests/test_recommender.py` | OOP interface correctness |
| Integration testing | `test_rag_integration.py` | Full pipeline without live API |
| Human eval | CLI output inspection | Subjective quality check of AI explanations |
