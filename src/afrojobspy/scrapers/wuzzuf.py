import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class WuzzufScraper(BaseScraper):
    """Scraper for Wuzzuf (Egypt / North Africa)"""
    def __init__(self, proxies: Optional[List[str]] = None):
        super().__init__(proxies=proxies)
        self.base_url = "https://wuzzuf.net/search/jobs/?q=&a=hpsp"
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
            cards = soup.select("div.css-1gatmva, div.job-card, div[data-qa='job-card']")
            
            seen_urls = set()
            for card in cards:
                link = card.select_one("a.css-o171kl, h2.css-m604qf a, a[href*='/jobs/']")
                if not link:
                    link = card.find("a", href=True)
                if not link:
                    continue
                
                job_url = link.get("href", "")
                title = link.get_text(strip=True)
                
                if not job_url or not title or len(title) < 4:
                    continue
                if "/jobs/" not in job_url:
                    continue

                if not job_url.startswith("http"):
                    job_url = "https://wuzzuf.net" + job_url if job_url.startswith("/") else f"https://wuzzuf.net/{job_url}"

                job_url = job_url.split("?")[0]
                if job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                if search_term and search_term.lower() not in title.lower():
                    continue

                company = "Wuzzuf Employer"
                comp_elem = card.select_one("a.css-17s97ql, .company-name")
                if comp_elem:
                    c_text = comp_elem.get_text(strip=True)
                    if c_text and len(c_text) < 50:
                        company = c_text

                jobs.append(JobPost(
                    title=title,
                    company=company,
                    location=location or "Egypt",
                    site_name="wuzzuf",
                    job_url=job_url
                ))
                
                if len(jobs) >= results_wanted:
                    break
        except Exception as e:
            logger.error(f"Wuzzuf scrape error: {e}")
        return jobs