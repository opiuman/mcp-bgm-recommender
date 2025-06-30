"""
Script analysis functionality for detecting mood, theme, and characteristics.
"""
from typing import Dict, List
from textblob import TextBlob
import logging

from config import ContentCategories
from models import ScriptAnalysis

logger = logging.getLogger(__name__)


class ScriptAnalyzer:
    """Analyzes YouTube short scripts to extract mood, theme, and characteristics."""
    
    def __init__(self):
        self.mood_keywords = ContentCategories.MOOD_KEYWORDS
        self.theme_keywords = ContentCategories.THEME_KEYWORDS
    
    def analyze_script(self, script: str) -> ScriptAnalysis:
        """
        Analyze script text and return comprehensive analysis.
        
        Args:
            script: The video script text to analyze
            
        Returns:
            ScriptAnalysis object with detected characteristics
        """
        if not script or not script.strip():
            raise ValueError("Script cannot be empty")
        
        script_lower = script.lower()
        
        # Perform sentiment analysis
        sentiment = self._analyze_sentiment(script)
        
        # Detect mood and theme based on keywords
        detected_moods = self._detect_moods(script_lower)
        detected_themes = self._detect_themes(script_lower)
        
        # Analyze pacing
        pacing = self._analyze_pacing(script)
        
        # Extract keywords
        keywords = self._extract_keywords(script)
        
        # Determine primary mood and theme
        primary_mood = self._determine_primary_mood(detected_moods, sentiment.polarity)
        primary_theme = detected_themes[0] if detected_themes else "general"
        
        logger.info(f"Script analysis: mood={primary_mood}, theme={primary_theme}, pacing={pacing}")
        
        return ScriptAnalysis(
            detected_mood=primary_mood,
            detected_theme=primary_theme,
            pacing=pacing,
            sentiment_score=sentiment.polarity,
            keywords=keywords[:10],  # Top 10 keywords
            all_detected_moods=detected_moods,
            all_detected_themes=detected_themes
        )
    
    def _analyze_sentiment(self, script: str) -> any:
        """Analyze sentiment using TextBlob."""
        try:
            blob = TextBlob(script)
            return blob.sentiment
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
            # Return neutral sentiment as fallback
            from collections import namedtuple
            Sentiment = namedtuple('Sentiment', ['polarity', 'subjectivity'])
            return Sentiment(0.0, 0.0)
    
    def _detect_moods(self, script_lower: str) -> List[str]:
        """Detect moods based on keyword matching."""
        detected_moods = []
        for mood, keywords in self.mood_keywords.items():
            if any(keyword in script_lower for keyword in keywords):
                detected_moods.append(mood)
        return detected_moods
    
    def _detect_themes(self, script_lower: str) -> List[str]:
        """Detect themes based on keyword matching."""
        detected_themes = []
        for theme, keywords in self.theme_keywords.items():
            if any(keyword in script_lower for keyword in keywords):
                detected_themes.append(theme)
        return detected_themes
    
    def _analyze_pacing(self, script: str) -> str:
        """
        Determine pacing based on sentence structure and punctuation.
        
        Args:
            script: The script text
            
        Returns:
            Pacing classification: "fast", "medium", or "slow"
        """
        exclamation_count = script.count('!')
        sentence_count = len([s for s in script.split('.') if s.strip()])
        word_count = len(script.split())
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Fast pacing indicators
        if exclamation_count > 2 or avg_sentence_length < 8:
            return "fast"
        # Slow pacing indicators
        elif avg_sentence_length > 15:
            return "slow"
        else:
            return "medium"
    
    def _extract_keywords(self, script: str) -> List[str]:
        """
        Extract meaningful keywords from the script.
        
        Args:
            script: The script text
            
        Returns:
            List of extracted keywords
        """
        try:
            blob = TextBlob(script)
            keywords = []
            
            # Extract nouns and adjectives longer than 3 characters
            for word, pos in blob.tags:
                if (pos in ['NN', 'NNS', 'JJ', 'JJR', 'JJS'] and 
                    len(word) > 3 and word.isalpha()):
                    keywords.append(word.lower())
            
            # Remove duplicates while preserving order
            return list(dict.fromkeys(keywords))
            
        except Exception as e:
            logger.warning(f"Keyword extraction failed: {e}")
            # Fallback: simple word extraction
            words = script.lower().split()
            return [word for word in words if len(word) > 3 and word.isalpha()][:10]
    
    def _determine_primary_mood(self, detected_moods: List[str], sentiment_polarity: float) -> str:
        """
        Determine the primary mood from detected moods and sentiment.
        
        Args:
            detected_moods: List of detected moods from keywords
            sentiment_polarity: Sentiment polarity score
            
        Returns:
            Primary mood string
        """
        # Use keyword-detected mood if available
        if detected_moods:
            return detected_moods[0]
        
        # Fall back to sentiment-based mood
        if sentiment_polarity < -0.1:
            return "dramatic"
        elif sentiment_polarity > 0.3:
            return "upbeat"
        elif sentiment_polarity > 0.1:
            return "motivational"
        else:
            return "calm"