# RAG Music Recommender Setup Guide

This project now includes **Retrieval-Augmented Generation (RAG)** for AI-powered music recommendations!

## What's RAG?

Your music recommender now works in two steps:

1. **Retrieval**: Uses song matching scores to find the top 5 most relevant songs from your database
2. **Generation**: Uses OpenAI's GPT to generate personalized, conversational explanations for *why* each song is recommended

Instead of just seeing technical reasons like "energy matched at 0.78", you'll get natural explanations like:
> "This track has the high energy you love (92% energy) perfect for powering through intense workouts. The dark, brooding mood will keep you focused on heavy lifts."

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `openai` — OpenAI API client
- `python-dotenv` — Environment variable management
- `pandas`, `pytest`, `streamlit` — Original dependencies

### 2. Get an OpenAI API Key

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy it

### 3. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
OPENAI_API_KEY=sk-your-actual-key-here
```

**Important**: Never commit `.env` to git! It's protected by `.gitignore`.

### 4. Run the Recommender

```bash
cd src
python main.py
```

You'll see AI-powered explanations for each song recommendation!

## How to Use in Your Code

### Option 1: Use RAG with AI (Default)

```python
from recommender import load_songs, recommend_songs_with_rag

songs = load_songs("data/songs.csv")
user_prefs = {
    "genre": "pop",
    "mood": "happy",
    "energy": 0.8,
    "weights": {...}
}

# Get recommendations with AI explanations
recommendations = recommend_songs_with_rag(
    user_prefs=user_prefs,
    songs=songs,
    k=5,
    use_ai=True  # ← Enable AI generation
)
```

### Option 2: Use Basic Explanations (No API Calls)

```python
# Turn off AI to use technical explanations or if API is unavailable
recommendations = recommend_songs_with_rag(
    user_prefs=user_prefs,
    songs=songs,
    k=5,
    use_ai=False  # ← Disable AI
)
```

### Option 3: Use Original Non-RAG Function

If you just want the basic scoring without any AI:

```python
from recommender import recommend_songs

recommendations = recommend_songs(user_prefs, songs, k=5)
```

## Architecture

```
Data (songs.csv)
      ↓
   Recommender.score_song()
   [Retrieval Phase]
      ↓
   Top-5 Songs
      ↓
   RAGExplainer.generate_explanation()
   [Generation Phase via OpenAI API]
      ↓
   AI-Powered Recommendations
```

**RAG Module** (`src/rag.py`):
- `RAGExplainer` class handles OpenAI API communication
- `generate_explanation()` — Creates personalized explanation for single song
- `generate_recommendations_summary()` — Creates summary for entire playlist
- Includes fallback explanations if API fails

## Troubleshooting

### "OpenAI API key not found"

- Check that `.env` file exists
- Check that `OPENAI_API_KEY=sk-...` is in the file
- Restart your terminal/IDE after creating `.env`

### "API Rate Limited" or slow responses

- OpenAI APIs have rate limits for free accounts
- Try setting `use_ai=False` to test with basic explanations
- Consider adding delays between API calls for production use

### Want to use a different LLM?

The `RAGExplainer` class can be adapted to use other APIs like:
- Anthropic Claude
- Hugging Face
- Local models

Edit `src/rag.py` to swap the API client.

## Next Steps

- [ ] Add conversation flow (ask follow-up questions about songs)
- [ ] Implement caching to avoid duplicate API calls
- [ ] Add streaming responses for faster feedback
- [ ] Build a Streamlit web UI
- [ ] Add prompt refinement based on user feedback

## Files Modified/Created

- ✅ `src/rag.py` — RAG module (new)
- ✅ `src/recommender.py` — Added `recommend_songs_with_rag()` function
- ✅ `src/main.py` — Updated to use RAG
- ✅ `requirements.txt` — Added `openai`, `python-dotenv`
- ✅ `.env.example` — Template for API keys
- ✅ `.gitignore` — Protects `.env` from git
