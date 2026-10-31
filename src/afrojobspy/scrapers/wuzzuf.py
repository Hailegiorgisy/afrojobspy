import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class WuzzufScraper(BaseScraper):
    """Scraper for Wuzzuf (Egypt / North Africa)."""

    def __init__(self, proxies: Optional[List[str]] = None):
        super().__init__(proxies=proxies)
        self.base_url = "https://wuzzuf.net/search/jobs/"

    def scrape(
        self,
        search_term: str = "",
        location: str = "",
        results_wanted: int = 10,
        **kwargs
    ) -> List[JobPost]:
        jobs: List[JobPost] = []
        page = 0
        seen_urls = set()

        while len(jobs) < results_wanted and page <= 5:
            params = {"a": "hpb"}
            if search_term:
                params["q"] = search_term
            if page > 0:
                params["start"] = page

            resp = self._safe_get(self.base_url, params=params)
            if not resp:
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select("div.css-1gatmva, div.job-card, div[data-qa='job-card']")
            found_on_page = 0

            for card in cards:
                link = card.select_one("a.css-o171kl, h2.css-m604qf a, a[href*='/jobs/']")
                if not link:
                    link = card.find("a", href=True)
                if not link:
                    continue

                job_url = link.get("href", "")
                title = link.get_text(strip=True)
                if not job_url or not title or len(title) < 4 or "/jobs/" not in job_url:
                    continue

                if not job_url.startswith("http"):
                    job_url = "https://wuzzuf.net" + job_url if job_url.startswith("/") else f"https://wuzzuf.net/{job_url}"
                job_url = job_url.split("?")[0]
                if job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                if search_term and search_term.lower() not in title.lower():
                    continue

                company = "Wuzzuf Employer"
                comp_elem = card.select_one("a.css-17s97ql, .company-name")
                if comp_elem:
                    c_text = comp_elem.get_text(strip=True)
                    if c_text and len(c_text) < 50:
                        company = c_text

                jobs.append(JobPost(
                    title=self._clean_text(title),
                    company=self._clean_text(company),
                    country="Egypt",
                    location=location or "Egypt",
                    site_name="wuzzuf",
                    job_url=job_url
                ))
                found_on_page += 1
                if len(jobs) >= results_wanted:
                    break

            if found_on_page == 0:
                break
            page += 1

        return jobs
