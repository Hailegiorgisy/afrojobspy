import requests
from abc import ABC, abstractmethod
from typing import List, Optional
from afrojobspy.models import JobPost

class BaseScraper(ABC):
    """
    Abstract Base Class for all African job board scrapers.
    Handles session initialization, default headers, and proxies.
    """
    def __init__(self, proxies: Optional[List[str]] = None):
        self.session = requests.Session()
        # Spoof a modern browser User-Agent to avoid immediate blocks
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        })
        self.proxies = proxies

    @abstractmethod
    def scrape(self, search_term: str, location: str, results_wanted: int) -> List[JobPost]:
        """
        Every child scraper must implement this method to parse its specific site.
        """
        pass