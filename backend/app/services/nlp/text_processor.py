"""Text processing service for Russian language."""

from typing import List, Dict, Tuple
import re
from collections import Counter


class TextProcessor:
    """
    Text processor for Russian language.

    Note: This is a basic implementation. In production, this would use:
    - spaCy with Russian model (ru_core_news_sm/md/lg)
    - pymorphy3 for morphological analysis
    - razdel for tokenization
    - natasha for NER
    """

    def __init__(self):
        """Initialize text processor."""
        self.stop_words = self._load_russian_stop_words()

    def _load_russian_stop_words(self) -> set:
        """Load Russian stop words."""
        # Basic set of Russian stop words
        return {
            "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а", "то",
            "все", "она", "так", "его", "но", "да", "ты", "к", "у", "же", "вы", "за",
            "бы", "по", "только", "ее", "мне", "было", "вот", "от", "меня", "еще", "нет",
            "о", "из", "ему", "теперь", "когда", "даже", "ну", "вдруг", "ли", "если",
            "уже", "или", "ни", "быть", "был", "него", "до", "вас", "нибудь", "опять",
            "уж", "вам", "ведь", "там", "потом", "себя", "ничего", "ей", "может", "они",
            "тут", "где", "есть", "надо", "ней", "для", "мы", "тебя", "их", "чем", "была",
            "сам", "чтоб", "без", "будто", "чего", "раз", "тоже", "себе", "под", "будет",
            "ж", "тогда", "кто", "этот", "того", "потому", "этого", "какой", "совсем",
            "ним", "здесь", "этом", "один", "почти", "мой", "тем", "чтобы", "нее", "сейчас",
            "были", "куда", "зачем", "всех", "никогда", "можно", "при", "наконец", "два",
            "об", "другой", "хоть", "после", "над", "больше", "тот", "через", "эти", "нас",
            "про", "всего", "них", "какая", "много", "разве", "три", "эту", "моя", "впрочем",
            "хорошо", "свою", "этой", "перед", "иногда", "лучше", "чуть", "том", "нельзя",
            "такой", "им", "более", "всегда", "конечно", "всю", "между",
        }

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Input text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove URLs
        text = re.sub(r"https?://\S+|www\.\S+", "", text)

        # Remove email addresses
        text = re.sub(r"\S+@\S+", "", text)

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove special characters but keep Russian letters, numbers, and basic punctuation
        text = re.sub(r"[^а-яёА-ЯЁa-zA-Z0-9\s.,!?;:\-]", "", text)

        return text.strip()

    def tokenize(self, text: str, remove_stop_words: bool = True) -> List[str]:
        """
        Tokenize text into words.

        Args:
            text: Input text
            remove_stop_words: Whether to remove stop words

        Returns:
            List of tokens
        """
        # Clean text
        text = self.clean_text(text)

        # Simple word tokenization
        words = re.findall(r"\b[а-яёА-ЯЁa-zA-Z]+\b", text)

        # Remove stop words if requested
        if remove_stop_words:
            words = [w for w in words if w.lower() not in self.stop_words]

        return words

    def extract_key_phrases(self, text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Extract key phrases from text based on frequency.

        Args:
            text: Input text
            top_n: Number of top phrases to return

        Returns:
            List of (phrase, frequency) tuples
        """
        tokens = self.tokenize(text, remove_stop_words=True)

        # Count word frequencies
        word_freq = Counter(tokens)

        # Get top N words
        top_words = word_freq.most_common(top_n)

        return top_words

    def extract_named_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text.

        This is a placeholder implementation. In production, use:
        - natasha library for Russian NER
        - spaCy with Russian model

        Args:
            text: Input text

        Returns:
            Dictionary with entity types and lists of entities
        """
        # Placeholder: Extract capitalized words as potential entities
        tokens = text.split()

        # Find sequences of capitalized words
        entities = {
            "PERSON": [],
            "ORGANIZATION": [],
            "LOCATION": [],
            "OTHER": [],
        }

        capitalized_sequences = []
        current_sequence = []

        for token in tokens:
            # Remove punctuation for checking
            clean_token = re.sub(r"[^\w\s]", "", token)

            if clean_token and clean_token[0].isupper() and len(clean_token) > 1:
                current_sequence.append(clean_token)
            else:
                if current_sequence:
                    capitalized_sequences.append(" ".join(current_sequence))
                    current_sequence = []

        if current_sequence:
            capitalized_sequences.append(" ".join(current_sequence))

        # Categorize entities (very basic heuristics)
        for entity in capitalized_sequences:
            words = entity.split()
            # This is just a placeholder - in production use proper NER
            if any(word in ["ООО", "АО", "ЗАО", "ОАО", "ИП"] for word in words):
                entities["ORGANIZATION"].append(entity)
            else:
                entities["OTHER"].append(entity)

        return entities

    def extract_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: Input text

        Returns:
            List of sentences
        """
        # Simple sentence splitting for Russian
        sentences = re.split(r"[.!?]+\s+", text)
        return [s.strip() for s in sentences if s.strip()]

    def calculate_text_statistics(self, text: str) -> Dict[str, any]:
        """
        Calculate various text statistics.

        Args:
            text: Input text

        Returns:
            Dictionary with statistics
        """
        sentences = self.extract_sentences(text)
        tokens = self.tokenize(text, remove_stop_words=False)
        tokens_no_stop = self.tokenize(text, remove_stop_words=True)

        return {
            "char_count": len(text),
            "word_count": len(tokens),
            "sentence_count": len(sentences),
            "unique_words": len(set(tokens_no_stop)),
            "avg_word_length": sum(len(w) for w in tokens) / len(tokens) if tokens else 0,
            "avg_sentence_length": len(tokens) / len(sentences) if sentences else 0,
            "lexical_diversity": len(set(tokens_no_stop)) / len(tokens_no_stop) if tokens_no_stop else 0,
        }

    def extract_ngrams(self, text: str, n: int = 2, top_k: int = 10) -> List[Tuple[str, int]]:
        """
        Extract n-grams from text.

        Args:
            text: Input text
            n: N-gram size
            top_k: Number of top n-grams to return

        Returns:
            List of (ngram, frequency) tuples
        """
        tokens = self.tokenize(text, remove_stop_words=True)

        # Generate n-grams
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngram = " ".join(tokens[i : i + n])
            ngrams.append(ngram)

        # Count frequencies
        ngram_freq = Counter(ngrams)

        return ngram_freq.most_common(top_k)
