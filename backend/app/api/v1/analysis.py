"""Analysis API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.research import Research
from app.models.analysis_result import AnalysisResult, AnalysisType
from app.services.analysis.trend_analyzer import TrendAnalyzer
from app.services.analysis.regional_analyzer import RegionalAnalyzer
from app.services.analysis.competitive_analyzer import CompetitiveAnalyzer
from sqlalchemy import select


router = APIRouter()


class TrendAnalysisRequest(BaseModel):
    """Request model for trend analysis."""
    research_id: str
    industry: str


class RegionalAnalysisRequest(BaseModel):
    """Request model for regional analysis."""
    research_id: str
    region_name: str
    industry: str


class CompetitiveAnalysisRequest(BaseModel):
    """Request model for competitive analysis."""
    research_id: str
    competitor_data: List[dict]
    our_product: dict


@router.post("/trends", response_model=dict)
async def analyze_trends(
    request: TrendAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze trends for a research project.

    Args:
        request: Trend analysis request
        db: Database session
        current_user: Current authenticated user

    Returns:
        Trend analysis results
    """
    # Verify research belongs to user
    result = await db.execute(
        select(Research).where(
            Research.id == request.research_id,
            Research.user_id == current_user.id,
        )
    )
    research = result.scalar_one_or_none()

    if not research:
        raise HTTPException(status_code=404, detail="Research not found")

    # Fetch collected data for research
    # In a real implementation, this would fetch actual collected data
    collected_data = []  # Placeholder

    # Perform trend analysis
    trend_analyzer = TrendAnalyzer()
    analysis_results = await trend_analyzer.analyze_industry_trends(
        industry=request.industry,
        collected_data=collected_data,
    )

    # Save analysis results
    analysis_result = AnalysisResult(
        research_id=research.id,
        analysis_type=AnalysisType.TREND,
        title=f"Trend Analysis for {request.industry}",
        summary=analysis_results.get("summary", ""),
        results=analysis_results,
    )
    db.add(analysis_result)
    await db.commit()

    return analysis_results


@router.post("/regional", response_model=dict)
async def analyze_regional(
    request: RegionalAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze regional market.

    Args:
        request: Regional analysis request
        db: Database session
        current_user: Current authenticated user

    Returns:
        Regional analysis results
    """
    # Verify research belongs to user
    result = await db.execute(
        select(Research).where(
            Research.id == request.research_id,
            Research.user_id == current_user.id,
        )
    )
    research = result.scalar_one_or_none()

    if not research:
        raise HTTPException(status_code=404, detail="Research not found")

    # Perform regional analysis
    regional_analyzer = RegionalAnalyzer()
    analysis_results = await regional_analyzer.analyze_region(
        region_name=request.region_name,
        industry=request.industry,
        db=db,
    )

    # Save analysis results
    analysis_result = AnalysisResult(
        research_id=research.id,
        analysis_type=AnalysisType.REGIONAL,
        title=f"Regional Analysis: {request.region_name}",
        summary=f"Analysis of {request.region_name} for {request.industry}",
        results=analysis_results,
    )
    db.add(analysis_result)
    await db.commit()

    return analysis_results


@router.post("/competitive", response_model=dict)
async def analyze_competitive(
    request: CompetitiveAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze competitive landscape.

    Args:
        request: Competitive analysis request
        db: Database session
        current_user: Current authenticated user

    Returns:
        Competitive analysis results
    """
    # Verify research belongs to user
    result = await db.execute(
        select(Research).where(
            Research.id == request.research_id,
            Research.user_id == current_user.id,
        )
    )
    research = result.scalar_one_or_none()

    if not research:
        raise HTTPException(status_code=404, detail="Research not found")

    # Perform competitive analysis
    competitive_analyzer = CompetitiveAnalyzer()
    analysis_results = await competitive_analyzer.create_competitive_landscape(
        competitors=request.competitor_data,
        our_product=request.our_product,
    )

    # Save analysis results
    analysis_result = AnalysisResult(
        research_id=research.id,
        analysis_type=AnalysisType.COMPETITIVE,
        title="Competitive Landscape Analysis",
        summary=f"Analysis of {len(request.competitor_data)} competitors",
        results=analysis_results,
    )
    db.add(analysis_result)
    await db.commit()

    return analysis_results


@router.get("/results/{research_id}", response_model=List[dict])
async def get_analysis_results(
    research_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all analysis results for a research project.

    Args:
        research_id: Research project ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of analysis results
    """
    # Verify research belongs to user
    result = await db.execute(
        select(Research).where(
            Research.id == research_id,
            Research.user_id == current_user.id,
        )
    )
    research = result.scalar_one_or_none()

    if not research:
        raise HTTPException(status_code=404, detail="Research not found")

    # Fetch all analysis results
    result = await db.execute(
        select(AnalysisResult).where(AnalysisResult.research_id == research_id)
    )
    analysis_results = result.scalars().all()

    return [
        {
            "id": str(ar.id),
            "analysis_type": ar.analysis_type,
            "title": ar.title,
            "summary": ar.summary,
            "results": ar.results,
            "created_at": ar.created_at.isoformat(),
        }
        for ar in analysis_results
    ]
