import json
import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class AfriworkScraper(BaseScraper):
    """Scraper for Afriwork Ethiopia"""
    def __init__(self, proxies: Optional[List[str]] = None):
        super().__init__(proxies=proxies)
        self.base_url = "https://afriworket.com/jobs"
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        })

    def scrape(self, search_term: str = "", location: str = "", results_wanted: int = 10) -> List[JobPost]:
        jobs = []
        try:
            response = self.session.get(self.base_url, timeout=15)
            if response.status_code != 200:
                return jobs
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 1. Try extracting Next.js hydration data if present
            script_tag = soup.find("script", id="__NEXT_DATA__")
            if script_tag and script_tag.string:
                try:
                    data = json.loads(script_tag.string)
                    page_props = data.get("props", {}).get("pageProps", {})
                    
                    job_list = (
                        page_props.get("jobs", []) or 
                        page_props.get("listings", []) or 
                        page_props.get("vacancies", [])
                    )
                    
                    if not job_list:
                        for k, v in page_props.items():
                            if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                                if any(field in v[0] for field in ["title", "job_title", "position"]):
                                    job_list = v
                                    break

                    for item in job_list[:results_wanted]:
                        title = item.get("title") or item.get("job_title") or item.get("position", "")
                        if not title:
                            continue
                        
                        job_id = item.get("id") or item.get("_id", "")
                        job_url = item.get("url") or (f"https://afriworket.com/jobs/{job_id}" if job_id else self.base_url)
                        
                        company_obj = item.get("company")
                        company = company_obj.get("name") if isinstance(company_obj, dict) else (company_obj or "Afriwork Partner")

                        if search_term and search_term.lower() not in title.lower():
                            continue

                        jobs.append(JobPost(
                            title=title,
                            company=company,
                            location=location or item.get("location", "Addis Ababa, Ethiopia"),
                            site_name="afriwork",
                            job_url=job_url
                        ))
                except Exception as json_err:
                    logger.debug(f"Afriwork JSON hydration fallback triggered: {json_err}")

            # 2. Fallback to general HTML anchor element parsing
            if not jobs:
                cards = soup.select("a[href*='/jobs/'], div.job-card, article")
                seen_urls = set()
                
                for card in cards:
                    link = card if card.name == "a" else card.find("a")
                    if not link:
                        continue
                    
                    job_url = link.get("href", "")
                    title = link.get_text(strip=True)
                    
                    if not title or len(title) < 4 or "/jobs/" not in job_url:
                        continue
                    if job_url.rstrip("/") in ["/jobs", "https://afriworket.com/jobs"]:
                        continue

                    if not job_url.startswith("http"):
                        job_url = "https://afriworket.com" + job_url if job_url.startswith("/") else f"https://afriworket.com/{job_url}"

                    job_url = job_url.split("?")[0]

                    if job_url in seen_urls:
                        continue
                    seen_urls.add(job_url)

                    if search_term and search_term.lower() not in title.lower():
                        continue

                    jobs.append(JobPost(
                        title=title,
                        company="Afriwork Partner",
                        location=location or "Addis Ababa, Ethiopia",
                        site_name="afriwork",
                        job_url=job_url
                    ))
                    
                    if len(jobs) >= results_wanted:
                        break
        except Exception as e:
            logger.error(f"Afriwork scrape error: {e}")
        return jobs