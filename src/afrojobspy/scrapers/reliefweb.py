import logging
from typing import List
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class ReliefWebScraper(BaseScraper):
    """
    Scraper implementation for ReliefWeb Jobs using direct HTML web scraping.
    """
    def __init__(self, proxies=None):
        super().__init__(proxies=proxies)
        self.base_url = "https://reliefweb.int/jobs"

    def scrape(self, search_term: str, location: str, results_wanted: int) -> List[JobPost]:
        jobs: List[JobPost] = []
        params = {
            "search": search_term
        }
        if location:
            params["country"] = location

        try:
            response = self.session.get(self.base_url, params=params, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch ReliefWeb HTML page. Status: {response.status_code}")
                return jobs
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find job cards or article entries on the page
            job_cards = soup.find_all("article") or soup.select(".card, .job-item, .teasers-item")
            
            for card in job_cards:
                if len(jobs) >= results_wanted:
                    break
                    
                try:
                    a_tag = card.find("a", href=True)
                    if not a_tag:
                        continue
                        hr = a_tag["href"]
                        
                    job_url = a_tag["href"]
                    if "/job/" not in job_url:
                        continue
                        
                    if not job_url.startswith("http"):
                        job_url = "https://reliefweb.int" + job_url
                        
                    title = a_tag.text.strip()
                    if not title or len(title) < 4:
                        continue
                        
                    comp_el = card.find(class_=["company", "source", "organization"])
                    company = comp_el.text.strip() if comp_el else "Humanitarian Organization"
                    
                    job_id = job_url.split("/")[-1] or "unknown"
                    
                    if any(j.job_url == job_url for j in jobs):
                        continue
                        
                    jobs.append(JobPost(
                        id=job_id,
                        title=title,
                        company=company,
                        location=location or "Africa / Global",
                        site_name="reliefweb",
                        job_url=job_url
                    ))
                except Exception:
                    continue
                    
        except Exception as e:
            logger.error(f"ReliefWeb HTML scrape error: {e}")
            
        return jobs