import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class GeezJobsScraper(BaseScraper):
    """Scraper for GeezJobs Ethiopia (geezjobs.com)."""

    def __init__(self, proxies: Optional[List[str]] = None):
        super().__init__(proxies=proxies)
        self.base_url = "https://geezjobs.com/"

    def scrape(
        self,
        search_term: str = "",
        location: str = "",
        results_wanted: int = 10,
        **kwargs
    ) -> List[JobPost]:
        jobs: List[JobPost] = []
        resp = self._safe_get(self.base_url, params={"s": search_term} if search_term else None)
        if not resp:
            return jobs

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select("div.job-card, div.vacancy-item, a.job-link, .featured-vacancy a, h3 a, h4 a")
        seen_urls = set()

        for card in cards:
            link = card if card.name == "a" else card.find("a", href=True)
            if not link:
                continue
            title = link.get_text(strip=True)
            job_url = link.get("href", "")
            if not title or len(title) < 5 or any(s in title.lower() for s in ["jobs", "post a job", "login", "register"]):
                continue
            if not job_url or "job" not in job_url.lower():
                continue

            if not job_url.startswith("http"):
                job_url = f"https://geezjobs.com{job_url}" if job_url.startswith("/") else f"https://geezjobs.com/{job_url}"
            if job_url in seen_urls:
                continue
            seen_urls.add(job_url)

            if search_term and search_term.lower() not in title.lower():
                continue

            jobs.append(JobPost(
                title=self._clean_text(title),
                company="GeezJobs Employer",
                country="Ethiopia",
                location=location or "Addis Ababa, Ethiopia",
                site_name="geezjobs",
                job_url=job_url
            ))
            if len(jobs) >= results_wanted:
                break

        return jobs
