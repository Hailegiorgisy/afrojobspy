import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class AUJobsScraper(BaseScraper):
    """Scraper for African Union Jobs (jobs.au.int)"""
    def __init__(self, proxies: Optional[List[str]] = None):
        super().__init__(proxies=proxies)
        self.base_url = "https://jobs.au.int/viewalljobs/"

    def scrape(self, search_term: str = "", location: str = "", results_wanted: int = 10) -> List[JobPost]:
        jobs = []
        try:
            response = self.session.get(self.base_url, timeout=15)
            if response.status_code != 200:
                return jobs
            
            soup = BeautifulSoup(response.text, "html.parser")
            # SAP SuccessFactors backend structure used by AU Jobs typically renders rows or list items
            rows = soup.find_all("tr", class_="dataRow") or soup.select(".job-result-item, .card")
            
            for row in rows[:results_wanted]:
                title_elem = row.find("a")
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                job_url = title_elem.get("href", "")
                if job_url and not job_url.startswith("http"):
                    job_url = "https://jobs.au.int" + job_url

                if search_term and search_term.lower() not in title.lower():
                    continue

                jobs.append(JobPost(
                    title=title,
                    company="African Union",
                    location=location or "Addis Ababa",
                    site_name="au_jobs",
                    job_url=job_url
                ))
        except Exception as e:
            logger.error(f"AU Jobs scrape error: {e}")
        return jobs