"""
Data models for the Find BGM MCP server.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class ScriptAnalysis:
    """Results of script content analysis."""
    detected_mood: str
    detected_theme: str
    pacing: str
    sentiment_score: float
    keywords: List[str]
    all_detected_moods: List[str]
    all_detected_themes: List[str]


@dataclass
class MusicRecommendation:
    """A single music recommendation."""
    title: str
    artist: str
    youtube_music_id: str
    confidence_score: float
    reason: str
    duration: int
    loop_suitable: bool


@dataclass
class RecommendationRequest:
    """Request parameters for music recommendations."""
    script: str
    duration: int
    genre_preference: str = "any"
    mood_preference: str = "any"
    content_type: str = "other"
    
    def validate(self) -> None:
        """Validate request parameters."""
        if not self.script or not self.script.strip():
            raise ValueError("Script cannot be empty")
        
        if not (15 <= self.duration <= 60):
            raise ValueError("Duration must be between 15 and 60 seconds")


@dataclass
class RecommendationResponse:
    """Complete response with analysis and recommendations."""
    analysis: ScriptAnalysis
    recommendations: List[MusicRecommendation]
    input_parameters: Dict[str, Any]
    search_info: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "analysis": {
                "detected_mood": self.analysis.detected_mood,
                "detected_theme": self.analysis.detected_theme,
                "pacing": self.analysis.pacing,
                "sentiment_score": self.analysis.sentiment_score,
                "keywords": self.analysis.keywords,
                "all_detected_moods": self.analysis.all_detected_moods,
                "all_detected_themes": self.analysis.all_detected_themes
            },
            "recommendations": [
                {
                    "title": rec.title,
                    "artist": rec.artist,
                    "youtube_music_id": rec.youtube_music_id,
                    "confidence_score": rec.confidence_score,
                    "reason": rec.reason,
                    "duration": rec.duration,
                    "loop_suitable": rec.loop_suitable
                }
                for rec in self.recommendations
            ],
            "input_parameters": self.input_parameters,
            "search_info": self.search_info
        }