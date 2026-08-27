import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class GeezJobsScraper(BaseScraper):
    """Scraper for GeezJobs Ethiopia"""
    def __init__(self, proxies: Optional[List[str]] = None):
        super().__init__(proxies=proxies)
        self.base_url = "https://geezjobs.com/"

    def scrape(self, search_term: str = "", location: str = "", results_wanted: int = 10) -> List[JobPost]:
        jobs = []
        try:
            response = self.session.get(self.base_url, timeout=15)
            if response.status_code != 200:
                return jobs
            
            soup = BeautifulSoup(response.text, "html.parser")
            # Look specifically for job title links or cards
            cards = soup.select("div.job-card, div.vacancy-item, a.job-link, .featured-vacancy a, h3 a, h4 a")
            
            seen_urls = set()
            for card in cards:
                # Find the anchor tag
                link_elem = card if card.name == "a" else card.find("a")
                if not link_elem:
                    continue
                
                title = link_elem.get_text(strip=True)
                job_url = link_elem.get("href", "")
                
                # Filter out garbage text, headers, and UI elements
                if not title or len(title) < 5 or title.lower() in ["jobs", "post a job", "login", "register", "view all vacancies"]:
                    continue
                if not job_url or "job" not in job_url.lower():
                    continue

                if job_url and not job_url.startswith("http"):
                    job_url = "https://geezjobs.com" + job_url

                if job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                if search_term and search_term.lower() not in title.lower():
                    continue

                jobs.append(JobPost(
                    title=title,
                    company="GeezJobs Employer",
                    location=location or "Addis Ababa, Ethiopia",
                    site_name="geezjobs",
                    job_url=job_url
                ))
                
                if len(jobs) >= results_wanted:
                    break
        except Exception as e:
            logger.error(f"GeezJobs scrape error: {e}")
        return jobs