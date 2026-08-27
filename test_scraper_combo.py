import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

class UnifiedJobScraper(BaseScraper):
    """Unified Scraper for Regional Job Boards"""
    def __init__(self, proxies: Optional[List[str]] = None):
        super().__init__(proxies=proxies)
        self.base_url = "https://www.jobberman.com/jobs"
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        })

    def scrape(self, search_term: str = "", location: str = "", results_wanted: int = 5) -> List[JobPost]:
        jobs = []
        try:
            response = self.session.get(self.base_url, timeout=15)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch page, status code: {response.status_code}")
                return jobs
            
            soup = BeautifulSoup(response.text, "html.parser")
            cards = soup.select("div.job-card, div.search-result-row, article, div.flex.flex-col")
            
            seen_urls = set()
            for card in cards:
                link = card.find("a", href=True)
                if not link:
                    continue
                
                job_url = link.get("href", "")
                if not job_url or ("/listings/" not in job_url and "/job/" not in job_url):
                    continue
                
                title_elem = card.select_one("h3, h2, .job-title, a.text-loading")
                title = title_elem.get_text(strip=True) if title_elem else link.get_text(strip=True)
                
                if not title or len(title) < 4:
                    continue
                if any(skip in title.lower() for skip in ["home", "login", "register", "about", "contact", "privacy", "terms"]):
                    continue

                if not job_url.startswith("http"):
                    job_url = "https://www.jobberman.com" + job_url if job_url.startswith("/") else f"https://www.jobberman.com/{job_url}"

                job_url = job_url.split("?")[0]
                if job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                if search_term and search_term.lower() not in title.lower():
                    continue

                company = "Verified Employer"
                comp_elem = card.select_one(".text-gray-500, .job-company, span.text-sm")
                if comp_elem:
                    c_text = comp_elem.get_text(strip=True)
                    if c_text and len(c_text) < 50 and "ago" not in c_text.lower():
                        company = c_text

                jobs.append(JobPost(
                    title=title,
                    company=company,
                    location=location or "Regional",
                    site_name="jobberman",
                    job_url=job_url
                ))
                
                if len(jobs) >= results_wanted:
                    break
        except Exception as e:
            logger.error(f"Scrape execution error: {e}")
        return jobs

# ==========================================
# BUILT-IN TESTER EXECUTION BLOCK
# ==========================================
def run_tests():
    print("=" * 60)
    print("🧪 TESTING UNIFIED SCRAPER ISOLATION")
    print("=" * 60)
    
    scraper = UnifiedJobScraper()
    jobs = scraper.scrape(results_wanted=5)
    
    print(f"Total jobs extracted: {len(jobs)}")
    for index, j in enumerate(jobs, start=1):
        print(f"{index}. {j.title} | Company: {j.company}")
        print(f"   URL: {j.job_url}")

if __name__ == "__main__":
    run_tests()