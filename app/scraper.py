"""
Async Playwright scraper for instante.justice.md
"""
from playwright.async_api import async_playwright
from .models import LitigationCase
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JusticeScraper:
    """Scraper for Moldova court decisions portal"""
    
    BASE_URL = "https://instante.justice.md/ro/hotaririle-instantei"
    
    async def search_company(self, company_name: str) -> list[LitigationCase]:
        """Search for court cases by company name"""
        cases = []
        
        logger.info(f"Starting search for: {company_name}")
        
        async with async_playwright() as p:
            logger.info("Launching browser...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                logger.info(f"Navigating to {self.BASE_URL}")
                await page.goto(self.BASE_URL, wait_until="networkidle", timeout=30000)
                logger.info("Page loaded")
                
                # Wait for form to be visible
                logger.info("Waiting for search form...")
                await page.wait_for_selector('.views-exposed-form', timeout=10000)
                logger.info("Form found")
                
                # Try multiple selectors for input
                input_selectors = [
                    'input[name="filter_implicat"]',
                    '#edit-filter-implicat',
                    '.views-exposed-form input[type="text"]',
                    'input.form-text'
                ]
                
                input_found = False
                for selector in input_selectors:
                    try:
                        el = await page.query_selector(selector)
                        if el:
                            logger.info(f"Input found with: {selector}")
                            await page.fill(selector, company_name)
                            input_found = True
                            break
                    except:
                        continue
                
                if not input_found:
                    # Log page HTML for debug
                    html = await page.content()
                    logger.error(f"No input found. Page HTML (first 2000 chars): {html[:2000]}")
                    raise RuntimeError("Search input not found")
                
                logger.info("Search term filled")
                
                # Try multiple selectors for submit button
                submit_selectors = [
                    'input[type="submit"]',
                    'button[type="submit"]',
                    '#edit-submit-search-results',
                    '.views-exposed-form button',
                    '.form-submit'
                ]
                
                submit_found = False
                for selector in submit_selectors:
                    try:
                        el = await page.query_selector(selector)
                        if el:
                            logger.info(f"Submit found with: {selector}")
                            await page.click(selector)
                            submit_found = True
                            break
                    except:
                        continue
                
                if not submit_found:
                    raise RuntimeError("Submit button not found")
                
                logger.info("Search button clicked, waiting for results...")
                
                # Wait for results
                await asyncio.sleep(5)
                
                # Parse results table
                rows = await page.query_selector_all("table.views-table tbody tr")
                logger.info(f"Found {len(rows)} table rows")
                
                for row in rows:
                    case = await self._parse_row(row)
                    if case:
                        cases.append(case)
                
                logger.info(f"Total cases parsed: {len(cases)}")
                        
            except Exception as e:
                logger.error(f"Scraping failed: {str(e)}")
                raise RuntimeError(f"Scraping failed: {str(e)}")
            finally:
                await browser.close()
                logger.info("Browser closed")
        
        return cases
    
    async def _parse_row(self, row) -> LitigationCase | None:
        """Parse table row into LitigationCase"""
        try:
            cells = await row.query_selector_all("td")
            
            if len(cells) >= 3:
                texts = []
                for cell in cells:
                    text = await cell.inner_text()
                    texts.append(text.strip())
                
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
