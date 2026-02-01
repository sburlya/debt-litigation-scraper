"""
Pydantic models for litigation scraper API
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date


class LitigationCase(BaseModel):
    """Single court case record"""
    case_number: str
    court: str
    parties: str
    case_type: Optional[str] = None
    filing_date: Optional[str] = None
    hearing_date: Optional[str] = None
    status: Optional[str] = None


class ScrapeRequest(BaseModel):
    """Request body for scraping"""
    company_name: str


class ScrapeResponse(BaseModel):
    """Response from scraper"""
    success: bool
    company_name: str
    total_cases: int
    cases: list[LitigationCase]
    scraped_at: str
    error: Optional[str] = None
