"""
MCP tool definitions and handlers.
"""
from typing import Dict, Any, List
import json
import logging

import mcp.types as types
from mcp.types import Tool

from config import ContentCategories
from models import RecommendationRequest, RecommendationResponse
from script_analyzer import ScriptAnalyzer
from music_service import MusicRecommendationService

logger = logging.getLogger(__name__)


class BGMTools:
    """Handler for Background Music recommendation tools."""
    
    def __init__(self, recommendation_service: MusicRecommendationService):
        self.recommendation_service = recommendation_service
        self.script_analyzer = ScriptAnalyzer()
    
    def get_tool_definitions(self) -> List[Tool]:
        """Return list of available tools."""
        return [
            Tool(
                name="recommend_background_music",
                description="Analyze YouTube short script and recommend background music from YouTube Music",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "script": {
                            "type": "string",
                            "description": "The YouTube short script/content text",
                            "minLength": 1
                        },
                        "duration": {
                            "type": "integer",
                            "description": "Duration of the short in seconds (15-60)",
                            "minimum": 15,
                            "maximum": 60
                        },
                        "genre_preference": {
                            "type": "string",
                            "description": "Optional genre preference",
                            "enum": ContentCategories.GENRES,
                            "default": "any"
                        },
                        "mood_preference": {
                            "type": "string", 
                            "description": "Optional mood preference",
                            "enum": ContentCategories.MOODS,
                            "default": "any"
                        },
                        "content_type": {
                            "type": "string",
                            "description": "Type of content being created",
                            "enum": ContentCategories.CONTENT_TYPES,
                            "default": "other"
                        }
                    },
                    "required": ["script", "duration"],
                    "additionalProperties": False
                }
            )
        ]
    
    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """
        Handle incoming tool calls.
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            List of text content responses
        """
        if name == "recommend_background_music":
            return await self._handle_music_recommendation(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    async def _handle_music_recommendation(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle music recommendation requests."""
        try:
            # Parse and validate request
            request = RecommendationRequest(
                script=arguments["script"],
                duration=arguments["duration"],
                genre_preference=arguments.get("genre_preference", "any"),
                mood_preference=arguments.get("mood_preference", "any"),
                content_type=arguments.get("content_type", "other")
            )
            request.validate()
            
            logger.info(f"Processing {request.content_type} content, duration: {request.duration}s")
            
            # Analyze script
            analysis = self.script_analyzer.analyze_script(request.script)
            logger.info(f"Analysis complete: {analysis.detected_mood} mood, {analysis.detected_theme} theme")
            
            # Get music recommendations
            recommendations = await self.recommendation_service.get_recommendations(
                analysis, request.genre_preference, request.mood_preference, request.duration
            )
            
            # Build response
            response = RecommendationResponse(
                analysis=analysis,
                recommendations=recommendations,
                input_parameters={
                    "script_length": len(request.script),
                    "duration": request.duration,
                    "genre_preference": request.genre_preference,
                    "mood_preference": request.mood_preference,
                    "content_type": request.content_type
                },
                search_info={
                    "search_terms_used": self.recommendation_service.generate_search_terms(
                        analysis, request.genre_preference, request.mood_preference
                    ),
                    "total_recommendations": len(recommendations),
                    "api_status": "active" if self.recommendation_service.music_service.client else "mock_mode"
                }
            )
            
            logger.info(f"Returning {len(recommendations)} recommendations")
            
            return [types.TextContent(
                type="text",
                text=json.dumps(response.to_dict(), indent=2, ensure_ascii=False)
            )]
            
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return [types.TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
        except Exception as e:
            logger.error(f"Unexpected error in music recommendation: {e}", exc_info=True)
            return [types.TextContent(
                type="text",
                text=f"An unexpected error occurred: {str(e)}"
            )]