"""
Tests for the core scoring and recommendation functions.
These test the actual scoring logic, not the OOP stub layer.
"""

import pytest
from recommender import score_song, recommend_songs, load_songs, confidence_label


# ── Fixtures ──────────────────────────────────────────────────────────────────

POP_PREFS = {
    "genre": "pop",
    "mood": "happy",
    "energy": 0.82,
    "valence": 0.84,
    "danceability": 0.79,
    "acousticness": 0.18,
    "tempo_normalized": 0.63,
    "weights": {
        "energy": 0.25,
        "mood": 0.20,
        "danceability": 0.20,
        "genre": 0.15,
        "valence": 0.10,
        "acousticness": 0.10,
    },
}

# Sunrise City — matches POP_PREFS almost perfectly
SUNRISE_CITY = {
    "id": 1, "title": "Sunrise City", "artist": "Neon Echo",
    "genre": "pop", "mood": "happy",
    "energy": 0.82, "tempo_bpm": 118, "valence": 0.84,
    "danceability": 0.79, "acousticness": 0.18,
}

# Library Rain — lofi/chill, low energy, high acousticness: bad match for POP_PREFS
LIBRARY_RAIN = {
    "id": 4, "title": "Library Rain", "artist": "Paper Lanterns",
    "genre": "lofi", "mood": "chill",
    "energy": 0.35, "tempo_bpm": 72, "valence": 0.60,
    "danceability": 0.58, "acousticness": 0.86,
}


# ── score_song ─────────────────────────────────────────────────────────────────

def test_perfect_match_scores_near_one():
    """A song that matches all features of the profile should score close to 1.0."""
    score, _ = score_song(POP_PREFS, SUNRISE_CITY)
    assert score >= 0.90, f"Expected near-perfect score, got {score}"


def test_mismatch_scores_lower_than_match():
    """A song mismatched on genre, mood, and audio features should score lower."""
    match_score, _ = score_song(POP_PREFS, SUNRISE_CITY)
    mismatch_score, _ = score_song(POP_PREFS, LIBRARY_RAIN)
    assert mismatch_score < match_score, (
        f"Mismatched song ({mismatch_score:.3f}) should score below matched song ({match_score:.3f})"
    )


def test_score_song_returns_reason_strings():
    """score_song should return a non-empty list of human-readable reason strings."""
    _, reasons = score_song(POP_PREFS, SUNRISE_CITY)
    assert isinstance(reasons, list), "Reasons should be a list"
    assert len(reasons) > 0, "Reasons list should not be empty"
    assert all(isinstance(r, str) for r in reasons), "Each reason should be a string"


def test_score_stays_in_range_for_valid_input():
    """Score should be between 0.0 and 1.0 for valid inputs."""
    score, _ = score_song(POP_PREFS, LIBRARY_RAIN)
    assert 0.0 <= score <= 1.0, f"Score {score} is outside 0–1 range"


# ── recommend_songs ────────────────────────────────────────────────────────────

def test_recommend_returns_exactly_k():
    """recommend_songs should return exactly k results."""
    songs = [SUNRISE_CITY, LIBRARY_RAIN]
    results = recommend_songs(POP_PREFS, songs, k=2)
    assert len(results) == 2


def test_recommend_sorted_descending():
    """recommend_songs should return results sorted by score, highest first."""
    songs = [SUNRISE_CITY, LIBRARY_RAIN]
    results = recommend_songs(POP_PREFS, songs, k=2)
    scores = [r[1] for r in results]
    assert scores == sorted(scores, reverse=True), "Results must be in descending score order"


def test_recommend_result_is_song_score_explanation_tuple():
    """Each result should be a (dict, float, str) tuple."""
    songs = [SUNRISE_CITY, LIBRARY_RAIN]
    song, score, explanation = recommend_songs(POP_PREFS, songs, k=1)[0]
    assert isinstance(song, dict)
    assert isinstance(score, float)
    assert isinstance(explanation, str)
    assert explanation.strip() != "", "Explanation should not be blank"


# ── load_songs ─────────────────────────────────────────────────────────────────

def test_load_songs_returns_expected_structure():
    """load_songs should return a list of dicts with all required fields."""
    songs = load_songs("data/songs.csv")
    assert isinstance(songs, list)
    assert len(songs) > 0
    required = {"id", "title", "artist", "genre", "mood", "energy",
                "tempo_bpm", "valence", "danceability", "acousticness"}
    assert required.issubset(songs[0].keys()), f"Missing fields: {required - songs[0].keys()}"


def test_load_songs_missing_file_raises():
    """load_songs should raise FileNotFoundError for a path that doesn't exist."""
    with pytest.raises(FileNotFoundError):
        load_songs("data/does_not_exist.csv")


# ── confidence_label ───────────────────────────────────────────────────────────

def test_confidence_label_high():
    assert confidence_label(0.80) == "High"
    assert confidence_label(0.95) == "High"


def test_confidence_label_medium():
    assert confidence_label(0.60) == "Medium"
    assert confidence_label(0.79) == "Medium"


def test_confidence_label_low():
    assert confidence_label(0.59) == "Low"
    assert confidence_label(0.10) == "Low"
