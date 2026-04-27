"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs_with_rag


def print_recommendations(label: str, recommendations: list) -> None:
    print("\n" + "=" * 60)
    print(f"  {label}")
    print("=" * 60)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n#{rank}  {song['title']} — {song['artist']}")
        print(f"     Score : {score:.2f} / 1.00")
        print(f"     Genre : {song['genre']}   Mood: {song['mood']}")
        print(f"     Why   :")
        # Handle both technical (split by |) and AI-generated (longer) explanations
        if " | " in explanation:
            for reason in explanation.split(" | "):
                print(f"             • {reason}")
        else:
            # For AI-generated explanations, wrap text nicely
            import textwrap
            wrapped = textwrap.fill(
                explanation,
                width=55,
                initial_indent="             • ",
                subsequent_indent="               "
            )
            print(wrapped)
        print("-" * 60)


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # --- Profile 1: High-Energy Pop ---
    # Taste profile derived from user's actual playlist
    # (Sabrina Carpenter, Zara Larsson, Don Toliver, Tory Lanez)
    # Categorical features: exact match scoring
    # Numerical features: proximity scoring — closer to target = higher score
    high_energy_pop = {
        # --- Categorical features ---
        "genre":        "dance pop",   # dominant genre across playlist
        "mood":         "confident",   # upbeat, self-assured tone preferred

        # --- Numerical features (all on 0.0–1.0 scale) ---
        "energy":       0.78,          # high energy but not peak — Espresso/Can't Tame Her range
        "valence":      0.82,          # bright and positive leaning
        "danceability": 0.84,          # highly danceable tracks preferred
        "acousticness": 0.12,          # produced/electronic sound preferred over acoustic

        # --- Tempo (normalized from BPM range 60–152) ---
        # Raw target: ~110 BPM  →  normalized: (110 - 60) / (152 - 60) ≈ 0.54
        "tempo_normalized": 0.54,

        # --- Feature weights (must sum to 1.0) ---
        "weights": {
            "energy":           0.25,  # most important — pace and intensity
            "mood":             0.20,  # emotional context
            "danceability":     0.20,  # core to this user's taste
            "genre":            0.15,  # style tiebreaker
            "valence":          0.10,  # positivity/brightness
            "acousticness":     0.10,  # preference for produced sound
        }
    }

    # --- Profile 2: Chill Lofi ---
    # Low-energy, relaxed background listening — studying or winding down
    # Raw target: ~75 BPM  →  normalized: (75 - 60) / (152 - 60) ≈ 0.16
    chill_lofi = {
        "genre":            "lo-fi",
        "mood":             "chill",

        "energy":           0.25,      # very low energy — calm and unobtrusive
        "valence":          0.45,      # neutral to slightly melancholic
        "danceability":     0.35,      # not meant to be danced to
        "acousticness":     0.70,      # warm, acoustic-leaning textures preferred
        "tempo_normalized": 0.16,      # slow BPM (~75)

        "weights": {
            "energy":           0.30,  # most important — must stay calm
            "acousticness":     0.25,  # texture matters a lot
            "mood":             0.20,  # chill vibe is essential
            "valence":          0.10,  # mild preference for neutral tone
            "danceability":     0.10,  # low priority
            "genre":            0.05,  # loose genre constraint
        }
    }

    # --- Profile 3: Deep Intense Rock ---
    # High-energy, dark-toned guitar-driven tracks — workouts or focus sessions
    # Raw target: ~140 BPM  →  normalized: (140 - 60) / (152 - 60) ≈ 0.87
    deep_intense_rock = {
        "genre":            "rock",
        "mood":             "intense",

        "energy":           0.92,      # near-maximum energy
        "valence":          0.30,      # dark, brooding tone preferred
        "danceability":     0.45,      # moderate — rhythmic but not club-oriented
        "acousticness":     0.08,      # heavily distorted/electric sound
        "tempo_normalized": 0.87,      # fast BPM (~140)

        "weights": {
            "energy":           0.30,  # must be high-intensity
            "mood":             0.25,  # darkness/intensity is the point
            "genre":            0.20,  # genre is a hard constraint here
            "valence":          0.10,  # dark tone matters
            "danceability":     0.10,  # secondary concern
            "acousticness":     0.05,  # minor penalty for acoustic sound
        }
    }

    # ---------------------------------------------------------------------------
    # ADVERSARIAL / EDGE-CASE PROFILES
    # These are designed to stress-test the scoring logic and surface unexpected
    # behaviour — not realistic taste profiles.
    # ---------------------------------------------------------------------------

    # --- Adversarial 1: Contradicting Categorical + Numerical ---
    # BUG TARGET: mood weight is permanently wasted (no catalog song has mood
    # "sad"), so 20 % of the score budget silently disappears and rankings are
    # driven by numerical features alone — user gets high-energy results despite
    # asking for a "sad" mood.
    contradicting_mood_energy = {
        "genre":            "pop",
        "mood":             "sad",        # ← does NOT exist anywhere in the catalog
        "energy":           0.90,         # high-energy target — opposite of "sad"
        "valence":          0.20,         # dark/low positivity
        "danceability":     0.60,
        "acousticness":     0.15,
        "tempo_normalized": 0.70,

        "weights": {
            "mood":             0.20,     # 20 % budget that will ALWAYS score 0
            "energy":           0.30,
            "genre":            0.15,
            "valence":          0.15,
            "danceability":     0.10,
            "acousticness":     0.10,
        }
    }

    # --- Adversarial 2: Phantom Genre + Mood (nothing in catalog matches) ---
    # BUG TARGET: both categorical weights are always wasted — 35 % of the score
    # budget is permanently 0.  Numerical proximity alone determines all rankings.
    # Ask: do the top results still make intuitive sense, or does the scorer
    # surface arbitrary songs?
    phantom_profile = {
        "genre":            "classical",  # ← not in catalog
        "mood":             "melancholic",# ← not in catalog
        "energy":           0.50,
        "valence":          0.40,
        "danceability":     0.50,
        "acousticness":     0.60,
        "tempo_normalized": 0.35,

        "weights": {
            "genre":            0.20,     # 20 % always 0
            "mood":             0.15,     # 15 % always 0 → 35 % total wasted
            "energy":           0.25,
            "valence":          0.20,
            "danceability":     0.10,
            "acousticness":     0.10,
        }
    }

    # --- Adversarial 3: Weights Summing to > 1.0 ---
    # BUG TARGET: score_song never validates or normalises weights.  These weights
    # sum to 1.80, so top scores will exceed 1.00 — breaking the advertised
    # "Score: X / 1.00" contract shown in print_recommendations.
    inflated_weights = {
        "genre":            "pop",
        "mood":             "happy",
        "energy":           0.80,
        "valence":          0.80,
        "danceability":     0.80,
        "acousticness":     0.10,
        "tempo_normalized": 0.50,

        "weights": {
            "energy":           0.30,     # weights sum = 1.80, not 1.00
            "mood":             0.30,
            "danceability":     0.30,
            "genre":            0.30,
            "valence":          0.30,
            "acousticness":     0.30,
        }
    }

    # --- Adversarial 4: Out-of-Range Numerical Value ---
    # BUG TARGET: energy set to 1.5 (above the 0–1 scale).
    # proximity = 1 - abs(1.5 - song_val).  For songs with energy < 0.5 this
    # produces a negative proximity, and with a 40 % energy weight the final
    # score goes negative — which sorted() still handles, but the output breaks
    # the "0.0–1.0" invariant and the ranking is inverted for low-energy songs.
    out_of_range_energy = {
        "genre":            "rock",
        "mood":             "intense",
        "energy":           1.5,          # ← deliberately out of [0, 1]
        "valence":          0.50,
        "danceability":     0.60,
        "acousticness":     0.10,
        "tempo_normalized": 0.80,

        "weights": {
            "energy":           0.40,     # high weight amplifies the out-of-range effect
            "mood":             0.20,
            "genre":            0.15,
            "valence":          0.10,
            "danceability":     0.10,
            "acousticness":     0.05,
        }
    }

    # --- Experimental: High-Energy Pop, energy×2 / genre×0.5 (normalized) ---
    # Raw change: energy 0.25→0.50, genre 0.15→0.075 — sum becomes 1.175.
    # All weights divided by 1.175 to restore a valid sum of 1.00.
    # energy: 0.50/1.175 ≈ 0.43   genre: 0.075/1.175 ≈ 0.06
    # mood:   0.20/1.175 ≈ 0.17   danceability: 0.20/1.175 ≈ 0.17
    # valence: 0.10/1.175 ≈ 0.09  acousticness: 0.10/1.175 ≈ 0.08
    # sum check: 0.43+0.17+0.17+0.06+0.09+0.08 = 1.00 ✓
    high_energy_pop_energy_boosted = {
        "genre":            "dance pop",
        "mood":             "confident",
        "energy":           0.78,
        "valence":          0.82,
        "danceability":     0.84,
        "acousticness":     0.12,
        "tempo_normalized": 0.54,

        "weights": {
            "energy":           0.43,  # was 0.25 — doubled then normalized
            "mood":             0.17,  # was 0.20 — normalized down
            "danceability":     0.17,  # was 0.20 — normalized down
            "genre":            0.06,  # was 0.15 — halved then normalized
            "valence":          0.09,  # was 0.10 — normalized down
            "acousticness":     0.08,  # was 0.10 — normalized down
        }
    }

    profiles = [
        ("TOP RECOMMENDATIONS — High-Energy Pop",                    high_energy_pop),
        ("TOP RECOMMENDATIONS — High-Energy Pop (energy×2/genre÷2)", high_energy_pop_energy_boosted),
        ("TOP RECOMMENDATIONS — Chill Lofi",                         chill_lofi),
        ("TOP RECOMMENDATIONS — Deep Intense Rock",                  deep_intense_rock),
        # --- adversarial ---
        ("[ADVERSARIAL] Contradicting Mood + Energy", contradicting_mood_energy),
        ("[ADVERSARIAL] Phantom Genre + Mood",        phantom_profile),
        ("[ADVERSARIAL] Inflated Weights (sum=1.80)", inflated_weights),
        ("[ADVERSARIAL] Out-of-Range Energy (1.5)",   out_of_range_energy),
    ]

    for label, prefs in profiles:
        recommendations = recommend_songs_with_rag(prefs, songs, k=5, use_ai=True)
        print_recommendations(label, recommendations)


if __name__ == "__main__":
    main()
