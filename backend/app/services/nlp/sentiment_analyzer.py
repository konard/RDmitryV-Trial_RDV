"""Sentiment analysis service for Russian text."""

from typing import Dict, List
from app.services.nlp.text_processor import TextProcessor


class SentimentAnalyzer:
    """
    Sentiment analyzer for Russian language.

    Note: This is a basic lexicon-based implementation.
    In production, use pre-trained models like:
    - RuSentiment
    - Dostoevsky
    - Transformers with Russian sentiment models
    """

    def __init__(self):
        """Initialize sentiment analyzer."""
        self.text_processor = TextProcessor()
        self.positive_words = self._load_positive_words()
        self.negative_words = self._load_negative_words()

    def _load_positive_words(self) -> set:
        """Load positive sentiment words."""
        return {
            "хороший", "отличный", "прекрасный", "замечательный", "великолепный",
            "успех", "рост", "развитие", "прибыль", "увеличение", "эффективность",
            "качество", "лидер", "победа", "достижение", "улучшение", "инновация",
            "выгода", "польза", "преимущество", "перспектива", "возможность",
            "надежный", "стабильный", "сильный", "передовой", "современный",
        }

    def _load_negative_words(self) -> set:
        """Load negative sentiment words."""
        return {
            "плохой", "ужасный", "отвратительный", "неудача", "провал",
            "падение", "кризис", "убыток", "снижение", "проблема", "риск",
            "угроза", "спад", "сокращение", "банкротство", "дефицит", "потеря",
            "слабый", "неэффективный", "устаревший", "опасный", "вредный",
            "недостаток", "нехватка", "трудность", "препятствие",
        }

    def analyze_sentiment(self, text: str) -> Dict[str, any]:
        """
        Analyze sentiment of text.

        Args:
            text: Input text

        Returns:
            Dictionary with sentiment analysis results
        """
        tokens = self.text_processor.tokenize(text, remove_stop_words=False)
        tokens_lower = [t.lower() for t in tokens]

        positive_count = sum(1 for token in tokens_lower if token in self.positive_words)
        negative_count = sum(1 for token in tokens_lower if token in self.negative_words)

        # Calculate sentiment score (-1 to 1)
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            sentiment_score = 0.0
            sentiment_label = "neutral"
        else:
            sentiment_score = (positive_count - negative_count) / total_sentiment_words

            if sentiment_score > 0.2:
                sentiment_label = "positive"
            elif sentiment_score < -0.2:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"

        return {
            "sentiment": sentiment_label,
            "score": sentiment_score,
            "positive_words_count": positive_count,
            "negative_words_count": negative_count,
            "confidence": abs(sentiment_score),
        }

    def analyze_aspect_sentiment(self, text: str, aspects: List[str]) -> Dict[str, Dict[str, any]]:
        """
        Analyze sentiment for specific aspects mentioned in text.

        Args:
            text: Input text
            aspects: List of aspects to analyze

        Returns:
            Dictionary with aspect-level sentiment
        """
        sentences = self.text_processor.extract_sentences(text)
        aspect_sentiments = {}

        for aspect in aspects:
            aspect_lower = aspect.lower()
            relevant_sentences = [s for s in sentences if aspect_lower in s.lower()]

            if relevant_sentences:
                combined_text = " ".join(relevant_sentences)
                sentiment = self.analyze_sentiment(combined_text)
                aspect_sentiments[aspect] = sentiment
            else:
                aspect_sentiments[aspect] = {
                    "sentiment": "not_mentioned",
                    "score": 0.0,
                    "positive_words_count": 0,
                    "negative_words_count": 0,
                    "confidence": 0.0,
                }

        return aspect_sentiments
