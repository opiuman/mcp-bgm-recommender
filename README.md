# Find BGM MCP Server

An MCP server that helps YouTube content creators find perfect background music for their shorts by analyzing script content and recommending tracks from YouTube Music.

## Features

- **Script Analysis**: Analyzes mood, theme, pacing, and sentiment from video scripts
- **Smart Recommendations**: Uses YouTube Music API to find suitable background tracks
- **Duration Filtering**: Ensures recommendations fit your short video length
- **Confidence Scoring**: Ranks recommendations by relevance to your content

## Architecture

The server follows clean architecture principles with modular design:

```text
find_bgm/
├── server.py              # Main server entry point
├── config.py              # Configuration management
├── models.py              # Data models and types
├── script_analyzer.py     # Script analysis logic
├── music_service.py       # YouTube Music API integration
├── tools.py               # MCP tool definitions
└── test_server.py         # Test suite
```

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. (Optional) Set up YouTube Music API access:
   - Follow the [ytmusicapi setup guide](https://ytmusicapi.readthedocs.io/en/stable/setup.html)
   - Create `oauth.json` file in the project directory
   - Without this, the server will use mock recommendations

## Usage

The server provides one main tool: `recommend_background_music`

### Parameters

- `script` (required): Your YouTube short script/content
- `duration` (required): Length of your short in seconds (15-60)
- `genre_preference` (optional): "pop", "electronic", "chill", "rock", "hip-hop", "classical", "ambient", "any"
- `mood_preference` (optional): "upbeat", "calm", "dramatic", "energetic", "relaxed", "motivational", "any"
- `content_type` (optional): "comedy", "educational", "lifestyle", "fitness", "cooking", "travel", "tech", "other"

### Example Response

```json
{
  "analysis": {
    "detected_mood": "motivational",
    "detected_theme": "fitness", 
    "pacing": "medium",
    "sentiment_score": 0.4,
    "keywords": ["workout", "energy", "strong"]
  },
  "recommendations": [
    {
      "title": "Uplifting Corporate Background",
      "artist": "Audio Library",
      "youtube_music_id": "abc123",
      "confidence_score": 0.85,
      "reason": "Strong match for motivational mood and fitness content",
      "duration": 45,
      "loop_suitable": true
    }
  ]
}
```

## Configuration

Customize behavior with environment variables:

```bash
# Logging level
export BGM_LOG_LEVEL=DEBUG

# OAuth file location
export BGM_OAUTH_FILE=my_oauth.json

# Search and recommendation limits
export BGM_MAX_DURATION=240
export BGM_SEARCH_LIMIT=15
```

## YouTube Music API Setup

### Method 1: Browser Authentication (Recommended)

1. Install ytmusicapi: `pip install ytmusicapi`
2. Run: `ytmusicapi browser`
3. Follow prompts to paste browser headers from YouTube Music
4. Save as `oauth.json`

### Method 2: OAuth Setup

1. Create Google Cloud project
2. Enable YouTube Data API v3
3. Create OAuth credentials
4. Run: `ytmusicapi oauth`
5. Complete authentication flow

Without the API, the server works with mock data for testing.

## Running the Server

```bash
python server.py
```

The server runs on stdio and can be integrated with any MCP-compatible client.

## Testing

```bash
# Test all components
python test_server.py

# Test with virtual environment
source venv/bin/activate
python test_server.py
```

## Claude Desktop Integration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "find-bgm": {
      "command": "/path/to/find_bgm/venv/bin/python",
      "args": ["/path/to/find_bgm/server.py"]
    }
  }
}
```

## Components

### ScriptAnalyzer

Analyzes script content to detect mood, theme, and pacing using natural language processing.

### YouTubeMusicService & MusicRecommendationService

Handles YouTube Music API integration and generates scored recommendations.

### BGMTools

MCP tool interface that orchestrates script analysis and music recommendations.

### Configuration Management

Environment-based configuration with sensible defaults and type safety.

## Example Usage

```python
from models import RecommendationRequest
from script_analyzer import ScriptAnalyzer
from music_service import MusicRecommendationService

# Analyze script
analyzer = ScriptAnalyzer()
analysis = analyzer.analyze_script("Your video script here")

# Get recommendations
service = MusicRecommendationService(music_service, config)
recommendations = await service.get_recommendations(
    analysis, "electronic", "upbeat", 30
)
```

The server provides intelligent music recommendations to help creators find the perfect soundtrack for their content! 🎵
