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
        
        # Build direct URL with search parameter
        from urllib.parse import quote
        search_url = f"{self.BASE_URL}?filter_implicat={quote(company_name)}"
        
        logger.info(f"Starting search for: {company_name}")
        logger.info(f"Direct URL: {search_url}")
        
        async with async_playwright() as p:
            logger.info("Launching browser...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                logger.info(f"Navigating to {search_url}")
                await page.goto(search_url, wait_until="networkidle", timeout=30000)
                logger.info("Page loaded")
                
                # Wait for table to appear
                await asyncio.sleep(3)
                
                # Log HTML to see what we got
                html = await page.content()
                
                # Check if table exists in HTML
                if "views-table" in html:
                    logger.info("Table class 'views-table' FOUND in HTML")
                else:
                    logger.info("Table class 'views-table' NOT FOUND in HTML")
                
                # Log relevant HTML snippet
                import re
                table_match = re.search(r'<table[^>]*class="[^"]*views-table[^"]*"[^>]*>.*?</table>', html, re.DOTALL)
                if table_match:
                    logger.info(f"Table HTML (first 500 chars): {table_match.group(0)[:500]}")
                else:
                    # Log body content
                    body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
                    if body_match:
                        logger.info(f"Body HTML (first 1000 chars): {body_match.group(1)[:1000]}")
                
                # Log current URL
                current_url = page.url
                logger.info(f"Current URL: {current_url}")
                
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
