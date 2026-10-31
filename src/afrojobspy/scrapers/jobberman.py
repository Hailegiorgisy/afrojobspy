import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class JobbermanScraper(BaseScraper):
    """Scraper for Jobberman (West Africa - Nigeria / Ghana)."""

    def __init__(self, proxies: Optional[List[str]] = None, country_code: str = "ng"):
        super().__init__(proxies=proxies)
        self.country_code = country_code.lower()
        domain = "com.gh" if self.country_code == "gh" else "com"
        self.base_url = f"https://www.jobberman.{domain}/jobs"

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
                params["q"] = search_term
            if page > 1:
                params["page"] = page

            resp = self._safe_get(self.base_url, params=params)
            if not resp:
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select("div.search-result-item, div.job-card, article, div.panel")
            found_on_page = 0

            for card in cards:
                link = card.find("a", href=True)
                if not link:
                    continue
                job_url = link.get("href", "")
                if not job_url or "/listings/" not in job_url:
                    continue

                title_elem = card.select_one("h3, h2, a.text-loading, .job-title")
                title = title_elem.get_text(strip=True) if title_elem else link.get_text(strip=True)
                if not title or len(title) < 4:
                    continue

                domain = "com.gh" if self.country_code == "gh" else "com"
                if not job_url.startswith("http"):
                    job_url = f"https://www.jobberman.{domain}{job_url}" if job_url.startswith("/") else f"https://www.jobberman.{domain}/{job_url}"
                job_url = job_url.split("?")[0]
                if job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                if search_term and search_term.lower() not in title.lower():
                    continue

                company = "Jobberman Employer"
                comp_elem = card.select_one(".text-gray-500, .job-company, span.text-sm")
                if comp_elem:
                    c_text = comp_elem.get_text(strip=True)
                    if c_text and len(c_text) < 60 and "ago" not in c_text.lower():
                        company = c_text

                country_name = "Ghana" if self.country_code == "gh" else "Nigeria"
                jobs.append(JobPost(
                    title=self._clean_text(title),
                    company=self._clean_text(company),
                    country=country_name,
                    location=location or country_name,
                    site_name="jobberman",
                    job_url=job_url
                ))
                found_on_page += 1
                if len(jobs) >= results_wanted:
                    break

            if found_on_page == 0:
                break
            page += 1

        return jobs
