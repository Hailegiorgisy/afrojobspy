import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class HahuJobsScraper(BaseScraper):
    """Scraper for HaHuJobs Ethiopia (hahu.jobs)."""

    def __init__(self, proxies: Optional[List[str]] = None):
        super().__init__(proxies=proxies)
        self.base_url = "https://www.hahu.jobs/jobs"

    def scrape(
        self,
        search_term: str = "",
        location: str = "",
        results_wanted: int = 10,
        **kwargs
    ) -> List[JobPost]:
        jobs: List[JobPost] = []
        params = {"query": search_term} if search_term else {}
        resp = self._safe_get(self.base_url, params=params)
        if not resp:
            return jobs

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select("div.card, article, div.job-card, .search-result-item, a[href*='/jobs/']")
        seen_urls = set()

        for card in cards:
            link = card if card.name == "a" else card.find("a", href=True)
            if not link:
                continue
            job_url = link.get("href", "")
            title = link.get_text(strip=True)
            if not job_url or len(title) < 5 or any(s in title.lower() for s in ["home", "login", "register", "about", "contact"]):
                continue

            if not job_url.startswith("http"):
                job_url = f"https://www.hahu.jobs{job_url}" if job_url.startswith("/") else f"https://www.hahu.jobs/{job_url}"
            job_url = job_url.split("?")[0]
            if job_url in seen_urls:
                continue
            seen_urls.add(job_url)

            if search_term and search_term.lower() not in title.lower():
                continue

            company = "HaHuJobs Employer"
            if card.name != "a":
                comp_elem = card.select_one(".company-name, .employer, h4, h5")
                if comp_elem:
                    c_text = comp_elem.get_text(strip=True)
                    if c_text and len(c_text) < 60:
                        company = c_text

            jobs.append(JobPost(
                title=self._clean_text(title),
                company=self._clean_text(company),
                country="Ethiopia",
                location=location or "Ethiopia",
                site_name="hahujobs",
                job_url=job_url
            ))
            if len(jobs) >= results_wanted:
                break

        return jobs
