# VibeMatch — RAG Music Recommender

A content-based music recommendation system that combines weighted feature scoring with OpenAI-powered natural language explanations, built as part of an Applied AI Systems course.

---

## Original Project

**Music Recommender Simulation** (Modules 1–3)

The original project was a pure content-based filtering system built entirely in Python without any external AI APIs. Its goal was to represent songs and user taste profiles as structured data and score every song in a 20-track catalog against a user's stated preferences — genre, mood, energy, danceability, valence, acousticness, and tempo — using a weighted proximity formula. The system ranked all songs by their score and returned the top matches, with a plain-text breakdown showing exactly which features helped or hurt each recommendation. Seven user profiles were tested, including three realistic taste profiles and four adversarial ones designed to expose edge cases like missing catalog labels, inflated weights, and out-of-range feature values.

---

## What This Project Does and Why It Matters

This project extends the original recommender with a full **RAG (Retrieval-Augmented Generation)** pipeline. Instead of returning a technical score breakdown, the system now passes each top-ranked song — along with the user's preferences and the reasons it scored well — to an OpenAI language model, which generates a short, conversational explanation in plain English.

The result is a system that demonstrates two skills relevant to real-world AI engineering:

1. **Retrieval**: a deterministic, auditable scoring algorithm that selects the best candidates from a catalog.
2. **Generation**: an LLM layer that turns structured data into natural language a user can actually read.

This mirrors how production recommendation systems work at companies like Spotify, YouTube, and Netflix — a fast retrieval layer selects candidates, and a generation or re-ranking layer adds context and personalization.

---

## Architecture Overview

> See [SYSTEM_DIAGRAM.md](SYSTEM_DIAGRAM.md) for the full ASCII diagram.

```
User Preferences → Retriever (score_song) → Top-K Candidates → RAG Generator (GPT-3.5) → CLI Output
                                                                        ↓
                                                                  Fallback Mode
                                                            (API unavailable → technical string)
```

| Component | File | Responsibility |
|---|---|---|
| Orchestrator | `src/main.py` | Loads catalog, iterates profiles, prints output |
| Knowledge Base | `data/songs.csv` | 20-song catalog with 8 audio features per track |
| Retriever | `src/recommender.py` | Weighted scoring, ranking, top-k selection |
| RAG Generator | `src/rag.py` | Builds LLM prompt, calls OpenAI, handles fallback |
| Logger | `src/logger_config.py` | Structured logs to `logs/` at DEBUG through ERROR |

**Data flows one way**: user preferences in → scored candidates → LLM context → explanation out. There is no feedback loop, personalization over time, or collaborative filtering — this is a pure content-based, single-query system.

---

## Setup Instructions

### Requirements

- Python 3.10 or higher
- An [OpenAI API key](https://platform.openai.com/api-keys) (free tier works; costs ~$0.001 per run)

### Step 1 — Clone the repo

```bash
git clone https://github.com/RawshanSinde/applied-ai-system-project.git
cd applied-ai-system-project
```

### Step 2 — Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Add your OpenAI API key

```bash
cp .env.example .env
```

Open `.env` and add your key:

```
OPENAI_API_KEY=sk-your-key-here
```

> `.env` is listed in `.gitignore` and will never be committed.

### Step 5 — Run the recommender

```bash
cd src
python main.py
```

To run without making any API calls (uses technical explanations instead):

```bash
python main.py --no-ai
```

### Step 6 — Run the tests

```bash
# Unit tests (OOP interface)
pytest

# Integration tests (full pipeline, no API key needed)
python test_rag_integration.py
```

Logs are written to `logs/music_recommender_<timestamp>.log` automatically.

---

## Sample Interactions

Each example shows the user preference profile passed in and the AI-generated output returned.

---

### Example 1 — High-Energy Pop

**Input profile**

```python
{
    "genre": "dance pop",  "mood": "confident",
    "energy": 0.78,        "valence": 0.82,
    "danceability": 0.84,  "acousticness": 0.12,
    "tempo_normalized": 0.54,
    "weights": { "energy": 0.25, "mood": 0.20, "danceability": 0.20,
                 "genre": 0.15, "valence": 0.10, "acousticness": 0.10 }
}
```

**Output**

```
============================================================
  TOP RECOMMENDATIONS — High-Energy Pop
============================================================

#1  Can't Tame Her — Zara Larsson
     Score : 0.93 / 1.00
     Genre : dance pop   Mood: confident
     Why   :
             • Can't Tame Her is practically built for your playlist —
               it nails your confident mood, matches your energy level
               almost exactly, and has the high danceability you're
               clearly chasing. This one's a no-brainer.

#2  Espresso — Sabrina Carpenter
     Score : 0.84 / 1.00
     Genre : electropop   Mood: confident
     Why   :
             • Espresso matches your vibe almost perfectly on feel —
               same confident energy, near-identical acousticness, and
               a brightness that lines up with your valence target.
               The only thing holding it back is the genre tag, but
               sonically it belongs right next to Can't Tame Her.

#3  Midnight Sun — Zara Larsson
     Score : 0.77 / 1.00
     Genre : dance pop   Mood: euphoric
     Why   :
             • Midnight Sun hits your genre and audio targets well,
               and "euphoric" sits right next to "confident" in feel.
               If you want something slightly more uplifting than your
               usual playlist, this is the natural next pick.
```

---

### Example 2 — Chill Lofi

**Input profile**

```python
{
    "genre": "lo-fi",  "mood": "chill",
    "energy": 0.25,    "valence": 0.45,
    "danceability": 0.35, "acousticness": 0.70,
    "tempo_normalized": 0.16,
    "weights": { "energy": 0.30, "acousticness": 0.25, "mood": 0.20,
                 "valence": 0.10, "danceability": 0.10, "genre": 0.05 }
}
```

**Output**

```
============================================================
  TOP RECOMMENDATIONS — Chill Lofi
============================================================

#1  Library Rain — Paper Lanterns
     Score : 0.91 / 1.00
     Genre : lofi   Mood: chill
     Why   :
             • Library Rain is exactly what you're looking for —
               a calm, organic-sounding track with low energy and
               high acousticness that's perfect for studying or
               winding down. The gentle tempo keeps things slow
               without feeling static.

#2  Midnight Coding — LoRoom
     Score : 0.87 / 1.00
     Genre : lofi   Mood: chill
     Why   :
             • Midnight Coding is a reliable study companion — low
               energy, warm acoustics, and a chill mood that won't
               pull your focus. It's essentially the same lane as
               Library Rain but with a slightly more electronic texture.

#3  Spacewalk Thoughts — Orbit Bloom
     Score : 0.79 / 1.00
     Genre : ambient   Mood: chill
     Why   :
             • Spacewalk Thoughts is the quietest track in the catalog
               and its energy of 0.28 is the closest thing to your
               target of 0.25. It's ambient rather than lofi, but
               the mood and acoustic warmth make it feel right at home
               in a late-night chill session.
```

---

### Example 3 — Deep Intense Rock

**Input profile**

```python
{
    "genre": "rock",  "mood": "intense",
    "energy": 0.92,   "valence": 0.30,
    "danceability": 0.45, "acousticness": 0.08,
    "tempo_normalized": 0.87,
    "weights": { "energy": 0.30, "mood": 0.25, "genre": 0.20,
                 "valence": 0.10, "danceability": 0.10, "acousticness": 0.05 }
}
```

**Output**

```
============================================================
  TOP RECOMMENDATIONS — Deep Intense Rock
============================================================

#1  Storm Runner — Voltline
     Score : 0.95 / 1.00
     Genre : rock   Mood: intense
     Why   :
             • Storm Runner is the only true rock track in the catalog
               and it delivers exactly what you want — near-maximum
               energy at 0.91, an intense mood, fast tempo at 152 BPM,
               and minimal acousticness. This is the clear #1.

#2  Gym Hero — Max Pulse
     Score : 0.71 / 1.00
     Genre : pop   Mood: intense
     Why   :
             • Gym Hero doesn't have the rock tag, but it matches your
               intensity and energy almost perfectly — 0.93 energy and
               a driving 132 BPM. If Storm Runner isn't enough, this is
               the closest thing to it in feel, even if the genre label
               differs.

#3  Night Drive Loop — Neon Echo
     Score : 0.58 / 1.00
     Genre : synthwave   Mood: moody
     Why   :
             • Night Drive Loop slides in here on energy and tempo more
               than mood — it's moody rather than intense, but the
               electronic edge and 0.75 energy give it a similar drive.
               Consider this a cool-down track after Storm Runner.
```

---

## Design Decisions

### Why RAG over a plain LLM call?

A bare language model call — "recommend me music" — has no grounding in an actual catalog. It would hallucinate song titles or give generic advice. The retrieval-first approach ensures the LLM only explains songs that actually exist and already scored well against the user's measurable preferences. The model's job is communication, not selection.

### Why weighted proximity scoring for retrieval?

The retrieval layer is intentionally deterministic and transparent. A vector embedding approach (e.g., cosine similarity on song embeddings) would be harder to audit and overkill for a 20-track catalog. Weighted proximity scoring means every recommendation can be fully explained: you can trace exactly which features contributed how much to any score. That transparency was important for identifying bugs and bias.

### Why GPT-3.5-turbo?

It is fast, cheap (~$0.001 per run), and more than capable for 2–3 sentence explanations. GPT-4 would produce marginally better prose but at 10–20× the cost per token for this output length. The prompt structure — passing song features, user preferences, match score, and top matching reasons — gives the model enough context to be specific without needing a larger model.

### Trade-offs

| Decision | Benefit | Cost |
|---|---|---|
| Binary categorical scoring (mood/genre) | Simple, auditable | Adjacent labels (e.g. "euphoric" vs "confident") penalized as heavily as total mismatches |
| Tempo weight hardcoded to 0 | Avoids BPM normalization complexity | Tempo appears in output but never affects rankings |
| No weight validation | Keeps scorer simple | Weights summing to > 1.0 silently produce scores above 1.0 |
| Fallback to technical strings on API error | System always returns output | Fallback output is noticeably less useful |
| Single user profile per run | Easy to reason about | No multi-user or group recommendations |

---

## Testing Summary

### What was tested

**Unit tests** (`tests/test_recommender.py`) cover the OOP interface: `Song`, `UserProfile`, and `Recommender`. They verify that `recommend()` returns results sorted with the best match first and that `explain_recommendation()` returns a non-empty string.

**Integration tests** (`test_rag_integration.py`) verify the full pipeline end-to-end without making API calls: `load_songs()` correctly parses the CSV, `score_song()` returns a score in the expected range, `recommend_songs()` returns properly-formatted tuples, and `recommend_songs_with_rag(use_ai=False)` works without an API key.

**Manual adversarial testing** (documented in [model_card.md](model_card.md)) ran seven profiles including four edge cases: a mood that doesn't exist in the catalog, a phantom genre and mood, inflated weights summing to 1.80, and an energy value of 1.5 outside the valid 0–1 range.

### What worked

- The scoring logic correctly surfaces the most musically intuitive results for well-represented profiles. Can't Tame Her and Espresso consistently ranked at the top of high-energy pop profiles for the right reasons.
- The RAG layer produces explanations that are meaningfully specific to each song — not generic filler — because the prompt passes actual feature values and matching reasons.
- The fallback chain works reliably: API error → `_fallback_explanation()` → technical string. The system never crashes on an API failure.
- Structured logging made it easy to trace exactly what the system did on each run, including which songs were scored and which API calls were made.

### What didn't work

- **Silent failures on adversarial inputs**: setting mood to `"sad"` (a label not in the catalog) produced no warning. The mood weight silently contributed 0 to every score, and the system confidently recommended a gym anthem as the top result. There is no out-of-distribution detection.
- **Scores above 1.0**: inflated weights (sum = 1.80) caused scores to exceed the advertised 0–1 range with no validation error.
- **Tempo has no effect**: the tempo weight is hardcoded to 0 in `score_song()`, so it appears in the output breakdown but changes nothing. This was a known shortcut.
- **Catalog depth**: genres with only one song (rock, jazz, ambient) always return the same #1 result regardless of the user's other preferences. There is no diversity in those results.

### What this taught about testing AI systems

The most important lesson was that AI-adjacent systems can produce output that *looks* correct while being completely wrong. A score of 0.67 and a printed explanation give the impression of a working recommendation — but if 20% of the scoring budget was silently discarded because the user's mood label didn't match anything in the catalog, that confidence is false. Testing AI systems requires adversarial inputs and checking the *meaning* of outputs, not just whether the system ran without errors.

---

## Reflection

Building this project changed how I think about the systems behind products I use every day.

The most concrete thing I learned is that a recommender doesn't understand music — it compares numbers. When the system recommended Can't Tame Her at the top of the High-Energy Pop profile, it wasn't because the algorithm understood what a confident, danceable pop song feels like. It was because the numbers attached to that song happened to be the closest to the numbers attached to the user profile. That process works surprisingly well when the catalog is well-matched to the user's taste, and falls apart quietly when it isn't.

The adversarial profiles made "silent failure" a real concept rather than an abstract warning. Watching the system print a confident-looking result for a profile that asked for sad music — and get back Gym Hero — was more instructive than any passing test. The output *looked* like it was working. There was no error, no warning, no low-confidence flag. That is how real recommendation systems develop invisible bias: not through a single obvious mistake, but through weight distributions and catalog gaps that quietly favor certain users while the surface output looks fine.

The RAG layer added a different kind of lesson: language models are powerful communicators but unreliable decision-makers. Using GPT to *explain* a decision made by a deterministic algorithm produced much better results than asking GPT to make the decision itself would have. The retrieval layer handles correctness; the generation layer handles clarity. Keeping those responsibilities separate made both easier to test and improve independently.

For a future employer reading this: the skills demonstrated here — retrieval pipeline design, LLM prompt engineering, fallback handling, adversarial testing, and structured logging — are the same skills involved in building production RAG systems, just at a smaller scale.

---

## Project Structure

```
applied-ai-system-project/
├── .env.example              # API key template (copy to .env)
├── requirements.txt          # Pinned dependencies
├── data/
│   └── songs.csv             # 20-song catalog
├── src/
│   ├── main.py               # Entry point and orchestrator
│   ├── recommender.py        # Scoring, ranking, RAG integration
│   ├── rag.py                # RAGExplainer — OpenAI calls + fallback
│   └── logger_config.py      # Structured logging to logs/
├── tests/
│   └── test_recommender.py   # Unit tests (pytest)
├── test_rag_integration.py   # Integration tests (no API key needed)
├── logs/                     # Runtime logs (auto-created)
├── SYSTEM_DIAGRAM.md         # Full ASCII architecture diagram
├── SETUP.md                  # Detailed setup guide
└── model_card.md             # Bias, limitations, and evaluation
```

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `openai` | 1.3.0 | GPT-3.5-turbo API client |
| `python-dotenv` | 1.0.0 | Load API key from `.env` |
| `pandas` | 2.0.3 | CSV parsing |
| `pytest` | 7.4.0 | Unit testing |
| `streamlit` | 1.28.0 | (Optional) web UI scaffolding |
