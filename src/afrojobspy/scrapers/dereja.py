import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class DerejaScraper(BaseScraper):
    """Scraper for Dereja Portal"""
    def __init__(self, proxies: Optional[List[str]] = None):
        super().__init__(proxies=proxies)
        self.base_url = "https://dereja.com/jobs"
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
            cards = soup.select("div.job-item, article, div.card, a[href*='/job'], div.listings")
            
            seen_urls = set()
            for card in cards:
                link = card if card.name == "a" else card.find("a", href=True)
                if not link:
                    continue
                
                job_url = link.get("href", "")
                title = link.get_text(strip=True)
                
                if not job_url or not title or len(title) < 5:
                    continue
                if any(skip in title.lower() for skip in ["home", "login", "register", "about", "contact", "privacy", "terms"]):
                    continue

                if not job_url.startswith("http"):
                    job_url = "https://dereja.com" + job_url if job_url.startswith("/") else f"https://dereja.com/{job_url}"

                job_url = job_url.split("?")[0]
                if job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                if search_term and search_term.lower() not in title.lower():
                    continue

                jobs.append(JobPost(
                    title=title,
                    company="Dereja Partner",
                    location=location or "Ethiopia",
                    site_name="dereja",
                    job_url=job_url
                ))
                
                if len(jobs) >= results_wanted:
                    break
        except Exception as e:
            logger.error(f"Dereja scrape error: {e}")
        return jobs