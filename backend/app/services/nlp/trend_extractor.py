"""Trend extraction service."""

from typing import List, Dict
from collections import defaultdict
from datetime import datetime
from app.services.nlp.text_processor import TextProcessor


class TrendExtractor:
    """Extract and analyze trends from text data."""

    def __init__(self):
        """Initialize trend extractor."""
        self.text_processor = TextProcessor()

    def extract_trending_topics(
        self,
        texts: List[Dict[str, any]],
        min_frequency: int = 3,
        top_n: int = 20,
    ) -> List[Dict[str, any]]:
        """
        Extract trending topics from multiple texts.

        Args:
            texts: List of text dictionaries with 'content' and 'date' fields
            min_frequency: Minimum frequency threshold
            top_n: Number of top trends to return

        Returns:
            List of trend dictionaries
        """
        # Collect all key phrases with timestamps
        phrase_occurrences = defaultdict(list)

        for text_data in texts:
            content = text_data.get("content", "")
            date = text_data.get("date", datetime.utcnow())

            # Extract key phrases
            phrases = self.text_processor.extract_key_phrases(content, top_n=50)

            for phrase, freq in phrases:
                phrase_occurrences[phrase].extend([date] * freq)

        # Filter by minimum frequency
        trending_topics = []
        for phrase, dates in phrase_occurrences.items():
            if len(dates) >= min_frequency:
                trending_topics.append({
                    "topic": phrase,
                    "frequency": len(dates),
                    "first_seen": min(dates),
                    "last_seen": max(dates),
                    "growth_rate": self._calculate_growth_rate(dates),
                })

        # Sort by frequency and growth rate
        trending_topics.sort(key=lambda x: (x["frequency"], x["growth_rate"]), reverse=True)

        return trending_topics[:top_n]

    def _calculate_growth_rate(self, dates: List[datetime]) -> float:
        """
        Calculate growth rate of mentions over time.

        Args:
            dates: List of mention timestamps

        Returns:
            Growth rate score
        """
        if len(dates) < 2:
            return 0.0

        # Sort dates
        sorted_dates = sorted(dates)

        # Split into two halves
        mid = len(sorted_dates) // 2
        first_half_count = mid
        second_half_count = len(sorted_dates) - mid

        # Calculate growth rate
        if first_half_count == 0:
            return 1.0

        return (second_half_count - first_half_count) / first_half_count

    def identify_emerging_trends(
        self,
        current_texts: List[Dict[str, any]],
        historical_texts: List[Dict[str, any]],
    ) -> List[Dict[str, any]]:
        """
        Identify emerging trends by comparing current and historical data.

        Args:
            current_texts: Recent texts
            historical_texts: Historical texts for comparison

        Returns:
            List of emerging trend dictionaries
        """
        current_topics = self.extract_trending_topics(current_texts, min_frequency=2)
        historical_topics = self.extract_trending_topics(historical_texts, min_frequency=2)

        # Create lookup for historical topics
        historical_lookup = {topic["topic"]: topic["frequency"] for topic in historical_topics}

        emerging_trends = []
        for topic in current_topics:
            topic_text = topic["topic"]
            current_freq = topic["frequency"]
            historical_freq = historical_lookup.get(topic_text, 0)

            # Calculate emergence score
            if historical_freq == 0:
                emergence_score = 1.0  # Completely new
            else:
                emergence_score = (current_freq - historical_freq) / historical_freq

            if emergence_score > 0.3:  # Significant increase
                emerging_trends.append({
                    "topic": topic_text,
                    "current_frequency": current_freq,
                    "historical_frequency": historical_freq,
                    "emergence_score": emergence_score,
                    "status": "new" if historical_freq == 0 else "growing",
                })

        emerging_trends.sort(key=lambda x: x["emergence_score"], reverse=True)

        return emerging_trends
