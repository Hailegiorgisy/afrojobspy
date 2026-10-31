import json
import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class AfriworkScraper(BaseScraper):
    """Scraper for Afriwork Ethiopia (afriworket.com)."""

    def __init__(self, proxies: Optional[List[str]] = None):
        super().__init__(proxies=proxies)
        self.base_url = "https://afriworket.com/jobs"

    def scrape(
        self,
        search_term: str = "",
        location: str = "",
        results_wanted: int = 10,
        **kwargs
    ) -> List[JobPost]:
        jobs: List[JobPost] = []
        resp = self._safe_get(self.base_url, params={"q": search_term} if search_term else None)
        if not resp:
            return jobs

        soup = BeautifulSoup(resp.text, "html.parser")
        seen_urls = set()

        # 1. Try Next.js __NEXT_DATA__
        script_tag = soup.find("script", id="__NEXT_DATA__")
        if script_tag and script_tag.string:
            try:
                data = json.loads(script_tag.string)
                page_props = data.get("props", {}).get("pageProps", {})
                job_list = page_props.get("jobs", []) or page_props.get("listings", []) or page_props.get("vacancies", [])
                
                if not job_list:
                    for k, v in page_props.items():
                        if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                            if any(f in v[0] for f in ["title", "job_title", "position"]):
                                job_list = v
                                break

                for item in job_list:
                    title = item.get("title") or item.get("job_title") or item.get("position", "")
                    if not title:
                        continue
                    if search_term and search_term.lower() not in title.lower():
                        continue

                    job_id = item.get("id") or item.get("_id", "")
                    job_url = item.get("url") or (f"https://afriworket.com/jobs/{job_id}" if job_id else self.base_url)
                    if job_url in seen_urls:
                        continue
                    seen_urls.add(job_url)

                    comp_obj = item.get("company")
                    company = comp_obj.get("name") if isinstance(comp_obj, dict) else (comp_obj or "Afriwork Partner")
                    loc = item.get("location") or location or "Addis Ababa, Ethiopia"

                    jobs.append(JobPost(
                        title=self._clean_text(title),
                        company=self._clean_text(company),
                        country="Ethiopia",
                        location=self._clean_text(loc),
                        site_name="afriwork",
                        job_url=job_url,
                        description=item.get("description")
                    ))
                    if len(jobs) >= results_wanted:
                        return jobs
            except Exception as e:
                logger.debug(f"[Afriwork] JSON hydration error: {e}")

        # 2. HTML fallback
        if not jobs:
            cards = soup.select("a[href*='/jobs/'], div.job-card, article")
            for card in cards:
                link = card if card.name == "a" else card.find("a")
                if not link:
                    continue
                job_url = link.get("href", "")
                title = link.get_text(strip=True)
                if not title or len(title) < 4 or "/jobs/" not in job_url:
                    continue
                if not job_url.startswith("http"):
                    job_url = f"https://afriworket.com{job_url}" if job_url.startswith("/") else f"https://afriworket.com/{job_url}"
                if job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                if search_term and search_term.lower() not in title.lower():
                    continue

                jobs.append(JobPost(
                    title=self._clean_text(title),
                    company="Afriwork Partner",
                    country="Ethiopia",
                    location=location or "Addis Ababa, Ethiopia",
                    site_name="afriwork",
                    job_url=job_url
                ))
                if len(jobs) >= results_wanted:
                    break

        return jobs
