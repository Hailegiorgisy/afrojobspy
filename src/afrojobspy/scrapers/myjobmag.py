import logging
from typing import List
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class MyJobMagScraper(BaseScraper):
    """
    Refined scraper implementation for MyJobMag.
    """
    def __init__(self, proxies=None):
        super().__init__(proxies=proxies)
        self.base_url = "https://www.myjobmag.com/search"

    def scrape(self, search_term: str, location: str, results_wanted: int) -> List[JobPost]:
        jobs: List[JobPost] = []
        page = 1
        
        while len(jobs) < results_wanted:
            params = {
                "q": search_term,
                "loc": location,
                "page": page
            }
            
            try:
                response = self.session.get(self.base_url, params=params, timeout=10)
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch MyJobMag page {page}. Status: {response.status_code}")
                    break
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Search across all block/list elements that could represent job entries
                candidates = soup.find_all(["li", "div", "article"], class_=True)
                found_valid = False
                
                for card in candidates:
                    if len(jobs) >= results_wanted:
                        break
                        
                    try:
                        # Find a valid job link within the container
                        a_tag = card.find("a", href=True)
                        if not a_tag:
                            continue
                            
                        job_url = a_tag["href"]
                        # Ensure the URL is actually a job posting link
                        if "/job/" not in job_url and "/jobs/" not in job_url:
                            continue
                            
                        if not job_url.startswith("http"):
                            job_url = "https://www.myjobmag.com" + job_url
                            
                        # Extract title (prefer headings, fallback to anchor text)
                        title_el = card.find(["h2", "h3", "h4"])
                        title = title_el.text.strip() if title_el else a_tag.text.strip()
                        
                        # Filter out navigation texts, blank spaces, or short snippets
                        if not title or len(title) < 4 or title.lower() in ["apply now", "view job", "read more"]:
                            continue
                            
                        # Extract company
                        comp_el = card.find(class_=["job-pnl-comp", "company", "employer", "mag-box-cmp"])
                        company = comp_el.text.strip() if comp_el else "N/A"
                        
                        # Extract location
                        loc_el = card.find(class_=["loc", "location", "job-loc"])
                        loc = loc_el.text.strip() if loc_el else (location or "Nigeria")
                        
                        job_id = job_url.split("/")[-1] or "unknown"

                        # Prevent duplicate entries on the same page loop
                        if any(j.job_url == job_url for j in jobs):
                            continue

                        job_post = JobPost(
                            id=job_id,
                            title=title,
                            company=company,
                            location=loc,
                            site_name="myjobmag",
                            job_url=job_url
                        )
                        jobs.append(job_post)
                        found_valid = True
                    except Exception:
                        continue
                
                if not found_valid and page > 1:
                    break
                    
                page += 1
            except Exception as net_err:
                logger.error(f"Network error during MyJobMag scrape: {net_err}")
                break
                
        return jobs