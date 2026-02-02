"""News parser service for extracting articles from news sites."""

from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re

from app.services.data_collection.scraper_service import ScraperService


class NewsParserService:
    """Service for parsing news websites and extracting articles."""

    def __init__(self):
        """Initialize news parser service."""
        self.scraper = ScraperService()

    def parse_article(self, html_content: str, url: str) -> Dict[str, Optional[str]]:
        """
        Parse a single article from HTML content.

        Args:
            html_content: HTML content of the article
            url: URL of the article

        Returns:
            Dictionary with article data
        """
        soup = BeautifulSoup(html_content, "lxml")

        article_data = {
            "title": None,
            "content": None,
            "summary": None,
            "author": None,
            "published_date": None,
            "url": url,
            "tags": [],
            "category": None,
        }

        # Extract title
        title_selectors = [
            ("h1", {"class": re.compile("title|headline|heading")}),
            ("h1", {}),
            ("title", {}),
        ]
        for tag, attrs in title_selectors:
            title_tag = soup.find(tag, attrs)
            if title_tag:
                article_data["title"] = title_tag.get_text().strip()
                break

        # Extract main content
        content_selectors = [
            ("div", {"class": re.compile("article|content|post|entry")}),
            ("article", {}),
        ]
        for tag, attrs in content_selectors:
            content_tag = soup.find(tag, attrs)
            if content_tag:
                # Remove unwanted elements
                for unwanted in content_tag.find_all(["script", "style", "aside", "nav"]):
                    unwanted.decompose()

                # Get text paragraphs
                paragraphs = content_tag.find_all("p")
                if paragraphs:
                    content_text = "\n\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
                    article_data["content"] = content_text
                    break

        # Extract summary/description
        meta_description = soup.find("meta", {"name": "description"})
        if meta_description:
            article_data["summary"] = meta_description.get("content", "").strip()
        elif soup.find("meta", {"property": "og:description"}):
            article_data["summary"] = soup.find("meta", {"property": "og:description"}).get("content", "").strip()

        # Extract author
        author_selectors = [
            ("meta", {"name": "author"}),
            ("span", {"class": re.compile("author")}),
            ("a", {"class": re.compile("author")}),
        ]
        for tag, attrs in author_selectors:
            author_tag = soup.find(tag, attrs)
            if author_tag:
                if tag == "meta":
                    article_data["author"] = author_tag.get("content", "").strip()
                else:
                    article_data["author"] = author_tag.get_text().strip()
                break

        # Extract published date
        date_selectors = [
            ("meta", {"property": "article:published_time"}),
            ("time", {"class": re.compile("date|time|published")}),
            ("span", {"class": re.compile("date|time|published")}),
        ]
        for tag, attrs in date_selectors:
            date_tag = soup.find(tag, attrs)
            if date_tag:
                if tag == "meta":
                    article_data["published_date"] = date_tag.get("content", "").strip()
                elif tag == "time" and date_tag.get("datetime"):
                    article_data["published_date"] = date_tag.get("datetime").strip()
                else:
                    article_data["published_date"] = date_tag.get_text().strip()
                break

        # Extract tags/keywords
        keywords_meta = soup.find("meta", {"name": "keywords"})
        if keywords_meta:
            keywords = keywords_meta.get("content", "")
            article_data["tags"] = [tag.strip() for tag in keywords.split(",") if tag.strip()]

        return article_data

    async def fetch_and_parse_article(self, url: str) -> Optional[Dict[str, Optional[str]]]:
        """
        Fetch and parse an article from a URL.

        Args:
            url: Article URL

        Returns:
            Dictionary with parsed article data or None
        """
        collected_data = await self.scraper.fetch_url(url)
        if not collected_data:
            return None

        article_data = self.parse_article(collected_data.raw_content, url)
        return article_data

    async def fetch_and_parse_multiple(self, urls: List[str]) -> List[Dict[str, Optional[str]]]:
        """
        Fetch and parse multiple articles.

        Args:
            urls: List of article URLs

        Returns:
            List of parsed article dictionaries
        """
        collected_data_list = await self.scraper.fetch_multiple_urls(urls)

        articles = []
        for collected_data in collected_data_list:
            if collected_data:
                article_data = self.parse_article(collected_data.raw_content, collected_data.source_url)
                articles.append(article_data)

        return articles

    def categorize_article(self, article: Dict[str, Optional[str]], industry: str) -> bool:
        """
        Check if article is relevant to the given industry.

        Args:
            article: Parsed article dictionary
            industry: Target industry

        Returns:
            True if article is relevant, False otherwise
        """
        # Simple keyword-based relevance check
        industry_keywords = industry.lower().split()

        text_to_check = " ".join([
            article.get("title", ""),
            article.get("content", ""),
            article.get("summary", ""),
            " ".join(article.get("tags", [])),
        ]).lower()

        # Check if any industry keyword appears in the text
        for keyword in industry_keywords:
            if keyword in text_to_check:
                return True

        return False

    def extract_news_sentiment_keywords(self, article: Dict[str, Optional[str]]) -> Dict[str, List[str]]:
        """
        Extract sentiment-indicating keywords from article.

        Args:
            article: Parsed article dictionary

        Returns:
            Dictionary with positive, negative, and neutral keywords
        """
        # Russian sentiment keywords
        positive_keywords = [
            "рост", "развитие", "успех", "прибыль", "увеличение", "инновация",
            "эффективность", "лидер", "победа", "достижение", "улучшение",
        ]

        negative_keywords = [
            "падение", "кризис", "убыток", "снижение", "проблема", "риск",
            "угроза", "спад", "сокращение", "банкротство", "дефицит",
        ]

        content = " ".join([
            article.get("title", ""),
            article.get("content", ""),
            article.get("summary", ""),
        ]).lower()

        found_positive = [kw for kw in positive_keywords if kw in content]
        found_negative = [kw for kw in negative_keywords if kw in content]

        return {
            "positive": found_positive,
            "negative": found_negative,
            "sentiment_score": len(found_positive) - len(found_negative),
        }
