%%writefile src/afrojobspy/scrapers/ethiojobs.py
import logging
import json
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class EthiojobsScraper(BaseScraper):
    """
    Robust scraper implementation for Ethiojobs (ethiojobs.net) 
    extracting data directly from Next.js server-side JSON payloads.
    """
    def __init__(self, proxies: Optional[List[str]] = None):
        super().__init__(proxies=proxies)
        self.base_url = "https://ethiojobs.net/jobs"

    def scrape(self, search_term: str = "", location: str = "", results_wanted: int = 10) -> List[JobPost]:
        jobs: List[JobPost] = []
        
        try:
            response = self.session.get(self.base_url, timeout=15)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch Ethiojobs page. Status: {response.status_code}")
                return jobs
            
            soup = BeautifulSoup(response.text, "html.parser")
            tag = soup.find("script", id="__NEXT_DATA__")
            
            if not tag or not tag.string:
                logger.warning("Ethiojobs __NEXT_DATA__ payload not found.")
                return jobs
                
            data = json.loads(tag.string)
            jobs_payload = data.get("props", {}).get("pageProps", {}).get("jobs", {})
            jobs_list = jobs_payload.get("data", [])
            
            for item in jobs_list:
                if len(jobs) >= results_wanted:
                    break
                    
                title = item.get("title", "").strip()
                slug = item.get("slug", "")
                job_id = str(item.get("id", ""))
                
                if not title:
                    continue
                    
                # Filter client-side if search_term is supplied
                if search_term and search_term.lower() not in title.lower():
                    desc = item.get("description", "")
                    if search_term.lower() not in desc.lower():
                        continue
                        
                # Construct clean job detail link
                job_url = f"https://ethiojobs.net/job/{slug}" if slug else self.base_url
                
                # Extract company name safely
                company_obj = item.get("company", {})
                company_name = "Ethiojobs Employer"
                if isinstance(company_obj, dict):
                    company_name = company_obj.get("name") or company_obj.get("company_name") or "Ethiojobs Employer"
                elif isinstance(company_obj, str):
                    company_name = company_obj

                description = item.get("description", "")
                date_posted = item.get("date_published")

                jobs.append(JobPost(
                    id=job_id,
                    title=title,
                    company=company_name,
                    location=location or "Ethiopia",
                    site_name="ethiojobs",
                    job_url=job_url,
                    description=description,
                    date_posted=date_posted
                ))
                
        except Exception as e:
            logger.error(f"Ethiojobs scrape error: {e}")
            
        return jobs