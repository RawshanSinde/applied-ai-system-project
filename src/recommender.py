import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from rag import RAGExplainer
from logger_config import logger

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
    
    Args:
        csv_path: Path to the CSV file containing song data
        
    Returns:
        List of song dictionaries
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV is malformed or missing required columns
    """
    import csv
    
    logger.info(f"Loading songs from: {csv_path}")
    
    try:
        if not os.path.exists(csv_path):
            logger.error(f"CSV file not found: {csv_path}")
            raise FileNotFoundError(f"Song data file not found: {csv_path}")
        
        songs = []
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            # Validate headers
            if reader.fieldnames is None:
                raise ValueError("CSV file is empty or malformed")
            
            required_fields = {
                "id", "title", "artist", "genre", "mood", "energy",
                "tempo_bpm", "valence", "danceability", "acousticness"
            }
            missing_fields = required_fields - set(reader.fieldnames)
            if missing_fields:
                raise ValueError(f"CSV missing required columns: {missing_fields}")
            
            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                try:
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
                except (ValueError, KeyError) as e:
                    logger.error(f"Error parsing row {row_num}: {str(e)}")
                    raise ValueError(f"Invalid data in row {row_num}: {str(e)}")
        
        logger.info(f"Successfully loaded {len(songs)} songs from {csv_path}")
        return songs
        
    except FileNotFoundError:
        raise
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading songs: {str(e)}", exc_info=True)
        raise

def confidence_label(score: float) -> str:
    """Translate a 0–1 match score into a human-readable confidence tier."""
    if score >= 0.80:
        return "High"
    elif score >= 0.60:
        return "Medium"
    return "Low"


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


def recommend_songs_with_rag(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    use_ai: bool = True,
    api_key: Optional[str] = None,
) -> List[Tuple[Dict, float, str]]:
    """
    Enhanced recommendation system with RAG (Retrieval-Augmented Generation).

    Retrieves top-k songs using scoring, then uses an LLM to generate
    personalized, conversational explanations (generation).

    Args:
        user_prefs: User preference dict with features and weights
        songs: Catalog of songs to recommend from
        k: Number of recommendations to return
        use_ai: If True, use LLM for explanations; if False, use basic scoring explanations
        api_key: OpenAI API key (optional, uses env var if not provided)

    Returns:
        List of (song, score, explanation) tuples with AI-powered explanations
        
    Raises:
        ValueError: If user_prefs is invalid or k > available songs
    """
    logger.info(f"Generating recommendations: k={k}, use_ai={use_ai}, songs_available={len(songs)}")
    
    if k > len(songs):
        logger.warning(f"Requested k={k} but only {len(songs)} songs available. Using all songs.")
        k = len(songs)
    
    if not songs:
        logger.error("No songs available for recommendations")
        raise ValueError("No songs available for recommendations")
    
    try:
        # Step 1: RETRIEVAL — Get top-k candidate songs using traditional scoring
        logger.debug("Starting retrieval phase: scoring all songs")
        scored = [
            (song, score, reasons)
            for song in songs
            for score, reasons in [score_song(user_prefs, song)]
        ]
        ranked = sorted(scored, key=lambda x: x[1], reverse=True)[:k]
        logger.info(f"Retrieved top {len(ranked)} songs from {len(songs)} total")

        # Step 2: GENERATION — Use LLM to create personalized explanations
        if use_ai:
            logger.debug("Starting generation phase: using AI for explanations")
            try:
                explainer = RAGExplainer(api_key=api_key)
                results = []
                for idx, (song, score, reasons) in enumerate(ranked, 1):
                    try:
                        # Get top 2-3 matching features for LLM context
                        top_features = reasons[:3]
                        # Generate AI explanation
                        ai_explanation = explainer.generate_explanation(
                            song, user_prefs, score, top_features
                        )
                        results.append((song, score, ai_explanation))
                        logger.debug(f"Generated explanation {idx}/{len(ranked)} for: {song.get('title', 'Unknown')}")
                    except Exception as e:
                        logger.warning(f"Failed to generate AI explanation for song {idx}, using fallback: {str(e)}")
                        results.append((song, score, " | ".join(reasons)))
                
                logger.info(f"Successfully generated {len(results)} recommendations with AI")
                return results
                
            except Exception as e:
                # Fallback to basic explanations if RAG fails
                logger.warning(f"RAG generation failed: {str(e)}. Falling back to basic explanations.")
                return [
                    (song, score, " | ".join(reasons))
                    for song, score, reasons in ranked
                ]
        else:
            # Return basic explanations without LLM
            logger.debug("Generating basic explanations without AI")
            return [
                (song, score, " | ".join(reasons))
                for song, score, reasons in ranked
            ]
            
    except Exception as e:
        logger.error(f"Fatal error in recommendation generation: {str(e)}", exc_info=True)
        raise
