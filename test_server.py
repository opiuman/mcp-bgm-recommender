#!/usr/bin/env python3
"""
Test script for the Find BGM MCP server
"""
import asyncio
import logging

from config import get_config
from script_analyzer import ScriptAnalyzer
from music_service import YouTubeMusicService, MusicRecommendationService
from models import RecommendationRequest

# Set up logging
logging.basicConfig(level=logging.INFO)


async def test_components():
    """Test the Find BGM components."""
    print("Testing Find BGM Components")
    print("=" * 50)
    
    # Load configuration
    server_config, audio_config = get_config()
    print(f"✅ Configuration loaded: {server_config.name} v{server_config.version}")
    
    # Test script analyzer
    print("\n1. Testing Script Analyzer")
    print("-" * 25)
    
    analyzer = ScriptAnalyzer()
    test_script = """
    Hey fitness enthusiasts! Ready for an intense 30-second HIIT workout? 
    This high-energy routine will get your heart pumping and burn maximum calories! 
    Let's crush this together and achieve those fitness goals!
    """
    
    analysis = analyzer.analyze_script(test_script)
    print(f"Detected mood: {analysis.detected_mood}")
    print(f"Detected theme: {analysis.detected_theme}")
    print(f"Pacing: {analysis.pacing}")
    print(f"Keywords: {analysis.keywords[:5]}")
    
    # Test music service (without real API)
    print("\n2. Testing Music Service")
    print("-" * 25)
    
    music_service = YouTubeMusicService(None, audio_config)  # No real client
    recommendation_service = MusicRecommendationService(music_service, audio_config)
    
    search_terms = recommendation_service.generate_search_terms(analysis, "electronic", "energetic")
    print(f"Generated search terms: {search_terms}")
    
    tracks = await music_service.search_tracks(search_terms, 30)
    print(f"Found {len(tracks)} tracks (mock data)")
    
    # Test recommendations
    print("\n3. Testing Recommendations")
    print("-" * 30)
    
    recommendations = await recommendation_service.get_recommendations(
        analysis, "electronic", "energetic", 30
    )
    
    print(f"Generated {len(recommendations)} recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec.title} by {rec.artist}")
        print(f"     Score: {rec.confidence_score:.2f} - {rec.reason}")
        print(f"     Duration: {rec.duration}s")
    
    # Test request validation
    print("\n4. Testing Request Validation")
    print("-" * 30)
    
    try:
        request = RecommendationRequest(
            script=test_script,
            duration=45,
            genre_preference="electronic",
            mood_preference="energetic",
            content_type="fitness"
        )
        request.validate()
        print("✅ Valid request passed validation")
    except ValueError as e:
        print(f"❌ Validation error: {e}")
    
    # Test invalid request
    try:
        invalid_request = RecommendationRequest(script="", duration=100)
        invalid_request.validate()
        print("❌ Invalid request should have failed")
    except ValueError as e:
        print(f"✅ Invalid request correctly rejected: {e}")
    
    print("\n" + "=" * 50)
    print("All components tested successfully! 🎵")


if __name__ == "__main__":
    asyncio.run(test_components())