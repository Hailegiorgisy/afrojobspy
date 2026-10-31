import json
import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class EthiojobsScraper(BaseScraper):
    """Scraper for Ethiojobs (ethiojobs.net), extracting via Next.js hydration or HTML."""

    def __init__(self, proxies: Optional[List[str]] = None):
        super().__init__(proxies=proxies)
        self.base_url = "https://www.ethiojobs.net/browse-jobs"

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
                params["search"] = search_term
            if page > 1:
                params["page"] = page

            resp = self._safe_get(self.base_url, params=params)
            if not resp:
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            
            # 1. Try Next.js __NEXT_DATA__
            next_tag = soup.find("script", id="__NEXT_DATA__")
            page_jobs_found = 0
            if next_tag and next_tag.string:
                try:
                    data = json.loads(next_tag.string)
                    props = data.get("props", {}).get("pageProps", {})
                    job_items = props.get("jobs", []) or props.get("data", []) or props.get("listings", [])
                    for item in job_items:
                        title = item.get("title") or item.get("job_title") or item.get("position")
                        if not title:
                            continue
                        job_id = item.get("id") or item.get("_id") or item.get("slug")
                        job_url = f"https://www.ethiojobs.net/jobs/{job_id}" if job_id else self.base_url
                        if job_url in seen_urls:
                            continue
                        seen_urls.add(job_url)

                        company = item.get("company", {})
                        company_name = company.get("name") if isinstance(company, dict) else (company or "N/A")
                        job_loc = item.get("location") or location or "Ethiopia"
                        
                        jobs.append(JobPost(
                            title=self._clean_text(title),
                            company=self._clean_text(company_name),
                            country="Ethiopia",
                            city=self._clean_text(job_loc),
                            location=self._clean_text(job_loc),
                            site_name="ethiojobs",
                            job_url=job_url,
                            description=item.get("summary") or item.get("description"),
                            deadline=item.get("deadline") or item.get("expiry_date"),
                            date_posted=item.get("created_at") or item.get("posted_at")
                        ))
                        page_jobs_found += 1
                        if len(jobs) >= results_wanted:
                            break
                except Exception as e:
                    logger.debug(f"[Ethiojobs] Next.js hydration extraction error: {e}")

            # 2. HTML Fallback
            if page_jobs_found == 0:
                cards = soup.select("div.job-item, div.listing-item, div.card, article, a[href*='/jobs/']")
                for card in cards:
                    link = card if card.name == "a" else card.find("a", href=True)
                    if not link:
                        continue
                    job_url = link.get("href", "")
                    title = link.get_text(strip=True)
                    if not job_url or len(title) < 4 or any(skip in title.lower() for skip in ["home", "login", "register", "about", "terms"]):
                        continue
                    if not job_url.startswith("http"):
                        job_url = f"https://www.ethiojobs.net{job_url}" if job_url.startswith("/") else f"https://www.ethiojobs.net/{job_url}"
                    if job_url in seen_urls:
                        continue
                    seen_urls.add(job_url)

                    if search_term and search_term.lower() not in title.lower():
                        continue

                    company_elem = card.select_one(".company-name, .employer, .company") if card.name != "a" else None
                    company = company_elem.get_text(strip=True) if company_elem else "N/A"

                    jobs.append(JobPost(
                        title=self._clean_text(title),
                        company=self._clean_text(company),
                        country="Ethiopia",
                        location=location or "Ethiopia",
                        site_name="ethiojobs",
                        job_url=job_url
                    ))
                    page_jobs_found += 1
                    if len(jobs) >= results_wanted:
                        break

            if page_jobs_found == 0:
                break
            page += 1

        return jobs
