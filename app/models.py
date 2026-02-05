"""
Pydantic models for litigation scraper API v2.0
Refund Project - Traffic Violations (art. 236)
"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class CaseType(str, Enum):
    """Case type filter values for Tipul_dosarului parameter"""
    ALL = ""
    CIVIL = "1"
    CONTRAVENTIONAL = "2"
    PENAL = "3"


class CourtInstance(str, Enum):
    """Court instance filter values"""
    ALL = "All"
    # Add specific courts as needed


class ScrapeRequest(BaseModel):
    """Request body for scraping with flexible filters"""

    # Primary search field (article number or case name)
    denumirea_dosarului: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Case name or article number (e.g., 'art. 236')",
        examples=["art. 236", "art. 236 alin. (1)"]
    )

    # Optional filters
    tipul_dosarului: CaseType = Field(
        default=CaseType.CONTRAVENTIONAL,
        description="Case type: 1=Civil, 2=Contraventional, 3=Penal"
    )

    instance: CourtInstance = Field(
        default=CourtInstance.ALL,
        description="Court instance filter"
    )

    numarul_dosarului: Optional[str] = Field(
        default=None,
        description="Specific case number"
    )

    data_pronuntarii: Optional[str] = Field(
        default=None,
        description="Ruling date filter (YYYY-MM-DD)"
    )

    # Pagination
    max_pages: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Maximum pages to scrape (10 results per page)"
    )

    # PDF options
    download_pdfs: bool = Field(
        default=False,
        description="Whether to download PDF documents"
    )

    convert_to_markdown: bool = Field(
        default=False,
        description="Whether to convert PDFs to Markdown/JSON"
    )


class LitigationCase(BaseModel):
    """Single court case record with full metadata"""

    # Core identifiers
    case_number: str = Field(..., description="Case number (Numărul dosarului)")
    case_name: str = Field(..., description="Case description (Denumirea dosarului)")

    # Court info
    court: str = Field(..., description="Court name (Instanțe judecătorești)")
    judge: Optional[str] = Field(default=None, description="Judge name (Judecător)")

    # Case classification
    case_type: Optional[str] = Field(default=None, description="Case type (Tipul dosarului)")
    topic: Optional[str] = Field(default=None, description="Case topic (Tematica dosarului)")

    # Dates
    ruling_date: Optional[str] = Field(default=None, description="Ruling date (Data pronunțării)")
    registration_date: Optional[str] = Field(default=None, description="Registration date (Data înregistrării)")
    publication_date: Optional[str] = Field(default=None, description="Publication date (Data publicării)")

    # Document
    pdf_url: Optional[str] = Field(default=None, description="PDF document URL")
    pdf_id: Optional[str] = Field(default=None, description="PDF GUID extracted from URL")

    # Legacy fields (deprecated, kept for compatibility)
    parties: Optional[str] = Field(default=None, deprecated=True)
    filing_date: Optional[str] = Field(default=None, deprecated=True)
    hearing_date: Optional[str] = Field(default=None, deprecated=True)
    status: Optional[str] = Field(default=None, deprecated=True)


class ScrapeResponse(BaseModel):
    """Response from scraper"""

    success: bool
    query: str = Field(..., description="Search query used")
    filters_applied: dict = Field(default_factory=dict, description="Filters that were applied")
    total_cases: int
    total_pages_scraped: int = Field(default=1)
    cases: list[LitigationCase]
    scraped_at: str
    error: Optional[str] = None

    # Legacy field (deprecated)
    company_name: Optional[str] = Field(default=None, deprecated=True)
