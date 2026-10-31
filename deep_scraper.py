import logging
import json
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class DeepScraper(BaseScraper):
    """
    A dynamic, configuration-driven scraper that extracts data from 
    Next.js __NEXT_DATA__ payloads using a JSON schema configuration.
    """
    def __init__(self, config: Dict[str, Any], proxies: Optional[List[str]] = None):
        super().__init__(proxies=proxies)
        self.config = config
        self.base_url = config.get("base_url", "") + config.get("search_path", "")
        
        # Add headers to avoid bot detection and CDNs blocking requests
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })

    def _get_nested_value(self, data: Any, path: str) -> Any:
        """Navigates a nested dictionary or list using dot-notation path string."""
        parts = path.split(".")
        for part in parts:
            if isinstance(data, dict) and part in data:
                data = data[part]
            else:
                return None
        return data

    def scrape(self, search_term: str = "", location: str = "", results_wanted: int = 10) -> List[JobPost]:
        jobs: List[JobPost] = []
        
        params = {}
        if search_term:
            params["q"] = search_term
        if location:
            params["location"] = location

        try:
            response = self.session.get(self.base_url, params=params, timeout=15)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {self.config.get('name')} page. Status: {response.status_code}")
                return jobs
            
            soup = BeautifulSoup(response.text, "html.parser")
            tag = soup.find("script", id="__NEXT_DATA__")
            
            if not tag or not tag.string:
                logger.warning(f"{self.config.get('name')} __NEXT_DATA__ payload not found.")
                return jobs
                
            data = json.loads(tag.string)
            
            payload_path = self.config.get("payload_path", "")
            jobs_list = self._get_nested_value(data, payload_path)
            
            if not isinstance(jobs_list, list):
                logger.warning(f"Expected a list at payload path '{payload_path}', got {type(jobs_list)}.")
                return jobs
            
            title_key = self.config.get("title_key", "title")
            slug_key = self.config.get("slug_key", "slug")
            id_key = self.config.get("id_key", "id")
            company_key = self.config.get("company_key", "company")
            location_key = self.config.get("location_key", "location")
            description_key = self.config.get("description_key", "description")
            date_key = self.config.get("date_key", "date_published")
            domain = self.config.get("base_url", "")

            for item in jobs_list:
                if len(jobs) >= results_wanted:
                    break
                    
                title = str(item.get(title_key, "")).strip()
                if not title:
                    continue
                    
                slug = item.get(slug_key, "")
                job_id = str(item.get(id_key, ""))
                
                # Client-side filtering fallback if search query parameters are ignored by the server
                if search_term and search_term.lower() not in title.lower():
                    desc_text = str(item.get(description_key, ""))
                    if search_term.lower() not in desc_text.lower():
                        continue

                job_url = f"{domain}/job/{slug}" if slug else domain
                
                # Handle company field safely whether it's a dict or a string
                company_obj = item.get(company_key, {})
                company_name = "Employer"
                if isinstance(company_obj, dict):
                    company_name = company_obj.get("name") or company_obj.get("company_name") or "Employer"
                elif isinstance(company_obj, str):
                    company_name = company_obj

                description = item.get(description_key, "")
                date_posted = item.get(date_key)
                job_loc = item.get(location_key) or location or self.config.get("region", "Ethiopia")

                jobs.append(JobPost(
                    id=job_id,
                    title=title,
                    company=company_name,
                    location=str(job_loc),
                    site_name=self.config.get("name", "custom").lower(),
                    job_url=job_url,
                    description=str(description),
                    date_posted=str(date_posted) if date_posted else None
                ))
                
        except Exception as e:
            logger.error(f"DeepScrape error for {self.config.get('name')}: {e}")
            
        return jobs