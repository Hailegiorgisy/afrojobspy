import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class FuzuScraper(BaseScraper):
    """Scraper for Fuzu (fuzu.com) - leading career platform in East Africa (Kenya, Uganda, etc.)."""

    def __init__(self, proxies: Optional[List[str]] = None):
        super().__init__(proxies=proxies)
        self.base_url = "https://www.fuzu.com/jobs"

    def scrape(
        self,
        search_term: str = "",
        location: str = "",
        results_wanted: int = 10,
        **kwargs
    ) -> List[JobPost]:
        jobs: List[JobPost] = []
        params = {}
        if search_term:
            params["title"] = search_term

        resp = self._safe_get(self.base_url, params=params)
        if not resp:
            return jobs

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select("div.job-card, article, div.JobCard, a[href*='/job/'], a[href*='/jobs/']")
        seen_urls = set()

        for card in cards:
            link = card if card.name == "a" else card.find("a", href=True)
            if not link:
                continue
            job_url = link.get("href", "")
            if not job_url or ("/job/" not in job_url and "/jobs/" not in job_url):
                continue

            title_elem = card.select_one("h2, h3, h4, .title") if card.name != "a" else link
            title = title_elem.get_text(strip=True) if title_elem else link.get_text(strip=True)
            if not title or len(title) < 4:
                continue

            if not job_url.startswith("http"):
                job_url = f"https://www.fuzu.com{job_url}" if job_url.startswith("/") else f"https://www.fuzu.com/{job_url}"
            job_url = job_url.split("?")[0]
            if job_url in seen_urls:
                continue
            seen_urls.add(job_url)

            if search_term and search_term.lower() not in title.lower():
                continue

            company = "Fuzu Partner"
            if card.name != "a":
                comp_elem = card.select_one(".company, .company-name, .employer, span.text-muted")
                if comp_elem:
                    c_text = comp_elem.get_text(strip=True)
                    if c_text and len(c_text) < 60:
                        company = c_text

            jobs.append(JobPost(
                title=self._clean_text(title),
                company=self._clean_text(company),
                country="Kenya",
                location=location or "East Africa",
                site_name="fuzu",
                job_url=job_url
            ))
            if len(jobs) >= results_wanted:
                break

        return jobs
