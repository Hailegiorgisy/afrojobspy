import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class GeezJobsScraper(BaseScraper):
    """Scraper for GeezJobs Ethiopia"""
    def __init__(self, proxies: Optional[List[str]] = None):
        super().__init__(proxies=proxies)
        self.base_url = "https://geezjobs.com/"

    def scrape(self, search_term: str = "", location: str = "", results_wanted: int = 10) -> List[JobPost]:
        jobs = []
        try:
            response = self.session.get(self.base_url, timeout=15)
            if response.status_code != 200:
                return jobs
            
            soup = BeautifulSoup(response.text, "html.parser")
            listings = soup.select("a.job-link, h3 a, .featured-vacancy a")
            
            for item in listings[:results_wanted]:
                title = item.get_text(strip=True)
                job_url = item.get("href", "")
                if job_url and not job_url.startswith("http"):
                    job_url = "https://geezjobs.com" + job_url

                if not title:
                    continue

                jobs.append(JobPost(
                    title=title,
                    company="GeezJobs Employer",
                    location=location or "Ethiopia",
                    site_name="geezjobs",
                    job_url=job_url
                ))
        except Exception as e:
            logger.error(f"GeezJobs scrape error: {e}")
        return jobs