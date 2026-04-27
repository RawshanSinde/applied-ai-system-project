"""
RAG (Retrieval-Augmented Generation) module for the Music Recommender.

This module uses OpenAI's API to generate personalized explanations for
music recommendations by providing the LLM with:
1. Retrieved songs from the database (retrieval)
2. User preferences and context
3. A structured prompt to generate explanations (generation)
"""

import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()


class RAGExplainer:
    """Generates AI-powered explanations for music recommendations."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize RAG explainer with OpenAI client.

        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
            model: Model to use for generation (default: gpt-3.5-turbo)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )

        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = model

    def generate_explanation(
        self,
        song: Dict,
        user_prefs: Dict,
        score: float,
        top_matching_features: List[str],
    ) -> str:
        """
        Generate a personalized explanation for why a song was recommended.

        Args:
            song: Song dict with id, title, artist, genre, mood, energy, etc.
            user_prefs: User preference dict with target features and weights
            score: Recommendation score (0-1)
            top_matching_features: List of reasons why this song was recommended

        Returns:
            AI-generated explanation string
        """
        # Build context for the LLM
        prompt = f"""You are a music recommendation expert. Generate a brief, friendly explanation (2-3 sentences) 
for why this song is being recommended to a user.

USER PREFERENCES:
- Favorite Genre: {user_prefs.get('genre', 'N/A')}
- Favorite Mood: {user_prefs.get('mood', 'N/A')}
- Target Energy Level: {user_prefs.get('energy', 0.5):.1%}
- Target Danceability: {user_prefs.get('danceability', 0.5):.1%}

RECOMMENDED SONG:
- Title: {song['title']}
- Artist: {song['artist']}
- Genre: {song['genre']}
- Mood: {song['mood']}
- Energy: {song['energy']:.1%}
- Danceability: {song['danceability']:.1%}
- Tempo: {song['tempo_bpm']} BPM
- Valence (Brightness): {song['valence']:.1%}
- Acousticness: {song['acousticness']:.1%}

MATCH SCORE: {score:.1%}

WHAT MATCHED:
{chr(10).join(f'• {feature}' for feature in top_matching_features)}

Generate a natural, conversational explanation that highlights why this song fits their taste. 
Keep it short and engaging, like a friend recommending a song."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150,
            )
            return response.choices[0].message.content.strip()
        except openai.APIError as e:
            # Fallback to basic explanation if API fails
            return self._fallback_explanation(song, top_matching_features)

    def _fallback_explanation(self, song: Dict, features: List[str]) -> str:
        """Fallback explanation if LLM API fails."""
        reasons = " and ".join(features[:2]) if features else "strong match"
        return f"{song['title']} by {song['artist']} is a great fit because: {reasons}."

    def generate_recommendations_summary(
        self, songs_with_context: List[Dict], user_prefs: Dict
    ) -> str:
        """
        Generate a summary explanation of all recommendations at once.

        Args:
            songs_with_context: List of dicts with song, score, features
            user_prefs: User preference dict

        Returns:
            Summary explanation for the entire recommendation set
        """
        song_list = "\n".join(
            [f"- {s['song']['title']} by {s['song']['artist']} (Score: {s['score']:.1%})"
             for s in songs_with_context]
        )

        prompt = f"""You are a music recommendation expert. Generate a brief summary (3-4 sentences) 
explaining this personalized playlist recommendation.

USER PROFILE:
- Favorite Genre: {user_prefs.get('genre', 'N/A')}
- Favorite Mood: {user_prefs.get('mood', 'N/A')}
- Prefers Energy Level: {user_prefs.get('energy', 0.5):.1%}

RECOMMENDED PLAYLIST:
{song_list}

Generate an engaging summary that explains how these songs work together as a cohesive 
recommendation set that matches their taste. Focus on themes and patterns across the songs."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200,
            )
            return response.choices[0].message.content.strip()
        except openai.APIError:
            return "This personalized playlist was curated based on your music preferences."
