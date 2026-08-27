import logging
from typing import List
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class EthiojobsScraper(BaseScraper):
    """
    Scraper implementation for Ethiojobs (ethiojobs.net).
    """
    def __init__(self, proxies=None):
        super().__init__(proxies=proxies)
        self.base_url = "https://www.ethiojobs.net/jobs/"

    def scrape(self, search_term: str, location: str, results_wanted: int) -> List[JobPost]:
        jobs: List[JobPost] = []
        
        try:
            response = self.session.get(self.base_url, timeout=15)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch Ethiojobs page. Status: {response.status_code}")
                return jobs
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Target listing blocks or general job article nodes on Ethiojobs
            cards = soup.select(".job-ad-item, .listing-item, article, .content-row, .job-item")
            
            # Fallback if specific classes change: find elements containing job links
            if not cards:
                cards = soup.find_all("div", class_=lambda x: x and "job" in x.lower())

            for card in cards:
                if len(jobs) >= results_wanted:
                    break
                    
                try:
                    a_tag = card.find("a", href=True)
                    if not a_tag:
                        continue
                        
                    job_url = a_tag["href"]
                    if not ("/job/" in job_url or "/jobs/" in job_url or "display-job" in job_url):
                        # Try to find any internal link inside the card
                        internal_a = card.find("a", href=lambda h: h and ("/job/" in h or "detail" in h))
                        if internal_a:
                            a_tag = internal_a
                            job_url = a_tag["href"]
                        else:
                            continue

                    title = a_tag.text.strip()
                    if not title or len(title) < 4 or title.lower() in ["apply now", "view details", "read more", "apply"]:
                        # Try looking for a header tag inside the card
                        h_tag = card.find(["h2", "h3", "h4"])
                        if h_tag and h_tag.text.strip():
                            title = h_tag.text.strip()
                        else:
                            continue

                    if search_term and search_term.lower() not in title.lower():
                        card_text = card.get_text().lower()
                        if search_term.lower() not in card_text:
                            continue

                    if not job_url.startswith("http"):
                        job_url = "https://www.ethiojobs.net" + job_url
                        
                    comp_el = card.find(class_=["company", "employer", "organization", "company-name"])
                    company = comp_el.text.strip() if comp_el else "Ethiojobs Employer"
                    
                    job_id = job_url.split("/")[-1] or "unknown"
                    
                    if any(j.job_url == job_url for j in jobs):
                        continue
                        
                    jobs.append(JobPost(
                        id=job_id,
                        title=title,
                        company=company,
                        location=location or "Ethiopia",
                        site_name="ethiojobs",
                        job_url=job_url
                    ))
                except Exception:
                    continue
                    
        except Exception as e:
            logger.error(f"Ethiojobs scrape error: {e}")
            
        return jobs