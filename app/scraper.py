"""
Playwright scraper for instante.justice.md
"""
from scrapling import StealthyFetcher
from datetime import datetime
from .models import LitigationCase
import time


class JusticeScraper:
    """Scraper for Moldova court decisions portal"""
    
    BASE_URL = "https://instante.justice.md/ro/hotaririle-instantei"
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.fetcher = None
    
    def _init_fetcher(self):
        """Initialize fetcher lazily"""
        if self.fetcher is None:
            self.fetcher = StealthyFetcher(headless=self.headless, auto_match=True)
    
    def search_company(self, company_name: str) -> list[LitigationCase]:
        """
        Search for court cases by company name
        
        Args:
            company_name: Name of the company to search for
            
        Returns:
            List of LitigationCase objects
        """
        self._init_fetcher()
        cases = []
        
        try:
            page = self.fetcher.new_page()
            
            # Navigate to search page
            page.goto(self.BASE_URL, wait_until="networkidle")
            
            # Find and fill search input
            input_selector = 'input[name="filter_implicat"]'
            if not page.query_selector(input_selector):
                input_selector = '.views-exposed-form input[type="text"]'
            
            page.fill(input_selector, company_name)
            
            # Click search button
            submit_selector = '.views-exposed-form button[type="submit"], .views-exposed-form input[type="submit"]'
            page.click(submit_selector)
            
            # Wait for results
            time.sleep(5)
            
            # Parse results table
            rows = page.query_selector_all("table.views-table tbody tr")
            
            for row in rows:
                cells = row.query_selector_all("td")
                if len(cells) >= 3:
                    case = self._parse_row(cells)
                    if case:
                        cases.append(case)
            
        except Exception as e:
            raise RuntimeError(f"Scraping failed: {str(e)}")
        finally:
            if self.fetcher:
                self.fetcher.close()
                self.fetcher = None
        
        return cases
    
    def _parse_row(self, cells) -> LitigationCase | None:
        """Parse table row into LitigationCase"""
        try:
            # Extract text from cells
            texts = [cell.inner_text().strip() for cell in cells]
            
            # Based on justice_results.json structure:
            # Column order: court, case_number, parties/description, dates...
            if len(texts) >= 3:
                return LitigationCase(
                    court=texts[0] if texts[0] else "N/A",
                    case_number=texts[1] if texts[1] else "N/A",
                    parties=texts[2] if texts[2] else "N/A",
                    filing_date=texts[3] if len(texts) > 3 else None,
                    hearing_date=texts[4] if len(texts) > 4 else None,
                    status=texts[5] if len(texts) > 5 else None,
                )
        except Exception:
            pass
        return None


# Singleton instance
_scraper: JusticeScraper | None = None


def get_scraper() -> JusticeScraper:
    """Get or create scraper instance"""
    global _scraper
    if _scraper is None:
        _scraper = JusticeScraper(headless=True)
    return _scraper
