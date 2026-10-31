import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class DerejaScraper(BaseScraper):
    """Scraper for Dereja Portal (dereja.com/jobs)."""

    def __init__(self, proxies: Optional[List[str]] = None):
        super().__init__(proxies=proxies)
        self.base_url = "https://dereja.com/jobs"

    def scrape(
        self,
        search_term: str = "",
        location: str = "",
        results_wanted: int = 10,
        **kwargs
    ) -> List[JobPost]:
        jobs: List[JobPost] = []
        resp = self._safe_get(self.base_url, params={"title": search_term} if search_term else None)
        if not resp:
            return jobs

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select("div.job-item, article, div.card, a[href*='/job'], div.listings")
        seen_urls = set()

        for card in cards:
            link = card if card.name == "a" else card.find("a", href=True)
            if not link:
                continue
            job_url = link.get("href", "")
            title = link.get_text(strip=True)
            if not job_url or len(title) < 5 or any(s in title.lower() for s in ["home", "login", "register", "about"]):
                continue

            if not job_url.startswith("http"):
                job_url = f"https://dereja.com{job_url}" if job_url.startswith("/") else f"https://dereja.com/{job_url}"
            job_url = job_url.split("?")[0]
            if job_url in seen_urls:
                continue
            seen_urls.add(job_url)

            if search_term and search_term.lower() not in title.lower():
                continue

            jobs.append(JobPost(
                title=self._clean_text(title),
                company="Dereja Partner",
                country="Ethiopia",
                location=location or "Ethiopia",
                site_name="dereja",
                job_url=job_url
            ))
            if len(jobs) >= results_wanted:
                break

        return jobs
