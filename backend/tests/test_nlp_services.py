"""Tests for NLP services."""

import pytest
from app.services.nlp.text_processor import TextProcessor
from app.services.nlp.sentiment_analyzer import SentimentAnalyzer


class TestTextProcessor:
    """Tests for text processor."""

    def test_clean_text_basic(self):
        """Test basic text cleaning."""
        processor = TextProcessor()
        text = "  Это тестовый ТЕКСТ!  С лишними   пробелами.  "
        cleaned = processor.clean_text(text)

        assert "тестовый" in cleaned
        assert "текст" in cleaned
        assert cleaned.startswith("это")
        assert "  " not in cleaned

    def test_clean_text_remove_urls(self):
        """Test URL removal."""
        processor = TextProcessor()
        text = "Новость на сайте https://example.com/news очень интересная"
        cleaned = processor.clean_text(text)

        assert "https" not in cleaned
        assert "example.com" not in cleaned
        assert "новость" in cleaned

    def test_clean_text_remove_emails(self):
        """Test email removal."""
        processor = TextProcessor()
        text = "Контакт: test@example.com для вопросов"
        cleaned = processor.clean_text(text)

        assert "test@example.com" not in cleaned
        assert "контакт" in cleaned

    def test_tokenize_basic(self):
        """Test basic tokenization."""
        processor = TextProcessor()
        text = "Это простой тест для проверки токенизации"
        tokens = processor.tokenize(text, remove_stop_words=False)

        assert "это" in tokens
        assert "простой" in tokens
        assert "тест" in tokens

    def test_tokenize_remove_stop_words(self):
        """Test tokenization with stop word removal."""
        processor = TextProcessor()
        text = "Это простой тест для проверки токенизации"
        tokens = processor.tokenize(text, remove_stop_words=True)

        # Stop words should be removed
        assert "это" not in tokens
        assert "для" not in tokens
        # Content words should remain
        assert "простой" in tokens
        assert "тест" in tokens

    def test_extract_sentences(self):
        """Test sentence extraction."""
        processor = TextProcessor()
        text = "Первое предложение. Второе предложение! Третье предложение?"
        sentences = processor.extract_sentences(text)

        assert len(sentences) == 3
        assert "Первое предложение" in sentences[0]
        assert "Второе предложение" in sentences[1]

    def test_extract_key_phrases(self):
        """Test key phrase extraction."""
        processor = TextProcessor()
        text = "рынок рынок анализ рынок исследование анализ данные"
        key_phrases = processor.extract_key_phrases(text, top_n=3)

        assert len(key_phrases) <= 3
        assert key_phrases[0][0] == "рынок"  # Most frequent
        assert key_phrases[0][1] == 3  # Frequency

    def test_calculate_text_statistics(self):
        """Test text statistics calculation."""
        processor = TextProcessor()
        text = "Это короткий текст. Он имеет две фразы."
        stats = processor.calculate_text_statistics(text)

        assert stats["word_count"] > 0
        assert stats["sentence_count"] == 2
        assert stats["char_count"] == len(text)
        assert stats["unique_words"] > 0
        assert 0 <= stats["lexical_diversity"] <= 1

    def test_extract_ngrams(self):
        """Test n-gram extraction."""
        processor = TextProcessor()
        text = "маркетинговое исследование рынка маркетинговое исследование продукта"
        bigrams = processor.extract_ngrams(text, n=2, top_k=5)

        assert len(bigrams) > 0
        # "маркетинговое исследование" should appear twice
        assert any("маркетинговое исследование" in ngram[0] for ngram in bigrams)

    def test_extract_named_entities(self):
        """Test named entity extraction."""
        processor = TextProcessor()
        text = "Компания ООО Рога и Копыта работает в Москве"
        entities = processor.extract_named_entities(text)

        assert "ORGANIZATION" in entities
        assert "LOCATION" in entities
        # Should find "ООО Рога и Копыта" as organization
        assert any("ООО" in org for org in entities["ORGANIZATION"])


class TestSentimentAnalyzer:
    """Tests for sentiment analyzer."""

    def test_positive_sentiment(self):
        """Test positive sentiment detection."""
        analyzer = SentimentAnalyzer()
        text = "Отличный продукт с великолепным качеством и высокой эффективностью"
        result = analyzer.analyze_sentiment(text)

        assert result["sentiment"] == "positive"
        assert result["score"] > 0
        assert result["positive_words_count"] > 0

    def test_negative_sentiment(self):
        """Test negative sentiment detection."""
        analyzer = SentimentAnalyzer()
        text = "Плохой продукт с ужасным качеством и множеством проблем"
        result = analyzer.analyze_sentiment(text)

        assert result["sentiment"] == "negative"
        assert result["score"] < 0
        assert result["negative_words_count"] > 0

    def test_neutral_sentiment(self):
        """Test neutral sentiment detection."""
        analyzer = SentimentAnalyzer()
        text = "Продукт имеет определенные характеристики и функции"
        result = analyzer.analyze_sentiment(text)

        assert result["sentiment"] == "neutral"
        assert abs(result["score"]) < 0.3

    def test_sentiment_score_range(self):
        """Test sentiment score is in valid range."""
        analyzer = SentimentAnalyzer()
        text = "Хороший продукт"
        result = analyzer.analyze_sentiment(text)

        assert -1.0 <= result["score"] <= 1.0
        assert 0.0 <= result["confidence"] <= 1.0

    def test_aspect_sentiment_mentioned(self):
        """Test aspect-based sentiment when aspect is mentioned."""
        analyzer = SentimentAnalyzer()
        text = "Качество продукта отличное. Цена высокая но оправданная."
        aspects = ["качество", "цена"]
        result = analyzer.analyze_aspect_sentiment(text, aspects)

        assert "качество" in result
        assert "цена" in result
        assert result["качество"]["sentiment"] == "positive"

    def test_aspect_sentiment_not_mentioned(self):
        """Test aspect-based sentiment when aspect is not mentioned."""
        analyzer = SentimentAnalyzer()
        text = "Продукт имеет хорошее качество"
        aspects = ["качество", "доставка"]
        result = analyzer.analyze_aspect_sentiment(text, aspects)

        assert "качество" in result
        assert "доставка" in result
        assert result["доставка"]["sentiment"] == "not_mentioned"
        assert result["доставка"]["score"] == 0.0

    def test_mixed_sentiment(self):
        """Test mixed sentiment detection."""
        analyzer = SentimentAnalyzer()
        text = "Хороший продукт но есть проблемы с качеством"
        result = analyzer.analyze_sentiment(text)

        # Should have both positive and negative words
        assert result["positive_words_count"] > 0
        assert result["negative_words_count"] > 0

    def test_empty_text_sentiment(self):
        """Test sentiment analysis on empty text."""
        analyzer = SentimentAnalyzer()
        text = ""
        result = analyzer.analyze_sentiment(text)

        assert result["sentiment"] == "neutral"
        assert result["score"] == 0.0
        assert result["positive_words_count"] == 0
        assert result["negative_words_count"] == 0
