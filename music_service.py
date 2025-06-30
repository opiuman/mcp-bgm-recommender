"""
Music search and recommendation service using YouTube Music API.
"""
from typing import Dict, List
import logging

from config import AudioConfig
from models import ScriptAnalysis, MusicRecommendation

logger = logging.getLogger(__name__)


class YouTubeMusicService:
    """Service for interacting with YouTube Music API."""
    
    def __init__(self, yt_music_client=None, config: AudioConfig = None):
        self.client = yt_music_client
        self.config = config or AudioConfig()
    
    async def search_tracks(self, search_terms: List[str], target_duration: int) -> List[Dict]:
        """
        Search for music tracks using YouTube Music API.
        
        Args:
            search_terms: List of search terms to use
            target_duration: Target duration in seconds
            
        Returns:
            List of track dictionaries from YouTube Music
        """
        if not self.client:
            logger.info("No YouTube Music client available, using mock data")
            return self._get_mock_tracks(target_duration)
        
        all_results = []
        
        try:
            for term in search_terms:
                logger.debug(f"Searching for: {term}")
                results = self.client.search(
                    term, 
                    filter="songs", 
                    limit=self.config.search_limit_per_term
                )
                
                for result in results:
                    if self._is_suitable_for_shorts(result, target_duration):
                        all_results.append(result)
                        
        except Exception as e:
            logger.error(f"YouTube Music search failed: {e}")
            return self._get_mock_tracks(target_duration)
        
        # Limit total results and remove duplicates
        unique_results = self._deduplicate_tracks(all_results)
        return unique_results[:self.config.max_search_results]
    
    def _is_suitable_for_shorts(self, track: Dict, target_duration: int) -> bool:
        """
        Check if a track is suitable for YouTube shorts.
        
        Args:
            track: Track dictionary from YouTube Music
            target_duration: Target duration in seconds
            
        Returns:
            True if track is suitable, False otherwise
        """
        # Check duration if available
        if 'duration_seconds' in track:
            duration = track['duration_seconds']
            return (duration >= target_duration and 
                   duration <= self.config.max_duration_seconds)
        
        # If no duration info, assume it's suitable
        return True
    
    def _deduplicate_tracks(self, tracks: List[Dict]) -> List[Dict]:
        """Remove duplicate tracks based on videoId."""
        seen_ids = set()
        unique_tracks = []
        
        for track in tracks:
            video_id = track.get('videoId')
            if video_id and video_id not in seen_ids:
                seen_ids.add(video_id)
                unique_tracks.append(track)
        
        return unique_tracks
    
    def _get_mock_tracks(self, duration: int) -> List[Dict]:
        """Return mock track data when YouTube Music API is unavailable."""
        return [
            {
                "title": "Uplifting Corporate Background",
                "artists": [{"name": "Audio Library"}],
                "videoId": "mock_id_1",
                "duration_seconds": min(45, duration + 15)
            },
            {
                "title": "Motivational Instrumental",
                "artists": [{"name": "Background Music"}],
                "videoId": "mock_id_2", 
                "duration_seconds": min(60, duration + 30)
            },
            {
                "title": "Energetic Pop Background",
                "artists": [{"name": "Royalty Free"}],
                "videoId": "mock_id_3",
                "duration_seconds": max(30, duration)
            }
        ]


class MusicRecommendationService:
    """Service for generating music recommendations."""
    
    def __init__(self, music_service: YouTubeMusicService, config: AudioConfig = None):
        self.music_service = music_service
        self.config = config or AudioConfig()
    
    def generate_search_terms(self, analysis: ScriptAnalysis, 
                            genre_preference: str, mood_preference: str) -> List[str]:
        """
        Generate search terms based on script analysis and preferences.
        
        Args:
            analysis: Script analysis results
            genre_preference: User's genre preference
            mood_preference: User's mood preference
            
        Returns:
            List of search terms
        """
        search_terms = []
        
        # Determine primary mood
        primary_mood = (mood_preference if mood_preference != "any" 
                       else analysis.detected_mood)
        
        # Base searches
        search_terms.extend([
            f"{primary_mood} background music",
            f"{analysis.detected_theme} music"
        ])
        
        # Genre-specific searches
        if genre_preference != "any":
            search_terms.extend([
                f"{genre_preference} {primary_mood}",
                f"{genre_preference} instrumental"
            ])
        
        # Pacing-based searches
        if analysis.pacing == "fast":
            search_terms.extend(["upbeat instrumental", "energetic background"])
        elif analysis.pacing == "slow":
            search_terms.extend(["calm instrumental", "ambient background"])
        
        return search_terms[:self.config.max_search_terms]
    
    async def get_recommendations(self, analysis: ScriptAnalysis, genre_preference: str,
                                mood_preference: str, duration: int) -> List[MusicRecommendation]:
        """
        Get music recommendations based on analysis and preferences.
        
        Args:
            analysis: Script analysis results
            genre_preference: User's genre preference
            mood_preference: User's mood preference
            duration: Target duration in seconds
            
        Returns:
            List of music recommendations
        """
        # Generate search terms
        search_terms = self.generate_search_terms(analysis, genre_preference, mood_preference)
        logger.info(f"Generated search terms: {search_terms}")
        
        # Search for tracks
        tracks = await self.music_service.search_tracks(search_terms, duration)
        logger.info(f"Found {len(tracks)} tracks")
        
        # Score and rank recommendations
        recommendations = self._score_and_rank_tracks(
            tracks, analysis, genre_preference, mood_preference
        )
        
        return recommendations[:self.config.max_recommendations]
    
    def _score_and_rank_tracks(self, tracks: List[Dict], analysis: ScriptAnalysis,
                             genre_preference: str, mood_preference: str) -> List[MusicRecommendation]:
        """Score and rank tracks based on relevance."""
        scored_recommendations = []
        
        for track in tracks:
            score = self._calculate_match_score(track, analysis, genre_preference, mood_preference)
            
            recommendation = MusicRecommendation(
                title=track.get("title", "Unknown Title"),
                artist=self._extract_artist_name(track),
                youtube_music_id=track.get("videoId", ""),
                confidence_score=score,
                reason=self._generate_recommendation_reason(track, analysis, score),
                duration=track.get("duration_seconds", 30),
                loop_suitable=track.get("duration_seconds", 30) >= 15
            )
            
            scored_recommendations.append(recommendation)
        
        # Sort by confidence score (highest first)
        return sorted(scored_recommendations, 
                     key=lambda x: x.confidence_score, reverse=True)
    
    def _calculate_match_score(self, track: Dict, analysis: ScriptAnalysis,
                             genre_preference: str, mood_preference: str) -> float:
        """Calculate how well a track matches the requirements."""
        score = 0.5  # Base score
        title_lower = track.get("title", "").lower()
        
        # Mood matching
        target_mood = (mood_preference if mood_preference != "any" 
                      else analysis.detected_mood)
        if target_mood in title_lower:
            score += 0.3
        
        # Theme matching
        if analysis.detected_theme in title_lower:
            score += 0.2
        
        # Keyword matching
        for keyword in analysis.keywords[:5]:
            if keyword in title_lower:
                score += 0.1
        
        # Prefer instrumental/background tracks
        if any(term in title_lower for term in ["instrumental", "background", "bgm"]):
            score += 0.2
        
        # Bonus for exact genre match
        if genre_preference != "any" and genre_preference in title_lower:
            score += 0.15
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _extract_artist_name(self, track: Dict) -> str:
        """Extract artist name from track data."""
        artists = track.get("artists", [])
        if artists and len(artists) > 0:
            return artists[0].get("name", "Unknown Artist")
        return "Unknown Artist"
    
    def _generate_recommendation_reason(self, track: Dict, analysis: ScriptAnalysis, score: float) -> str:
        """Generate explanation for why this track was recommended."""
        if score > 0.8:
            match_level = "Strong match"
        elif score > 0.6:
            match_level = "Good match"
        else:
            match_level = "Moderate match"
        
        reason_parts = [match_level, f"for {analysis.detected_mood} mood"]
        
        if analysis.detected_theme != "general":
            reason_parts.append(f"and {analysis.detected_theme} content")
        
        return " ".join(reason_parts)