"""Trend analysis service."""

from typing import List, Dict
from datetime import datetime
from collections import defaultdict

from app.services.nlp.trend_extractor import TrendExtractor
from app.services.nlp.sentiment_analyzer import SentimentAnalyzer
from app.models.trend import TrendSignificance, TrendDirection


class TrendAnalyzer:
    """Service for analyzing market trends."""

    def __init__(self):
        """Initialize trend analyzer."""
        self.trend_extractor = TrendExtractor()
        self.sentiment_analyzer = SentimentAnalyzer()

    async def analyze_industry_trends(
        self,
        industry: str,
        collected_data: List[Dict[str, any]],
    ) -> Dict[str, any]:
        """
        Analyze trends for a specific industry.

        Args:
            industry: Industry name
            collected_data: List of collected data dictionaries

        Returns:
            Dictionary with trend analysis results
        """
        # Extract trending topics
        texts = [
            {
                "content": data.get("content", ""),
                "date": data.get("date", datetime.utcnow()),
            }
            for data in collected_data
        ]

        trending_topics = self.trend_extractor.extract_trending_topics(texts, min_frequency=2, top_n=20)

        # Categorize trends by significance
        high_significance = []
        medium_significance = []
        low_significance = []

        for topic in trending_topics:
            significance = self._calculate_significance(topic)
            topic["significance"] = significance

            if significance == TrendSignificance.HIGH:
                high_significance.append(topic)
            elif significance == TrendSignificance.MEDIUM:
                medium_significance.append(topic)
            else:
                low_significance.append(topic)

        return {
            "industry": industry,
            "analysis_date": datetime.utcnow().isoformat(),
            "total_trends": len(trending_topics),
            "high_significance_trends": high_significance,
            "medium_significance_trends": medium_significance,
            "low_significance_trends": low_significance,
            "summary": self._generate_trend_summary(trending_topics),
        }

    def _calculate_significance(self, topic: Dict[str, any]) -> TrendSignificance:
        """
        Calculate trend significance based on frequency and growth rate.

        Args:
            topic: Trending topic dictionary

        Returns:
            TrendSignificance enum value
        """
        frequency = topic.get("frequency", 0)
        growth_rate = topic.get("growth_rate", 0)

        # Weighted score
        score = frequency * 0.6 + growth_rate * 10 * 0.4

        if score > 20:
            return TrendSignificance.HIGH
        elif score > 10:
            return TrendSignificance.MEDIUM
        else:
            return TrendSignificance.LOW

    def _determine_direction(self, growth_rate: float) -> TrendDirection:
        """
        Determine trend direction based on growth rate.

        Args:
            growth_rate: Growth rate value

        Returns:
            TrendDirection enum value
        """
        if growth_rate > 0.5:
            return TrendDirection.GROWING
        elif growth_rate < -0.3:
            return TrendDirection.DECLINING
        elif growth_rate > 0.1:
            return TrendDirection.EMERGING
        else:
            return TrendDirection.STABLE

    def _generate_trend_summary(self, trends: List[Dict[str, any]]) -> str:
        """
        Generate a summary of trends.

        Args:
            trends: List of trend dictionaries

        Returns:
            Summary string
        """
        if not trends:
            return "Недостаточно данных для анализа трендов."

        top_trend = trends[0]
        growing_trends = [t for t in trends if t.get("growth_rate", 0) > 0.3]

        summary = f"Основной тренд: '{top_trend['topic']}' (частота: {top_trend['frequency']}). "

        if growing_trends:
            summary += f"Растущие тренды: {', '.join([t['topic'] for t in growing_trends[:3]])}. "

        return summary

    async def compare_cross_industry_trends(
        self,
        primary_industry: str,
        related_industries: List[str],
        collected_data_by_industry: Dict[str, List[Dict[str, any]]],
    ) -> Dict[str, any]:
        """
        Compare trends across industries.

        Args:
            primary_industry: Primary industry to analyze
            related_industries: List of related industries
            collected_data_by_industry: Data grouped by industry

        Returns:
            Cross-industry trend analysis
        """
        industry_trends = {}

        # Analyze each industry
        for industry in [primary_industry] + related_industries:
            data = collected_data_by_industry.get(industry, [])
            if data:
                texts = [
                    {
                        "content": d.get("content", ""),
                        "date": d.get("date", datetime.utcnow()),
                    }
                    for d in data
                ]
                trends = self.trend_extractor.extract_trending_topics(texts, min_frequency=2, top_n=10)
                industry_trends[industry] = trends

        # Find common trends
        common_trends = self._find_common_trends(industry_trends)

        return {
            "primary_industry": primary_industry,
            "related_industries": related_industries,
            "industry_trends": industry_trends,
            "common_trends": common_trends,
            "cross_industry_insights": self._generate_cross_industry_insights(common_trends),
        }

    def _find_common_trends(self, industry_trends: Dict[str, List[Dict[str, any]]]) -> List[Dict[str, any]]:
        """
        Find trends common across multiple industries.

        Args:
            industry_trends: Trends by industry

        Returns:
            List of common trends
        """
        topic_industries = defaultdict(list)

        for industry, trends in industry_trends.items():
            for trend in trends:
                topic = trend["topic"]
                topic_industries[topic].append(industry)

        # Find topics appearing in multiple industries
        common_trends = []
        for topic, industries in topic_industries.items():
            if len(industries) > 1:
                common_trends.append({
                    "topic": topic,
                    "industries": industries,
                    "cross_industry_relevance": len(industries) / len(industry_trends),
                })

        common_trends.sort(key=lambda x: x["cross_industry_relevance"], reverse=True)

        return common_trends

    def _generate_cross_industry_insights(self, common_trends: List[Dict[str, any]]) -> str:
        """Generate insights from cross-industry trends."""
        if not common_trends:
            return "Общих трендов между отраслями не выявлено."

        top_common = common_trends[0]
        return (
            f"Наиболее значимый межотраслевой тренд: '{top_common['topic']}', "
            f"присутствует в {len(top_common['industries'])} отраслях."
        )
