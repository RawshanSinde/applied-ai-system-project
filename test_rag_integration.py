#!/usr/bin/env python3
"""
Quick integration test for RAG Music Recommender

Tests that:
1. Song data loads correctly
2. Scoring functions work
3. RAG module can be imported
4. Recommendation function has correct signature
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from recommender import load_songs, score_song, recommend_songs, recommend_songs_with_rag

def test_load_songs():
    """Test song loading"""
    print("✓ Testing song loading...", end=" ")
    songs = load_songs("data/songs.csv")
    assert len(songs) > 0, "No songs loaded"
    assert "title" in songs[0], "Song missing title"
    print(f"OK ({len(songs)} songs)")
    return songs

def test_scoring(songs):
    """Test basic scoring"""
    print("✓ Testing scoring function...", end=" ")
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "valence": 0.8,
        "danceability": 0.8,
        "acousticness": 0.1,
        "tempo_normalized": 0.5,
        "weights": {
            "energy": 0.25,
            "mood": 0.20,
            "danceability": 0.20,
            "genre": 0.15,
            "valence": 0.10,
            "acousticness": 0.10,
        }
    }
    score, reasons = score_song(user_prefs, songs[0])
    assert 0 <= score <= 2, f"Score out of range: {score}"
    assert len(reasons) > 0, "No reasons provided"
    print("OK")

def test_recommendations(songs):
    """Test basic recommendations without RAG"""
    print("✓ Testing basic recommendations...", end=" ")
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "valence": 0.8,
        "danceability": 0.8,
        "acousticness": 0.1,
        "tempo_normalized": 0.5,
        "weights": {
            "energy": 0.25,
            "mood": 0.20,
            "danceability": 0.20,
            "genre": 0.15,
            "valence": 0.10,
            "acousticness": 0.10,
        }
    }
    recommendations = recommend_songs(user_prefs, songs, k=3)
    assert len(recommendations) <= 3, "Too many recommendations"
    assert len(recommendations[0]) == 3, "Recommendation tuple format wrong"
    print(f"OK ({len(recommendations)} recommendations)")

def test_rag_function(songs):
    """Test RAG function signature (without API calls)"""
    print("✓ Testing RAG function...", end=" ")
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "valence": 0.8,
        "danceability": 0.8,
        "acousticness": 0.1,
        "tempo_normalized": 0.5,
        "weights": {
            "energy": 0.25,
            "mood": 0.20,
            "danceability": 0.20,
            "genre": 0.15,
            "valence": 0.10,
            "acousticness": 0.10,
        }
    }
    # Test without AI (should work without API key)
    recommendations = recommend_songs_with_rag(
        user_prefs, songs, k=3, use_ai=False
    )
    assert len(recommendations) <= 3, "Too many recommendations"
    print("OK (without AI)")
    
    print("✓ RAG module imported successfully...", end=" ")
    from rag import RAGExplainer
    print("OK")

def main():
    print("\n" + "="*50)
    print("RAG Music Recommender - Integration Test")
    print("="*50 + "\n")
    
    try:
        songs = test_load_songs()
        test_scoring(songs)
        test_recommendations(songs)
        test_rag_function(songs)
        
        print("\n" + "="*50)
        print("✅ All tests passed!")
        print("="*50)
        print("\nNext steps:")
        print("1. Create .env file with your OpenAI API key")
        print("2. Run: python src/main.py")
        print("3. See AI-powered recommendations!")
        print("\nFor setup instructions, see RAG_SETUP.md")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
