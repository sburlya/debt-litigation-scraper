"""
FastAPI application for litigation scraper
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

from .models import ScrapeRequest, ScrapeResponse, LitigationCase
from .scraper import JusticeScraper


app = FastAPI(
    title="Debt AI Litigation Scraper",
    description="Microservice for scraping court cases from instante.justice.md",
    version="1.0.0",
)

# CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,https://debt.md").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/litigation", response_model=ScrapeResponse)
async def scrape_litigation(request: ScrapeRequest):
    """
    Scrape court cases for a company
    
    Args:
        request: ScrapeRequest with company_name
        
    Returns:
        ScrapeResponse with list of cases
    """
    company_name = request.company_name.strip()
    
    if not company_name:
        raise HTTPException(status_code=400, detail="company_name is required")
    
    if len(company_name) < 3:
        raise HTTPException(status_code=400, detail="company_name must be at least 3 characters")
    
    try:
        scraper = JusticeScraper()
        cases = scraper.search_company(company_name)
        
        return ScrapeResponse(
            success=True,
            company_name=company_name,
            total_cases=len(cases),
            cases=cases,
            scraped_at=datetime.utcnow().isoformat(),
            error=None,
        )
        
    except Exception as e:
        return ScrapeResponse(
            success=False,
            company_name=company_name,
            total_cases=0,
            cases=[],
            scraped_at=datetime.utcnow().isoformat(),
            error=str(e),
        )


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "service": "Debt AI Litigation Scraper",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "scrape": "POST /api/litigation",
        },
    }
