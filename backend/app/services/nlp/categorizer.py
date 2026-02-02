"""Text categorization service."""

from typing import List, Dict
from app.services.nlp.text_processor import TextProcessor


class Categorizer:
    """
    Text categorizer for industry and topic classification.

    Note: This is a keyword-based implementation.
    In production, use ML models like:
    - BERT for Russian (ruBERT)
    - FastText classifiers
    - scikit-learn with TF-IDF
    """

    def __init__(self):
        """Initialize categorizer."""
        self.text_processor = TextProcessor()
        self.industry_keywords = self._load_industry_keywords()
        self.topic_keywords = self._load_topic_keywords()

    def _load_industry_keywords(self) -> Dict[str, List[str]]:
        """Load industry-specific keywords."""
        return {
            "IT и технологии": [
                "программирование", "разработка", "софт", "приложение", "технология",
                "интернет", "цифровой", "данные", "облако", "искусственный интеллект",
            ],
            "Розничная торговля": [
                "магазин", "продажа", "товар", "покупатель", "ритейл", "торговля",
                "ассортимент", "скидка", "акция", "клиент",
            ],
            "Общественное питание": [
                "ресторан", "кафе", "еда", "питание", "меню", "блюдо", "кухня",
                "доставка", "повар", "обслуживание",
            ],
            "Финансы и банки": [
                "банк", "кредит", "финансы", "инвестиции", "ставка", "депозит",
                "платеж", "валюта", "биржа", "капитал",
            ],
            "Образование": [
                "образование", "обучение", "школа", "университет", "курс", "студент",
                "преподаватель", "учеба", "знания", "навыки",
            ],
            "Здравоохранение": [
                "медицина", "здоровье", "лечение", "больница", "клиника", "врач",
                "пациент", "диагностика", "терапия", "здравоохранение",
            ],
            "Строительство и недвижимость": [
                "строительство", "недвижимость", "жилье", "квартира", "дом", "ремонт",
                "проект", "застройщик", "объект", "площадь",
            ],
            "Транспорт и логистика": [
                "транспорт", "логистика", "доставка", "перевозка", "склад", "маршрут",
                "грузоперевозки", "автомобиль", "поставка", "экспедирование",
            ],
            "Производство": [
                "производство", "завод", "фабрика", "продукция", "изготовление",
                "промышленность", "выпуск", "оборудование", "технологический процесс",
            ],
            "Сельское хозяйство": [
                "сельское хозяйство", "агро", "фермер", "урожай", "посев", "земля",
                "растениеводство", "животноводство", "агропромышленный",
            ],
        }

    def _load_topic_keywords(self) -> Dict[str, List[str]]:
        """Load topic-specific keywords."""
        return {
            "Инновации": [
                "инновация", "новинка", "разработка", "внедрение", "современный",
                "прорыв", "передовой", "технология", "революция",
            ],
            "Финансовые показатели": [
                "прибыль", "доход", "выручка", "убыток", "рентабельность", "оборот",
                "показатель", "рост", "снижение", "процент",
            ],
            "Конкуренция": [
                "конкурент", "конкуренция", "рынок", "доля", "позиция", "лидер",
                "соперничество", "борьба", "преимущество",
            ],
            "Регулирование": [
                "закон", "регулирование", "норматив", "требование", "стандарт",
                "правило", "ограничение", "законодательство", "политика",
            ],
            "Инвестиции": [
                "инвестиция", "вложение", "капитал", "финансирование", "проект",
                "развитие", "расширение", "модернизация", "фонд",
            ],
            "Кадры": [
                "персонал", "сотрудник", "кадры", "работник", "команда", "найм",
                "зарплата", "мотивация", "обучение", "руководитель",
            ],
            "Маркетинг": [
                "маркетинг", "реклама", "продвижение", "бренд", "аудитория",
                "кампания", "позиционирование", "сегмент", "каналы",
            ],
        }

    def categorize_by_industry(self, text: str, top_n: int = 3) -> List[Dict[str, any]]:
        """
        Categorize text by industry.

        Args:
            text: Input text
            top_n: Number of top industries to return

        Returns:
            List of industry matches with scores
        """
        text_lower = text.lower()
        industry_scores = {}

        for industry, keywords in self.industry_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                industry_scores[industry] = score

        # Sort by score and return top N
        sorted_industries = sorted(
            industry_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        return [
            {
                "industry": industry,
                "score": score,
                "confidence": score / max(industry_scores.values()) if industry_scores else 0,
            }
            for industry, score in sorted_industries[:top_n]
        ]

    def categorize_by_topic(self, text: str, top_n: int = 5) -> List[Dict[str, any]]:
        """
        Categorize text by topic.

        Args:
            text: Input text
            top_n: Number of top topics to return

        Returns:
            List of topic matches with scores
        """
        text_lower = text.lower()
        topic_scores = {}

        for topic, keywords in self.topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                topic_scores[topic] = score

        # Sort by score and return top N
        sorted_topics = sorted(
            topic_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        return [
            {
                "topic": topic,
                "score": score,
                "confidence": score / max(topic_scores.values()) if topic_scores else 0,
            }
            for topic, score in sorted_topics[:top_n]
        ]

    def classify_document(self, text: str) -> Dict[str, any]:
        """
        Classify document with both industry and topic categories.

        Args:
            text: Input text

        Returns:
            Dictionary with classification results
        """
        industries = self.categorize_by_industry(text, top_n=3)
        topics = self.categorize_by_topic(text, top_n=5)

        # Calculate text statistics
        stats = self.text_processor.calculate_text_statistics(text)

        return {
            "industries": industries,
            "topics": topics,
            "primary_industry": industries[0]["industry"] if industries else None,
            "primary_topic": topics[0]["topic"] if topics else None,
            "statistics": stats,
        }
