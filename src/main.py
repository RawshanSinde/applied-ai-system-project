"""
Command line runner for the Music Recommender Simulation.

This script demonstrates the RAG (Retrieval-Augmented Generation) music
recommender system with AI-powered explanations.

Usage:
    python main.py                 # Run with AI explanations
    python main.py --no-ai        # Run without AI (fallback mode)
"""

import sys
import os
from pathlib import Path

# Add src to path so we can import modules
sys.path.insert(0, os.path.dirname(__file__))

from recommender import load_songs, recommend_songs_with_rag, confidence_label
from logger_config import logger


def print_recommendations(label: str, recommendations: list) -> None:
    print("\n" + "=" * 60)
    print(f"  {label}")
    print("=" * 60)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n#{rank}  {song['title']} — {song['artist']}")
        print(f"     Score      : {score:.2f} / 1.00  [{confidence_label(score)} confidence]")
        print(f"     Genre      : {song['genre']}   Mood: {song['mood']}")
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
    """
    Main entry point for the music recommender system.
    
    Loads song data and generates recommendations for multiple user profiles,
    demonstrating the RAG system with AI-powered explanations.
    """
    try:
        logger.info("=" * 70)
        logger.info("Starting Music Recommender System")
        logger.info("=" * 70)
        
        # Validate data file exists
        data_file = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")
        if not os.path.exists(data_file):
            logger.error(f"Data file not found: {data_file}")
            print(f"\n❌ ERROR: Song data file not found at {data_file}")
            print("   Please ensure data/songs.csv exists in the project root")
            sys.exit(1)
        
        # Load songs
        logger.info("Loading song catalog...")
        songs = load_songs(data_file)
        print(f"\n✓ Loaded {len(songs)} songs from catalog")
        logger.info(f"Successfully loaded {len(songs)} songs")

        # Define user profiles
        logger.debug("Defining user preference profiles...")
        high_energy_pop = {
            "genre":        "dance pop",
            "mood":         "confident",
            "energy":       0.78,
            "valence":      0.82,
            "danceability": 0.84,
            "acousticness": 0.12,
            "tempo_normalized": 0.54,
            "weights": {
                "energy":           0.25,
                "mood":             0.20,
                "danceability":     0.20,
                "genre":            0.15,
                "valence":          0.10,
                "acousticness":     0.10,
            }
        }

        chill_lofi = {
            "genre":            "lo-fi",
            "mood":             "chill",
            "energy":           0.25,
            "valence":          0.45,
            "danceability":     0.35,
            "acousticness":     0.70,
            "tempo_normalized": 0.16,
            "weights": {
                "energy":           0.30,
                "acousticness":     0.25,
                "mood":             0.20,
                "valence":          0.10,
                "danceability":     0.10,
                "genre":            0.05,
            }
        }

        deep_intense_rock = {
            "genre":            "rock",
            "mood":             "intense",
            "energy":           0.92,
            "valence":          0.30,
            "danceability":     0.45,
            "acousticness":     0.08,
            "tempo_normalized": 0.87,
            "weights": {
                "energy":           0.30,
                "mood":             0.25,
                "genre":            0.20,
                "valence":          0.10,
                "danceability":     0.10,
                "acousticness":     0.05,
            }
        }

        profiles = [
            ("TOP RECOMMENDATIONS — High-Energy Pop",      high_energy_pop),
            ("TOP RECOMMENDATIONS — Chill Lofi",           chill_lofi),
            ("TOP RECOMMENDATIONS — Deep Intense Rock",    deep_intense_rock),
        ]

        # Generate recommendations for each profile
        logger.info(f"Generating recommendations for {len(profiles)} user profiles")
        use_ai = "--no-ai" not in sys.argv
        
        if use_ai:
            logger.info("AI explanations enabled")
            print("\n📝 Using AI-powered explanations from OpenAI")
        else:
            logger.info("AI explanations disabled - using fallback mode")
            print("\n📝 Using technical explanations (AI mode disabled)")

        for label, prefs in profiles:
            try:
                logger.info(f"Generating recommendations for: {label}")
                recommendations = recommend_songs_with_rag(
                    prefs, songs, k=5, use_ai=use_ai
                )
                print_recommendations(label, recommendations)
            except Exception as e:
                logger.error(f"Failed to generate recommendations for {label}: {str(e)}", exc_info=True)
                print(f"\n❌ ERROR: Failed to generate recommendations for {label}")
                print(f"   Details: {str(e)}")
                continue
        
        logger.info("=" * 70)
        logger.info("Recommendation generation completed successfully")
        logger.info("=" * 70)
        print("\n✓ Recommendation generation completed! Check logs/ directory for details.")
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}", exc_info=True)
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}", exc_info=True)
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("Program interrupted by user")
        print("\n⚠️  Program interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error in main: {str(e)}", exc_info=True)
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        print("   Please check logs/ directory for details")
        sys.exit(1)


if __name__ == "__main__":
    main()
