"""
Playwright scraper for instante.justice.md
"""
from playwright.sync_api import sync_playwright
from .models import LitigationCase
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JusticeScraper:
    """Scraper for Moldova court decisions portal"""
    
    BASE_URL = "https://instante.justice.md/ro/hotaririle-instantei"
    
    def search_company(self, company_name: str) -> list[LitigationCase]:
        """Search for court cases by company name"""
        cases = []
        
        logger.info(f"Starting search for: {company_name}")
        
        with sync_playwright() as p:
            logger.info("Launching browser...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                logger.info(f"Navigating to {self.BASE_URL}")
                page.goto(self.BASE_URL, wait_until="networkidle", timeout=30000)
                logger.info("Page loaded")
                
                # Fill search input
                input_selector = 'input[name="filter_implicat"]'
                input_el = page.query_selector(input_selector)
                logger.info(f"Input element found: {input_el is not None}")
                
                if not input_el:
                    input_selector = '.views-exposed-form input[type="text"]'
                    input_el = page.query_selector(input_selector)
                    logger.info(f"Fallback input found: {input_el is not None}")
                
                page.fill(input_selector, company_name)
                logger.info("Search term filled")
                
                # Click search button
                submit_selector = '.views-exposed-form input[type="submit"], .views-exposed-form button[type="submit"]'
                submit_el = page.query_selector(submit_selector)
                logger.info(f"Submit button found: {submit_el is not None}")
                
                page.click(submit_selector)
                logger.info("Search button clicked")
                
                # Wait for results
                time.sleep(5)
                logger.info("Waited 5 seconds")
                
                # Log page content for debug
                page_title = page.title()
                logger.info(f"Page title: {page_title}")
                
                # Parse results table
                rows = page.query_selector_all("table.views-table tbody tr")
                logger.info(f"Found {len(rows)} table rows")
                
                for i, row in enumerate(rows):
                    case = self._parse_row(row)
                    if case:
                        cases.append(case)
                        if i < 3:
                            logger.info(f"Case {i}: {case.case_number}")
                
                logger.info(f"Total cases parsed: {len(cases)}")
                        
            except Exception as e:
                logger.error(f"Scraping failed: {str(e)}")
                raise RuntimeError(f"Scraping failed: {str(e)}")
            finally:
                browser.close()
                logger.info("Browser closed")
        
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
        except Exception as e:
            logger.error(f"Parse error: {e}")
        return None
