"""
Playwright scraper for instante.justice.md
"""
from scrapling import Fetcher
from datetime import datetime
from .models import LitigationCase
import time


class JusticeScraper:
    """Scraper for Moldova court decisions portal"""
    
    BASE_URL = "https://instante.justice.md/ro/hotaririle-instantei"
    
    def search_company(self, company_name: str) -> list[LitigationCase]:
        """
        Search for court cases by company name
        
        Args:
            company_name: Name of the company to search for
            
        Returns:
            List of LitigationCase objects
        """
        cases = []
        
        try:
            fetcher = Fetcher(auto_match=True)
            
            # Build search URL with query parameter
            search_url = f"{self.BASE_URL}?filter_implicat={company_name}"
            
            # Fetch the page
            response = fetcher.get(search_url)
            
            if response.status != 200:
                raise RuntimeError(f"HTTP {response.status}")
            
            # Parse results table
            rows = response.css("table.views-table tbody tr")
            
            for row in rows:
                case = self._parse_row(row)
                if case:
                    cases.append(case)
            
        except Exception as e:
            raise RuntimeError(f"Scraping failed: {str(e)}")
        
        return cases
    
    def _parse_row(self, row) -> LitigationCase | None:
        """Parse table row into LitigationCase"""
        try:
            cells = row.css("td")
            
            if len(cells) >= 3:
                return LitigationCase(
                    court=cells[0].text.strip() if cells[0].text else "N/A",
                    case_number=cells[1].text.strip() if cells[1].text else "N/A",
                    parties=cells[2].text.strip() if cells[2].text else "N/A",
                    filing_date=cells[3].text.strip() if len(cells) > 3 and cells[3].text else None,
                    hearing_date=cells[4].text.strip() if len(cells) > 4 and cells[4].text else None,
                    status=cells[5].text.strip() if len(cells) > 5 and cells[5].text else None,
                )
        except Exception:
            pass
        return None
