import logging
from typing import List
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class UNJobsScraper(BaseScraper):
    """
    Scraper implementation for UNJobs (unjobs.org).
    """
    def __init__(self, proxies=None):
        super().__init__(proxies=proxies)
        self.base_url = "https://unjobs.org/search"

    def scrape(self, search_term: str, location: str, results_wanted: int) -> List[JobPost]:
        jobs: List[JobPost] = []
        params = {"q": search_term}
        if location:
            params["loc"] = location

        try:
            response = self.session.get(self.base_url, params=params, timeout=10)
            if response.status_code != 200:
                return jobs
            
            soup = BeautifulSoup(response.text, "html.parser")
            job_links = [a for a in soup.find_all("a", href=True) if "/vacancy/" in a["href"] or "/jobs/" in a["href"]]

            for a in job_links:
                if len(jobs) >= results_wanted:
                    break
                job_url = a["href"]
                if not job_url.startswith("http"):
                    job_url = "https://unjobs.org" + job_url
                
                title = a.text.strip()
                if not title or len(title) < 4:
                    continue
                
                job_id = job_url.split("/")[-1] or "unknown"
                if any(j.job_url == job_url for j in jobs):
                    continue

                jobs.append(JobPost(
                    id=job_id,
                    title=title,
                    company="United Nations / International Org",
                    location=location or "Africa / Global",
                    site_name="unjobs",
                    job_url=job_url
                ))
        except Exception as e:
            logger.error(f"UNJobs scrape error: {e}")
            
        return jobs