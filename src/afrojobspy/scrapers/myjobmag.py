import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class MyJobMagScraper(BaseScraper):
    """Scraper for MyJobMag (Nigeria, Kenya, Ghana, South Africa)."""

    def __init__(self, proxies: Optional[List[str]] = None, country_code: str = "ng"):
        super().__init__(proxies=proxies)
        self.country_code = country_code.lower()
        if self.country_code == "ke":
            self.base_url = "https://www.myjobmag.co.ke/search/jobs"
            self.country = "Kenya"
        elif self.country_code == "gh":
            self.base_url = "https://www.myjobmag.com.gh/search/jobs"
            self.country = "Ghana"
        elif self.country_code == "za":
            self.base_url = "https://www.myjobmag.co.za/search/jobs"
            self.country = "South Africa"
        else:
            self.base_url = "https://www.myjobmag.com/search/jobs"
            self.country = "Nigeria"

    def scrape(
        self,
        search_term: str = "",
        location: str = "",
        results_wanted: int = 10,
        **kwargs
    ) -> List[JobPost]:
        jobs: List[JobPost] = []
        params = {"q": search_term} if search_term else {}
        resp = self._safe_get(self.base_url, params=params)
        if not resp:
            return jobs

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select("li.job-info, div.job-info, li.mag-b, li[class*='job']")
        seen_urls = set()

        for card in cards:
            link = card.select_one("h2 a, h3 a, a[href*='/job/']")
            if not link:
                continue
            job_url = link.get("href", "")
            title = link.get_text(strip=True)
            if not job_url or len(title) < 4:
                continue

            if not job_url.startswith("http"):
                prefix = self.base_url.split("/search")[0]
                job_url = prefix + job_url if job_url.startswith("/") else f"{prefix}/{job_url}"
            job_url = job_url.split("?")[0]
            if job_url in seen_urls:
                continue
            seen_urls.add(job_url)

            if search_term and search_term.lower() not in title.lower():
                continue

            company = "MyJobMag Employer"
            comp_elem = card.select_one("a[href*='/jobs-at/'], .company, .employer")
            if comp_elem:
                c_text = comp_elem.get_text(strip=True)
                if c_text and len(c_text) < 60:
                    company = c_text

            jobs.append(JobPost(
                title=self._clean_text(title),
                company=self._clean_text(company),
                country=self.country,
                location=location or self.country,
                site_name="myjobmag",
                job_url=job_url
            ))
            if len(jobs) >= results_wanted:
                break

        return jobs
