"""Database query optimization utilities."""

from typing import List, Optional, Type, TypeVar
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

T = TypeVar('T', bound=Base)


class QueryOptimizer:
    """Utility class for optimizing database queries."""

    @staticmethod
    async def get_with_relations(
        db: AsyncSession,
        model: Type[T],
        id: any,
        relations: List[str] = None,
    ) -> Optional[T]:
        """
        Get model instance with eager loading of relations.

        Args:
            db: Database session
            model: SQLAlchemy model class
            id: Instance ID
            relations: List of relationship names to eager load

        Returns:
            Model instance or None

        Example:
            research = await QueryOptimizer.get_with_relations(
                db,
                Research,
                research_id,
                relations=["reports", "analysis_results"]
            )
        """
        query = select(model).where(model.id == id)

        if relations:
            for relation in relations:
                query = query.options(selectinload(getattr(model, relation)))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_paginated(
        db: AsyncSession,
        model: Type[T],
        skip: int = 0,
        limit: int = 20,
        filters: dict = None,
        order_by: any = None,
    ) -> tuple[List[T], int]:
        """
        Get paginated results with total count.

        Args:
            db: Database session
            model: SQLAlchemy model class
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of filters {field: value}
            order_by: Column to order by

        Returns:
            Tuple of (records, total_count)

        Example:
            researches, total = await QueryOptimizer.get_paginated(
                db,
                Research,
                skip=0,
                limit=20,
                filters={"user_id": user_id},
                order_by=Research.created_at.desc()
            )
        """
        # Build query
        query = select(model)

        # Apply filters
        if filters:
            for field, value in filters.items():
                query = query.where(getattr(model, field) == value)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply ordering
        if order_by is not None:
            query = query.order_by(order_by)

        # Apply pagination
        query = query.offset(skip).limit(limit)

        # Execute query
        result = await db.execute(query)
        items = result.scalars().all()

        return items, total

    @staticmethod
    async def bulk_create(
        db: AsyncSession,
        model: Type[T],
        instances: List[dict],
        return_instances: bool = False,
    ) -> Optional[List[T]]:
        """
        Bulk create instances efficiently.

        Args:
            db: Database session
            model: SQLAlchemy model class
            instances: List of dictionaries with instance data
            return_instances: Whether to return created instances

        Returns:
            List of created instances if return_instances is True

        Example:
            data = [
                {"name": "Source 1", "url": "http://example1.com"},
                {"name": "Source 2", "url": "http://example2.com"},
            ]
            await QueryOptimizer.bulk_create(db, DataSource, data)
        """
        if not instances:
            return []

        # Create instances
        model_instances = [model(**data) for data in instances]

        # Add to session
        db.add_all(model_instances)
        await db.commit()

        if return_instances:
            # Refresh all instances
            for instance in model_instances:
                await db.refresh(instance)
            return model_instances

        return None

    @staticmethod
    async def exists(
        db: AsyncSession,
        model: Type[T],
        filters: dict,
    ) -> bool:
        """
        Check if record exists efficiently.

        Args:
            db: Database session
            model: SQLAlchemy model class
            filters: Dictionary of filters

        Returns:
            True if record exists

        Example:
            exists = await QueryOptimizer.exists(
                db,
                User,
                {"email": "test@example.com"}
            )
        """
        query = select(model)

        for field, value in filters.items():
            query = query.where(getattr(model, field) == value)

        query = select(func.count()).select_from(query.subquery())

        result = await db.execute(query)
        count = result.scalar()

        return count > 0

    @staticmethod
    def optimize_query_for_listing(query, model: Type[T]) -> any:
        """
        Optimize query for listing views.

        Args:
            query: SQLAlchemy query
            model: Model class

        Returns:
            Optimized query

        Example:
            query = select(Research)
            query = QueryOptimizer.optimize_query_for_listing(query, Research)
        """
        # Use joined loading for frequently accessed relations
        # This reduces N+1 queries

        # Example: if listing researches, load user data
        if hasattr(model, 'user'):
            query = query.options(joinedload(model.user))

        return query


class DatabaseIndexHelper:
    """Helper class for database indexing recommendations."""

    @staticmethod
    def get_index_recommendations() -> List[str]:
        """
        Get database index recommendations for the application.

        Returns:
            List of SQL CREATE INDEX statements

        These indexes should be created via Alembic migrations.
        """
        return [
            # Research table indexes
            "CREATE INDEX IF NOT EXISTS idx_research_user_id ON research(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_research_status ON research(status);",
            "CREATE INDEX IF NOT EXISTS idx_research_created_at ON research(created_at DESC);",
            "CREATE INDEX IF NOT EXISTS idx_research_user_created ON research(user_id, created_at DESC);",

            # Report table indexes
            "CREATE INDEX IF NOT EXISTS idx_report_research_id ON report(research_id);",
            "CREATE INDEX IF NOT EXISTS idx_report_created_at ON report(created_at DESC);",

            # Data source indexes
            "CREATE INDEX IF NOT EXISTS idx_data_source_url ON data_source(url);",
            "CREATE INDEX IF NOT EXISTS idx_data_source_type ON data_source(source_type);",
            "CREATE INDEX IF NOT EXISTS idx_data_source_reliability ON data_source(reliability_score DESC);",

            # Collected data indexes
            "CREATE INDEX IF NOT EXISTS idx_collected_data_source ON collected_data(source_id);",
            "CREATE INDEX IF NOT EXISTS idx_collected_data_research ON collected_data(research_id);",
            "CREATE INDEX IF NOT EXISTS idx_collected_data_collected_at ON collected_data(collected_at DESC);",

            # Analysis result indexes
            "CREATE INDEX IF NOT EXISTS idx_analysis_result_research ON analysis_result(research_id);",
            "CREATE INDEX IF NOT EXISTS idx_analysis_result_type ON analysis_result(analysis_type);",

            # Verification indexes
            "CREATE INDEX IF NOT EXISTS idx_verification_source ON source_verification(source_id);",
            "CREATE INDEX IF NOT EXISTS idx_verification_status ON source_verification(status);",
            "CREATE INDEX IF NOT EXISTS idx_verification_verified_at ON source_verification(verified_at DESC);",

            # Composite indexes for common queries
            "CREATE INDEX IF NOT EXISTS idx_research_user_status ON research(user_id, status);",
            "CREATE INDEX IF NOT EXISTS idx_collected_data_research_source ON collected_data(research_id, source_id);",
        ]
