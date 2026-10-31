import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class AUJobsScraper(BaseScraper):
    """Scraper for African Union (AU) Jobs Portal (jobs.au.int)."""

    def __init__(self, proxies: Optional[List[str]] = None):
        super().__init__(proxies=proxies)
        self.base_url = "https://jobs.au.int/search/?q=&searchResultView=LIST"

    def scrape(
        self,
        search_term: str = "",
        location: str = "",
        results_wanted: int = 10,
        **kwargs
    ) -> List[JobPost]:
        jobs: List[JobPost] = []
        url = f"https://jobs.au.int/search/?q={search_term}&searchResultView=LIST" if search_term else self.base_url
        resp = self._safe_get(url)
        if not resp:
            return jobs

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select("tr.data-row, div.job-tile, .searchResults-row, tr[id^='row'], li.job-item, a[href*='/job/']")
        seen_urls = set()

        for card in cards:
            link = card if card.name == "a" else card.find("a", href=True)
            if not link:
                continue
            job_url = link.get("href", "")
            title = link.get_text(strip=True)
            if not job_url or len(title) < 5 or "/job/" not in job_url:
                continue
            if any(skip in title.lower() for skip in ["home", "login", "register", "about", "faq", "search"]):
                continue

            if not job_url.startswith("http"):
                job_url = f"https://jobs.au.int{job_url}" if job_url.startswith("/") else f"https://jobs.au.int/{job_url}"
            job_url = job_url.split("?")[0]
            if job_url in seen_urls:
                continue
            seen_urls.add(job_url)

            if search_term and search_term.lower() not in title.lower():
                continue

            job_loc = location or "Pan-African"
            loc_elem = card.select_one(".jobLocation, .location, span.col")
            if loc_elem:
                l_text = loc_elem.get_text(strip=True)
                if l_text and len(l_text) < 50:
                    job_loc = l_text

            jobs.append(JobPost(
                title=self._clean_text(title),
                company="African Union (AU)",
                country="Pan-African",
                location=self._clean_text(job_loc),
                site_name="au_jobs",
                job_url=job_url
            ))
            if len(jobs) >= results_wanted:
                break

        return jobs
