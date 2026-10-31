import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class CareerJunctionScraper(BaseScraper):
    """Scraper for CareerJunction (South Africa)."""

    def __init__(self, proxies: Optional[List[str]] = None):
        super().__init__(proxies=proxies)
        self.base_url = "https://www.careerjunction.co.za/jobs"

    def scrape(
        self,
        search_term: str = "",
        location: str = "",
        results_wanted: int = 10,
        **kwargs
    ) -> List[JobPost]:
        jobs: List[JobPost] = []
        page = 1
        seen_urls = set()

        while len(jobs) < results_wanted and page <= 5:
            params = {}
            if search_term:
                params["keywords"] = search_term
            if location:
                params["location"] = location
            if page > 1:
                params["page"] = page

            resp = self._safe_get(self.base_url, params=params)
            if not resp:
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select("div.job-card, div.module-job, article, div.results-item")
            found_on_page = 0

            for card in cards:
                link = card.find("a", href=True)
                if not link:
                    continue
                job_url = link.get("href", "")
                if not job_url or "/jobs/" not in job_url:
                    continue

                title_elem = card.select_one("h2, h3, .job-title, a")
                title = title_elem.get_text(strip=True) if title_elem else link.get_text(strip=True)
                if not title or len(title) < 4:
                    continue
                if any(skip in title.lower() for skip in ["home", "login", "register", "about", "contact", "privacy", "terms"]):
                    continue

                if not job_url.startswith("http"):
                    job_url = "https://www.careerjunction.co.za" + job_url if job_url.startswith("/") else f"https://www.careerjunction.co.za/{job_url}"
                job_url = job_url.split("?")[0]
                if job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                if search_term and search_term.lower() not in title.lower():
                    continue

                company = "CareerJunction Partner"
                comp_elem = card.select_one(".company-name, .job-company")
                if comp_elem:
                    c_text = comp_elem.get_text(strip=True)
                    if c_text and len(c_text) < 50:
                        company = c_text

                jobs.append(JobPost(
                    title=self._clean_text(title),
                    company=self._clean_text(company),
                    country="South Africa",
                    location=location or "South Africa",
                    site_name="careerjunction",
                    job_url=job_url
                ))
                found_on_page += 1
                if len(jobs) >= results_wanted:
                    break

            if found_on_page == 0:
                break
            page += 1

        return jobs
