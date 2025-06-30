"""
Configuration management for the Find BGM MCP server.
"""
import os
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class ServerConfig:
    """Server configuration settings."""
    name: str = "find-bgm-server"
    version: str = "0.1.0"
    log_level: str = "INFO"
    oauth_file: str = "oauth.json"


@dataclass
class AudioConfig:
    """Audio and music-related configuration."""
    max_duration_seconds: int = 300  # 5 minutes
    search_limit_per_term: int = 10
    max_search_terms: int = 5
    max_search_results: int = 20
    max_recommendations: int = 5


class ContentCategories:
    """Content categorization constants."""
    
    GENRES = [
        "pop", "electronic", "chill", "rock", "hip-hop", 
        "classical", "ambient", "any"
    ]
    
    MOODS = [
        "upbeat", "calm", "dramatic", "energetic", 
        "relaxed", "motivational", "any"
    ]
    
    CONTENT_TYPES = [
        "comedy", "educational", "lifestyle", "fitness", 
        "cooking", "travel", "tech", "other"
    ]
    
    MOOD_KEYWORDS: Dict[str, List[str]] = {
        'upbeat': ['excited', 'happy', 'energetic', 'fun', 'celebration', 'party', 'awesome', 'amazing'],
        'calm': ['peaceful', 'relaxed', 'serene', 'quiet', 'meditation', 'gentle', 'soft'],
        'dramatic': ['intense', 'powerful', 'emotional', 'serious', 'dramatic', 'tension'],
        'motivational': ['success', 'achieve', 'goal', 'motivation', 'inspire', 'dream', 'work', 'grind'],
        'energetic': ['fast', 'quick', 'rush', 'speed', 'action', 'move', 'go', 'run'],
        'relaxed': ['chill', 'easy', 'slow', 'comfortable', 'laid-back', 'casual']
    }
    
    THEME_KEYWORDS: Dict[str, List[str]] = {
        'fitness': ['workout', 'exercise', 'gym', 'fitness', 'muscle', 'training', 'health'],
        'cooking': ['recipe', 'cook', 'food', 'kitchen', 'ingredients', 'delicious', 'taste'],
        'travel': ['travel', 'trip', 'journey', 'adventure', 'explore', 'destination', 'vacation'],
        'tech': ['technology', 'app', 'software', 'digital', 'code', 'tech', 'innovation'],
        'lifestyle': ['daily', 'routine', 'life', 'lifestyle', 'personal', 'self-care'],
        'educational': ['learn', 'education', 'tutorial', 'how-to', 'explain', 'guide', 'tips']
    }


def get_config() -> tuple[ServerConfig, AudioConfig]:
    """Get configuration from environment variables or defaults."""
    server_config = ServerConfig(
        log_level=os.getenv("BGM_LOG_LEVEL", "INFO"),
        oauth_file=os.getenv("BGM_OAUTH_FILE", "oauth.json"),
    )
    
    audio_config = AudioConfig(
        max_duration_seconds=int(os.getenv("BGM_MAX_DURATION", "300")),
        search_limit_per_term=int(os.getenv("BGM_SEARCH_LIMIT", "10")),
        max_search_terms=int(os.getenv("BGM_MAX_SEARCH_TERMS", "5")),
        max_search_results=int(os.getenv("BGM_MAX_SEARCH_RESULTS", "20")),
        max_recommendations=int(os.getenv("BGM_MAX_RECOMMENDATIONS", "5")),
    )
    
    return server_config, audio_config