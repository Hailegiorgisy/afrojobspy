import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class HahuJobsScraper(BaseScraper):
    """Scraper for HaHuJobs Ethiopia"""
    def __init__(self, proxies: Optional[List[str]] = None):
        super().__init__(proxies=proxies)
        self.base_url = "https://www.hahu.jobs/jobs"

    def scrape(self, search_term: str = "", location: str = "", results_wanted: int = 10) -> List[JobPost]:
        jobs = []
        try:
            response = self.session.get(self.base_url, timeout=15)
            if response.status_code != 200:
                return jobs
            
            soup = BeautifulSoup(response.text, "html.parser")
            cards = soup.select(".job-card, article, .card")
            
            for card in cards[:results_wanted]:
                title_elem = card.find("a")
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                job_url = title_elem.get("href", "")
                if job_url and not job_url.startswith("http"):
                    job_url = "https://www.hahu.jobs" + job_url

                jobs.append(JobPost(
                    title=title,
                    company="HaHuJobs Employer",
                    location=location or "Ethiopia",
                    site_name="hahujobs",
                    job_url=job_url
                ))
        except Exception as e:
            logger.error(f"HaHuJobs scrape error: {e}")
        return jobs