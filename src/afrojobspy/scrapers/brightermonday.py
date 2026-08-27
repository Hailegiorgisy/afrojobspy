import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class BrighterMondayScraper(BaseScraper):
    """Scraper for BrighterMonday (East Africa)"""
    def __init__(self, proxies: Optional[List[str]] = None):
        super().__init__(proxies=proxies)
        self.base_url = "https://www.brightermonday.co.ke/jobs"

    def scrape(self, search_term: str = "", location: str = "", results_wanted: int = 10) -> List[JobPost]:
        jobs = []
        try:
            response = self.session.get(self.base_url, timeout=15)
            if response.status_code != 200:
                return jobs
            
            soup = BeautifulSoup(response.text, "html.parser")
            cards = soup.select("div.card, div[data-cy='job-card']")
            
            for card in cards[:results_wanted]:
                title_elem = card.select_one("a.text-lg, h3 a, a.job-title")
                company_elem = card.select_one(".text-sm.text-gray-500, .company-name")
                
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                job_url = title_elem.get("href", "")
                company = company_elem.get_text(strip=True) if company_elem else "BrighterMonday Employer"

                if search_term and search_term.lower() not in title.lower():
                    continue

                jobs.append(JobPost(
                    title=title,
                    company=company,
                    location=location or "Kenya / East Africa",
                    site_name="brightermonday",
                    job_url=job_url
                ))
        except Exception as e:
            logger.error(f"BrighterMonday scrape error: {e}")
        return jobs