"""
Playwright scraper for instante.justice.md
"""
from playwright.sync_api import sync_playwright
from datetime import datetime
from .models import LitigationCase
import time


class JusticeScraper:
    """Scraper for Moldova court decisions portal"""
    
    BASE_URL = "https://instante.justice.md/ro/hotaririle-instantei"
    
    def search_company(self, company_name: str) -> list[LitigationCase]:
        """
        Search for court cases by company name
        """
        cases = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                page.goto(self.BASE_URL, wait_until="networkidle", timeout=30000)
                
                # Fill search input
                input_selector = 'input[name="filter_implicat"]'
                page.fill(input_selector, company_name)
                
                # Click search button
                submit_selector = '.views-exposed-form input[type="submit"], .views-exposed-form button[type="submit"]'
                page.click(submit_selector)
                
                # Wait for results
                time.sleep(5)
                
                # Parse results table
                rows = page.query_selector_all("table.views-table tbody tr")
                
                for row in rows:
                    case = self._parse_row(row)
                    if case:
                        cases.append(case)
                        
            except Exception as e:
                raise RuntimeError(f"Scraping failed: {str(e)}")
            finally:
                browser.close()
        
        return cases
    
    def _parse_row(self, row) -> LitigationCase | None:
        """Parse table row into LitigationCase"""
        try:
            cells = row.query_selector_all("td")
            
            if len(cells) >= 3:
                texts = [cell.inner_text().strip() for cell in cells]
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
