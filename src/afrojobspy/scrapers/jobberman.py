import logging
from typing import List
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class JobbermanScraper(BaseScraper):
    """
    Scraper implementation for Jobberman.
    """
    def __init__(self, proxies=None):
        super().__init__(proxies=proxies)
        self.base_url = "https://www.jobberman.com/jobs"

    def scrape(self, search_term: str, location: str, results_wanted: int) -> List[JobPost]:
        jobs: List[JobPost] = []
        page = 1
        
        while len(jobs) < results_wanted:
            params = {
                "q": search_term,
                "location": location,
                "page": page
            }
            
            try:
                response = self.session.get(self.base_url, params=params, timeout=10)
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch Jobberman page {page}. Status: {response.status_code}")
                    break
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Jobberman search cards typically use article tags or specific card classes
                job_cards = soup.find_all("div", class_="panel-card") or soup.find_all("article")
                if not job_cards:
                    # Fallback structural search
                    job_cards = soup.select(".job-listing, .search-result, div[data-cy='listing-card']")
                
                if not job_cards:
                    # Generic anchor fallback
                    links = soup.find_all("a", href=True)
                    found_any = False
                    for a in links:
                        href = a["href"]
                        if "/listings/" in href and len(a.text.strip()) > 5:
                            if len(jobs) >= results_wanted:
                                break
                            job_url = href if href.startswith("http") else "https://www.jobberman.com" + href
                            job_id = job_url.split("/")[-1]
                            
                            if not any(j.job_url == job_url for j in jobs):
                                jobs.append(JobPost(
                                    id=job_id,
                                    title=a.text.strip(),
                                    company="N/A",
                                    location=location or "Nigeria",
                                    site_name="jobberman",
                                    job_url=job_url
                                ))
                                found_any = True
                    if not found_any or page > 2:
                        break
                    page += 1
                    continue

                for card in job_cards:
                    if len(jobs) >= results_wanted:
                        break
                        
                    try:
                        a_tag = card.find("a", href=True)
                        if not a_tag:
                            continue
                            
                        job_url = a_tag["href"]
                        if "/listings/" not in job_url and "/job" not in job_url:
                            continue
                            
                        if not job_url.startswith("http"):
                            job_url = "https://www.jobberman.com" + job_url
                            
                        title_el = card.find(["h2", "h3", "p"])
                        title = title_el.text.strip() if title_el else a_tag.text.strip()
                        
                        if not title or len(title) < 4:
                            continue
                            
                        comp_el = card.find(class_=["text-gray-500", "company-name", "text-muted"])
                        company = comp_el.text.strip() if comp_el else "N/A"
                        
                        loc_el = card.find(class_=["location", "text-gray-400"])
                        loc = loc_el.text.strip() if loc_el else (location or "Nigeria")
                        
                        job_id = job_url.split("/")[-1] or "unknown"

                        if any(j.job_url == job_url for j in jobs):
                            continue

                        jobs.append(JobPost(
                            id=job_id,
                            title=title,
                            company=company,
                            location=loc,
                            site_name="jobberman",
                            job_url=job_url
                        ))
                    except Exception:
                        continue
                
                page += 1
            except Exception as net_err:
                logger.error(f"Network error during Jobberman scrape: {net_err}")
                break
                
        return jobs