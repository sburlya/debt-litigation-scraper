"""
URL Builder for instante.justice.md search queries
"""
from urllib.parse import urlencode, quote
from typing import Optional
from .models import CaseType, CourtInstance


class URLBuilder:
    """Builds search URLs for instante.justice.md"""

    BASE_URL = "https://instante.justice.md/ro/hotaririle-instantei"

    def __init__(
        self,
        denumirea_dosarului: str,
        tipul_dosarului: CaseType = CaseType.CONTRAVENTIONAL,
        instance: CourtInstance = CourtInstance.ALL,
        numarul_dosarului: Optional[str] = None,
        data_pronuntarii: Optional[str] = None,
        tematica_dosarului: Optional[str] = None,
    ):
        self.denumirea_dosarului = denumirea_dosarului
        self.tipul_dosarului = tipul_dosarului
        self.instance = instance
        self.numarul_dosarului = numarul_dosarului
        self.data_pronuntarii = data_pronuntarii
        self.tematica_dosarului = tematica_dosarului

    def build(self, page: int = 0) -> str:
        """
        Build search URL with all parameters.

        Args:
            page: Page number (0-indexed, site uses 'page' param)

        Returns:
            Complete URL string for the search query
        """
        params = {
            "Instance": self.instance.value,
            "Numarul_dosarului": self.numarul_dosarului or "",
            "Denumirea_dosarului": self.denumirea_dosarului,
            "date": self.data_pronuntarii or "",
            "Tematica_dosarului": self.tematica_dosarului or "",
            "Tipul_dosarului": self.tipul_dosarului.value,
        }

        # Add pagination if not first page
        if page > 0:
            params["page"] = str(page)

        # Build query string
        query_string = urlencode(params, quote_via=quote)

        return f"{self.BASE_URL}?{query_string}"

    def get_filters_dict(self) -> dict:
        """Return applied filters as dictionary for response metadata"""
        return {
            "denumirea_dosarului": self.denumirea_dosarului,
            "tipul_dosarului": self.tipul_dosarului.value,
            "instance": self.instance.value,
            "numarul_dosarului": self.numarul_dosarului,
            "data_pronuntarii": self.data_pronuntarii,
        }

    @classmethod
    def from_request(cls, request) -> "URLBuilder":
        """
        Factory method to create URLBuilder from ScrapeRequest.

        Args:
            request: ScrapeRequest pydantic model

        Returns:
            Configured URLBuilder instance
        """
        return cls(
            denumirea_dosarului=request.denumirea_dosarului,
            tipul_dosarului=request.tipul_dosarului,
            instance=request.instance,
            numarul_dosarului=request.numarul_dosarului,
            data_pronuntarii=request.data_pronuntarii,
        )


# PDF URL utilities
PDF_BASE_URL = "https://instante.justice.md/ro/pigd_integration/pdf"


def extract_pdf_id(pdf_url: str) -> Optional[str]:
    """
    Extract GUID from PDF URL.

    Args:
        pdf_url: Full PDF URL or just the GUID

    Returns:
        GUID string or None if invalid
    """
    if not pdf_url:
        return None

    # Handle full URL
    if PDF_BASE_URL in pdf_url:
        return pdf_url.split("/")[-1]

    # Handle relative URL or just GUID
    if "/" in pdf_url:
        return pdf_url.split("/")[-1]

    # Assume it's already a GUID
    return pdf_url


def build_pdf_url(pdf_id: str) -> str:
    """
    Build full PDF URL from GUID.

    Args:
        pdf_id: PDF document GUID

    Returns:
        Complete PDF URL
    """
    return f"{PDF_BASE_URL}/{pdf_id}"
