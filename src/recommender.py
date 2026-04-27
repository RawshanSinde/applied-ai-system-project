from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv

    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    int(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Returns a weighted match score (0.0–1.0) and a list of per-feature reason strings for one song."""
    weights = user_prefs["weights"]
    score = 0.0
    reasons = []

    # --- Categorical features: exact match → full weight, no match → 0 ---
    if song["mood"] == user_prefs["mood"]:
        points = weights["mood"]
        score += points
        reasons.append(f"mood match: {song['mood']} (+{points:.2f})")
    else:
        reasons.append(f"mood mismatch: {song['mood']} vs {user_prefs['mood']} (+0.00)")

    if song["genre"] == user_prefs["genre"]:
        points = weights["genre"]
        score += points
        reasons.append(f"genre match: {song['genre']} (+{points:.2f})")
    else:
        reasons.append(f"genre mismatch: {song['genre']} vs {user_prefs['genre']} (+0.00)")

    # --- Numerical features: proximity score × weight ---
    # Tempo must be normalized to 0–1 before comparing (BPM range: 60–152)
    tempo_normalized = (song["tempo_bpm"] - 60) / (152 - 60)

    numerical = [
        ("energy",       song["energy"],       user_prefs["energy"],       weights["energy"]),
        ("danceability", song["danceability"],  user_prefs["danceability"], weights["danceability"]),
        ("valence",      song["valence"],       user_prefs["valence"],      weights["valence"]),
        ("acousticness", song["acousticness"],  user_prefs["acousticness"], weights["acousticness"]),
        ("tempo",        tempo_normalized,      user_prefs["tempo_normalized"], 0.0),  # informational only
    ]

    for feature, song_val, target_val, weight in numerical:
        proximity = 1 - abs(target_val - song_val)
        points = weight * proximity
        score += points
        if weight > 0:
            reasons.append(f"{feature}: {song_val:.2f} vs target {target_val:.2f} → proximity {proximity:.2f} (+{points:.2f})")

    return round(score, 4), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores every song in the catalog, sorts by score descending, and returns the top k as (song, score, explanation) tuples."""
    # Score every song — score_song returns (float, List[str])
    scored = [(song, score, reasons) for song in songs
              for score, reasons in [score_song(user_prefs, song)]]

    # sorted() returns a new list, leaving the original catalog unchanged
    # key=lambda picks the score (index 1) as the sort value
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)

    # Join reasons into a single explanation string for each result
    return [(song, score, " | ".join(reasons)) for song, score, reasons in ranked[:k]]
