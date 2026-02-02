"""Competitive analysis service."""

from typing import List, Dict
from app.services.nlp.sentiment_analyzer import SentimentAnalyzer
from app.services.nlp.text_processor import TextProcessor


class CompetitiveAnalyzer:
    """Service for competitive analysis and SWOT."""

    def __init__(self):
        """Initialize competitive analyzer."""
        self.sentiment_analyzer = SentimentAnalyzer()
        self.text_processor = TextProcessor()

    async def analyze_competitor(
        self,
        competitor_data: Dict[str, any],
        our_product_description: str,
    ) -> Dict[str, any]:
        """
        Analyze a single competitor.

        Args:
            competitor_data: Competitor information
            our_product_description: Our product description for comparison

        Returns:
            Competitor analysis results
        """
        competitor_name = competitor_data.get("name", "Unknown")
        competitor_description = competitor_data.get("description", "")

        # Calculate similarity score
        similarity_score = self._calculate_similarity(
            our_product_description,
            competitor_description,
        )

        # Perform SWOT analysis
        swot = self._perform_swot_analysis(competitor_data)

        # Assess threat level
        threat_level = self._assess_threat_level(competitor_data, similarity_score)

        return {
            "name": competitor_name,
            "similarity_score": similarity_score,
            "threat_level": threat_level,
            "swot": swot,
            "market_position": competitor_data.get("market_position", "unknown"),
            "key_advantages": self._extract_key_advantages(competitor_data),
            "vulnerabilities": self._extract_vulnerabilities(competitor_data),
        }

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using Jaccard similarity.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0-1)
        """
        tokens1 = set(self.text_processor.tokenize(text1, remove_stop_words=True))
        tokens2 = set(self.text_processor.tokenize(text2, remove_stop_words=True))

        if not tokens1 or not tokens2:
            return 0.0

        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)

        return len(intersection) / len(union) if union else 0.0

    def _perform_swot_analysis(self, competitor_data: Dict[str, any]) -> Dict[str, List[str]]:
        """
        Perform SWOT analysis for competitor.

        Args:
            competitor_data: Competitor information

        Returns:
            SWOT dictionary
        """
        # Extract existing SWOT if available
        swot = {
            "strengths": competitor_data.get("strengths", []),
            "weaknesses": competitor_data.get("weaknesses", []),
            "opportunities": competitor_data.get("opportunities", []),
            "threats": competitor_data.get("threats", []),
        }

        # If not available, generate basic SWOT
        if not any(swot.values()):
            swot = self._generate_basic_swot(competitor_data)

        return swot

    def _generate_basic_swot(self, competitor_data: Dict[str, any]) -> Dict[str, List[str]]:
        """Generate basic SWOT based on available data."""
        swot = {
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": [],
        }

        market_share = competitor_data.get("market_share", 0)
        if market_share > 20:
            swot["strengths"].append("Значительная доля рынка")
        elif market_share < 5:
            swot["weaknesses"].append("Небольшая доля рынка")

        if competitor_data.get("established", False):
            swot["strengths"].append("Устоявшийся бренд")
        else:
            swot["opportunities"].append("Возможность опередить нового игрока")

        return swot

    def _assess_threat_level(self, competitor_data: Dict[str, any], similarity_score: float) -> str:
        """
        Assess threat level of competitor.

        Args:
            competitor_data: Competitor information
            similarity_score: Product similarity score

        Returns:
            Threat level: "high", "medium", or "low"
        """
        threat_score = 0.0

        # Similarity factor
        threat_score += similarity_score * 40

        # Market share factor
        market_share = competitor_data.get("market_share", 0)
        threat_score += (market_share / 100) * 30

        # Brand strength factor
        if competitor_data.get("brand_recognition", "low") == "high":
            threat_score += 20
        elif competitor_data.get("brand_recognition") == "medium":
            threat_score += 10

        # Financial strength
        if competitor_data.get("financial_position", "weak") == "strong":
            threat_score += 10

        if threat_score > 70:
            return "high"
        elif threat_score > 40:
            return "medium"
        else:
            return "low"

    def _extract_key_advantages(self, competitor_data: Dict[str, any]) -> List[str]:
        """Extract key competitive advantages."""
        advantages = []

        if competitor_data.get("market_share", 0) > 15:
            advantages.append("Лидерская позиция на рынке")

        if competitor_data.get("brand_recognition") == "high":
            advantages.append("Сильный бренд")

        if competitor_data.get("innovation", False):
            advantages.append("Инновационный подход")

        if competitor_data.get("price_advantage", False):
            advantages.append("Ценовое преимущество")

        return advantages

    def _extract_vulnerabilities(self, competitor_data: Dict[str, any]) -> List[str]:
        """Extract competitor vulnerabilities."""
        vulnerabilities = []

        if competitor_data.get("customer_satisfaction", 5) < 3:
            vulnerabilities.append("Низкая удовлетворенность клиентов")

        if competitor_data.get("outdated_technology", False):
            vulnerabilities.append("Устаревшие технологии")

        if competitor_data.get("limited_regions", False):
            vulnerabilities.append("Ограниченная география присутствия")

        return vulnerabilities

    async def create_competitive_landscape(
        self,
        competitors: List[Dict[str, any]],
        our_product: Dict[str, any],
    ) -> Dict[str, any]:
        """
        Create comprehensive competitive landscape analysis.

        Args:
            competitors: List of competitor data
            our_product: Our product information

        Returns:
            Competitive landscape analysis
        """
        competitor_analyses = []

        for competitor in competitors:
            analysis = await self.analyze_competitor(
                competitor,
                our_product.get("description", ""),
            )
            competitor_analyses.append(analysis)

        # Categorize by threat level
        high_threat = [c for c in competitor_analyses if c["threat_level"] == "high"]
        medium_threat = [c for c in competitor_analyses if c["threat_level"] == "medium"]
        low_threat = [c for c in competitor_analyses if c["threat_level"] == "low"]

        return {
            "total_competitors": len(competitors),
            "competitor_analyses": competitor_analyses,
            "threat_distribution": {
                "high": len(high_threat),
                "medium": len(medium_threat),
                "low": len(low_threat),
            },
            "main_competitors": high_threat,
            "market_positioning_map": self._create_positioning_map(competitor_analyses),
            "strategic_recommendations": self._generate_strategic_recommendations(competitor_analyses),
        }

    def _create_positioning_map(self, competitors: List[Dict[str, any]]) -> Dict[str, any]:
        """Create market positioning map."""
        return {
            "note": "Positioning map would be generated based on key dimensions",
            "dimensions": ["price", "quality", "innovation", "market_share"],
            "competitors": [
                {
                    "name": c["name"],
                    "position": c.get("market_position", "unknown"),
                }
                for c in competitors
            ],
        }

    def _generate_strategic_recommendations(self, competitors: List[Dict[str, any]]) -> List[str]:
        """Generate strategic recommendations based on competitive analysis."""
        recommendations = []

        high_threat_count = sum(1 for c in competitors if c["threat_level"] == "high")

        if high_threat_count > 0:
            recommendations.append(
                f"Выявлено {high_threat_count} сильных конкурентов. "
                "Рекомендуется четкое дифференцирование продукта."
            )

        if high_threat_count == 0:
            recommendations.append(
                "Конкурентная среда благоприятна для входа на рынок. "
                "Рекомендуется активное наступление."
            )

        return recommendations
