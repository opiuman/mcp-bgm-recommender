#!/usr/bin/env python3
"""
Find BGM MCP Server

A Model Context Protocol server that helps YouTube content creators find perfect 
background music for their shorts by analyzing script content and recommending 
tracks from YouTube Music.
"""
import asyncio
import logging
import os
import sys
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.lowlevel import NotificationOptions
import mcp.types as types

from config import get_config, ServerConfig, AudioConfig
from music_service import YouTubeMusicService, MusicRecommendationService
from tools import BGMTools


class FindBGMServer:
    """Main server class for the Find BGM MCP server."""
    
    def __init__(self, server_config: ServerConfig, audio_config: AudioConfig):
        self.server_config = server_config
        self.audio_config = audio_config
        self.server = Server(server_config.name)
        self.logger = self._setup_logging()
        
        # Initialize services
        self.youtube_music_client = self._initialize_youtube_music()
        self.music_service = YouTubeMusicService(self.youtube_music_client, audio_config)
        self.recommendation_service = MusicRecommendationService(self.music_service, audio_config)
        self.tools = BGMTools(self.recommendation_service)
        
        # Register handlers
        self._register_handlers()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.server_config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(self.server_config.name)
    
    def _initialize_youtube_music(self):
        """Initialize YouTube Music API client if credentials are available."""
        try:
            from ytmusicapi import YTMusic
            
            oauth_path = os.path.join(os.path.dirname(__file__), self.server_config.oauth_file)
            
            if os.path.exists(oauth_path):
                client = YTMusic(oauth_path)
                self.logger.info("YouTube Music API initialized successfully")
                return client
            else:
                self.logger.warning(f"{self.server_config.oauth_file} not found. Using mock recommendations.")
                return None
                
        except ImportError:
            self.logger.warning("ytmusicapi not installed. Using mock recommendations.")
            return None
        except Exception as e:
            self.logger.error(f"Failed to initialize YouTube Music API: {e}")
            return None
    
    def _register_handlers(self):
        """Register MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools."""
            return self.tools.get_tool_definitions()
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls."""
            return await self.tools.handle_tool_call(name, arguments)
    
    async def run(self):
        """Run the MCP server."""
        self.logger.info(f"Starting {self.server_config.name} v{self.server_config.version}")
        
        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name=self.server_config.name,
                        server_version=self.server_config.version,
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    ),
                )
        except Exception as e:
            self.logger.error(f"Server error: {e}", exc_info=True)
            raise


async def main():
    """Main entry point for the server."""
    try:
        # Load configuration
        server_config, audio_config = get_config()
        
        # Create and run server
        server = FindBGMServer(server_config, audio_config)
        await server.run()
        
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())