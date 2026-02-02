"""Regional analysis service for Russian Federation."""

from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.region import Region


class RegionalAnalyzer:
    """Service for analyzing regional markets in Russia."""

    def __init__(self):
        """Initialize regional analyzer."""
        self.federal_districts = [
            "Центральный",
            "Северо-Западный",
            "Южный",
            "Северо-Кавказский",
            "Приволжский",
            "Уральский",
            "Сибирский",
            "Дальневосточный",
        ]

    async def analyze_region(
        self,
        region_name: str,
        industry: str,
        db: AsyncSession,
    ) -> Dict[str, any]:
        """
        Analyze a specific region for an industry.

        Args:
            region_name: Name of the region
            industry: Industry to analyze
            db: Database session

        Returns:
            Regional analysis results
        """
        # Fetch region data from database
        result = await db.execute(
            select(Region).where(Region.name == region_name)
        )
        region = result.scalar_one_or_none()

        if not region:
            # Return basic analysis without detailed data
            return {
                "region": region_name,
                "industry": industry,
                "status": "no_data",
                "message": "Данные по региону недоступны",
            }

        # Calculate opportunity score
        opportunity_score = self._calculate_opportunity_score(region, industry)

        # Generate insights
        insights = self._generate_regional_insights(region, industry)

        return {
            "region": region.name,
            "federal_district": region.federal_district,
            "industry": industry,
            "demographic": {
                "population": region.population,
                "population_density": region.population_density,
                "urban_population_percent": region.urban_population_percent,
            },
            "economic": {
                "gdp": region.gdp,
                "gdp_per_capita": region.gdp_per_capita,
                "unemployment_rate": region.unemployment_rate,
                "average_income": region.average_income,
            },
            "business_environment": {
                "business_activity_index": region.business_activity_index,
                "number_of_businesses": region.number_of_businesses,
                "investment_attractiveness": region.investment_attractiveness,
            },
            "opportunity_score": opportunity_score,
            "key_industries": region.key_industries or [],
            "regional_features": region.regional_features,
            "insights": insights,
        }

    def _calculate_opportunity_score(self, region: Region, industry: str) -> float:
        """
        Calculate opportunity score for launching business in region.

        Args:
            region: Region model
            industry: Industry name

        Returns:
            Opportunity score (0-10)
        """
        score = 5.0  # Base score

        # Population factor (more population = more potential customers)
        if region.population:
            if region.population > 2_000_000:
                score += 1.0
            elif region.population > 1_000_000:
                score += 0.5

        # GDP per capita factor
        if region.gdp_per_capita:
            if region.gdp_per_capita > 700_000:
                score += 1.0
            elif region.gdp_per_capita > 500_000:
                score += 0.5

        # Business activity factor
        if region.business_activity_index:
            score += (region.business_activity_index / 10) * 1.5

        # Investment attractiveness factor
        if region.investment_attractiveness:
            score += (region.investment_attractiveness / 10) * 1.5

        # Unemployment rate factor (lower is better)
        if region.unemployment_rate:
            if region.unemployment_rate < 4.0:
                score += 0.5
            elif region.unemployment_rate > 7.0:
                score -= 0.5

        # Industry match factor
        if region.key_industries and industry in str(region.key_industries):
            score += 1.0

        # Normalize to 0-10
        return max(0.0, min(10.0, score))

    def _generate_regional_insights(self, region: Region, industry: str) -> List[str]:
        """
        Generate insights about the region.

        Args:
            region: Region model
            industry: Industry name

        Returns:
            List of insight strings
        """
        insights = []

        # Population insights
        if region.population:
            if region.population > 1_000_000:
                insights.append(f"Крупный региональный рынок с населением {region.population:,} человек")
            else:
                insights.append(f"Средний региональный рынок с населением {region.population:,} человек")

        # Urban population
        if region.urban_population_percent:
            if region.urban_population_percent > 75:
                insights.append("Высокая урбанизация благоприятна для розничного бизнеса")

        # Economic insights
        if region.gdp_per_capita:
            if region.gdp_per_capita > 600_000:
                insights.append("Высокий уровень доходов населения")
            elif region.gdp_per_capita < 300_000:
                insights.append("Необходимо учитывать ограниченную покупательную способность")

        # Business environment
        if region.investment_attractiveness:
            if region.investment_attractiveness > 7:
                insights.append("Регион привлекателен для инвестиций")
            elif region.investment_attractiveness < 4:
                insights.append("Инвестиционный климат требует внимания")

        # Industry-specific
        if region.key_industries:
            if industry in str(region.key_industries):
                insights.append(f"Регион имеет развитую инфраструктуру для отрасли '{industry}'")

        return insights

    async def compare_regions(
        self,
        region_names: List[str],
        industry: str,
        db: AsyncSession,
    ) -> Dict[str, any]:
        """
        Compare multiple regions for market entry.

        Args:
            region_names: List of region names to compare
            industry: Industry to analyze
            db: Database session

        Returns:
            Comparison results
        """
        regional_analyses = []

        for region_name in region_names:
            analysis = await self.analyze_region(region_name, industry, db)
            regional_analyses.append(analysis)

        # Rank regions by opportunity score
        ranked_regions = sorted(
            [r for r in regional_analyses if r.get("opportunity_score")],
            key=lambda x: x["opportunity_score"],
            reverse=True,
        )

        return {
            "industry": industry,
            "regions_compared": len(region_names),
            "regional_analyses": regional_analyses,
            "ranking": ranked_regions,
            "recommendation": ranked_regions[0] if ranked_regions else None,
        }
