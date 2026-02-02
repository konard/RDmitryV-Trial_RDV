"""Data source model."""

from sqlalchemy import Column, String, Text, DateTime, Float, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class SourceType(str, enum.Enum):
    """Data source type."""
    WEB_SCRAPING = "web_scraping"
    API = "api"
    NEWS = "news"
    GOVERNMENT = "government"
    SOCIAL_MEDIA = "social_media"
    DATABASE = "database"


class SourceStatus(str, enum.Enum):
    """Data source status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"


class DataSource(Base):
    """Data source model."""

    __tablename__ = "data_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    source_type = Column(Enum(SourceType), nullable=False)
    url = Column(Text, nullable=True)
    api_endpoint = Column(Text, nullable=True)

    # Reliability metrics
    reliability_score = Column(Float, default=0.5, nullable=False)  # 0-1 scale
    success_rate = Column(Float, default=1.0, nullable=False)  # Success rate

    # Status
    status = Column(Enum(SourceStatus), default=SourceStatus.ACTIVE, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Metadata
    category = Column(String, nullable=True)  # e.g., "market_data", "news", "statistics"
    update_frequency = Column(String, nullable=True)  # e.g., "daily", "weekly"
    last_successful_fetch = Column(DateTime, nullable=True)
    last_failed_fetch = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    collected_data = relationship("CollectedData", back_populates="source", cascade="all, delete-orphan")
