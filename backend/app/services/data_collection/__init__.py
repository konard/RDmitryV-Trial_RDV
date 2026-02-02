"""Data collection services."""

from app.services.data_collection.scraper_service import ScraperService
from app.services.data_collection.api_integrations import APIIntegrationService
from app.services.data_collection.news_parser import NewsParserService

__all__ = ["ScraperService", "APIIntegrationService", "NewsParserService"]
